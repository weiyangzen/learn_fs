# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumpu401.c

## Purpose

This file implements MPU-401 UART raw-MIDI support for the main EMU10K1/Audigy driver. It creates one MIDI port on EMU10K1 cards and two MIDI ports on Audigy cards, bridges ALSA rawmidi open/close/trigger operations to the hardware UART, and dispatches MIDI receive/transmit-ready interrupts.

## Important APIs, types, and functions

The public entry points are `snd_emu10k1_midi` and `snd_emu10k1_audigy_midi`. Both use `emu10k1_midi_init` to allocate an ALSA rawmidi device, set input/output ops, initialize `open_lock`, `input_lock`, and `output_lock`, and attach `struct snd_emu10k1_midi` as private data. `snd_emu10k1_midi` configures the classic EMU10K1 port at `MUDATA`; `snd_emu10k1_audigy_midi` configures `A_MUDATA1` and `A_MUDATA2` with separate Audigy interrupt bits and callbacks.

Low-level helpers `mpu401_read` and `mpu401_write` abstract the hardware difference: Audigy accesses MIDI registers through `snd_emu10k1_ptr_read/write`, while non-Audigy cards use direct I/O ports relative to `emu->port`. Macros define data/status/command access and the standard status bits (`0x80` input empty, `0x40` output busy). `snd_emu10k1_midi_cmd` sends `MPU401_RESET` or `MPU401_ENTER_UART` and optionally waits for `MPU401_ACK`.

ALSA rawmidi callbacks are `snd_emu10k1_midi_input_open`, `snd_emu10k1_midi_output_open`, `snd_emu10k1_midi_input_close`, `snd_emu10k1_midi_output_close`, `snd_emu10k1_midi_input_trigger`, and `snd_emu10k1_midi_output_trigger`. Interrupt callbacks are `snd_emu10k1_midi_interrupt`, `snd_emu10k1_midi_interrupt2`, and shared `do_emu10k1_midi_interrupt`.

## Control Flow

Opening either input or output records the substream and sets the matching mode bit under `open_lock`. If the opposite direction is already open, the port is already in UART mode and the callback returns. Otherwise the hardware is reset and put into UART mode, with ACK checking. Closing a direction disables the matching interrupt, clears the mode bit and substream pointer, and resets the hardware only when both directions are closed.

Input trigger simply enables or disables the receive interrupt bit. Output trigger opportunistically writes up to four bytes immediately while the UART reports output-ready, then enables transmit-empty interrupts if more data may be pending. If the ALSA transmit queue is empty or the output mode is no longer active, it returns without enabling TX interrupts. The interrupt handler receives a card-wide status word from the main IRQ code. For RX, it reads one byte when the RX bit is set and input is available, clearing stale bytes if the input side is not active. For TX, it writes one queued byte when the TX bit is set and the hardware is ready, disabling TX interrupts when no byte is available.

## State and Persistence Behavior

All state is runtime-only in `struct snd_emu10k1_midi`: rawmidi pointer, current input/output substreams, mode bits, locks, interrupt masks, hardware port offsets, and dispatch callback. `snd_emu10k1_midi_free` clears `interrupt` and `rmidi` so late IRQs disable MIDI interrupts instead of dereferencing a freed rawmidi object. Hardware UART mode is reset on first open and final close; queued MIDI bytes live in ALSA rawmidi buffers, not in this file.

## Dependencies and Integration Points

The code depends on ALSA rawmidi APIs, EMU10K1 register helpers, card interrupt enable/disable helpers, and the main device struct from `include/sound/emu10k1.h`. The main IRQ handler in the core driver calls the function pointer stored in each MIDI struct when MIDI bits appear in the interrupt status. User-space integration is the standard ALSA rawmidi device interface with duplex capability.

## Risks

The command path busy-waits for ACKs while holding `input_lock`, and failure paths log hardware status/data reads after the lock is released. Interrupt processing reads or writes at most one byte per IRQ, so high traffic depends on timely repeated TX/RX interrupts. The code uses separate open/input/output locks; changes must preserve ordering to avoid races among trigger, close, and interrupt paths. Audigy and non-Audigy register access are intentionally different; using the wrong port offset or interrupt mask would silently break one generation. The free callback only nulls pointers, so main-driver teardown must also ensure interrupts are disabled or synchronized.

## Test Signals

Useful tests include rawmidi device creation on EMU10K1 and two-device creation on Audigy, successful reset/UART ACK on first open, duplex open without redundant reset, final close reset, MIDI receive delivery through `snd_rawmidi_receive`, transmit drain through immediate writes plus TX interrupts, interrupt disabling when queues empty or rawmidi is freed, behavior when no hardware ACK arrives, and regression coverage for Audigy pointer-register access versus legacy I/O-port access.
