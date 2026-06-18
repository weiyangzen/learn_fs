# sources/distributed-fs/ceph-client/sound/isa/sb/sb8_midi.c

## Purpose
This file implements the raw MIDI interface for 8-bit Sound Blaster DSP MIDI mode. It supports input, output, and duplex UART behavior on DSP version 2.0 and later, using timer-driven polling for output.

## Important APIs, Types, and Functions
The exported functions are `snd_sb8dsp_midi_interrupt()` and `snd_sb8dsp_midi()`. RawMIDI callbacks are `snd_sb8dsp_midi_input_open/close/trigger` and output equivalents. `snd_sb8dsp_midi_output_write()` drains ALSA transmit bytes to the DSP. `snd_sb8dsp_midi_output_timer()` keeps output moving while triggered.

## Control Flow
Opening input or output checks `chip->open` under `open_lock`. DSP 2.0+ allows the opposite MIDI stream and its trigger flags to coexist; older DSPs do not. On first MIDI open, the DSP is reset and DSP 2.0+ is put into IRQ UART mode. Input trigger enables or disables input interrupt mode, issuing `SB_DSP_MIDI_INPUT_IRQ` toggles on old hardware. Output trigger starts a one-jiffy timer and immediately attempts to write. Output writing peeks one byte at a time, waits briefly for FIFO availability on DSP 2.0+, writes either directly or through `SB_DSP_MIDI_OUTPUT`, acknowledges transmitted bytes, and stops the timer when no data remains.

Interrupt handling drains up to 64 bytes while data is available, acknowledges orphan interrupts when no rawmidi exists, and calls `snd_rawmidi_receive()` only when the input trigger is active.

## State and Persistence
State is in `struct snd_sb`: `open` bits, MIDI substream pointers, `midi_timer`, and `midi_input_lock`. No persistent storage exists.

## Dependencies and Integration Points
This file depends on ALSA rawmidi APIs, SB IO-port macros and DSP command helpers, and the card-level interrupt dispatcher in `sb8.c`.

## Risks and Edge Cases
Timer and interrupt paths share open and virtual stream state, so lock pairing matters. Output uses small hard busy-waits and a periodic timer rather than hardware transmit interrupts. Closing output deletes the timer synchronously, which is important for avoiding use-after-close. `snd_sb8dsp_midi_interrupt()` returns `IRQ_HANDLED` even when it drains no triggered data as long as a rawmidi exists.

## Test Signals
Open/close both MIDI directions on DSP 2.0+ for duplex, verify old hardware rejects conflicting opens, confirm output timer stops after transmit buffer drains, confirm input data is ignored until trigger is enabled, and verify MIDI use while PCM is closed because `sb8.c` routes the shared IRQ by `SB_OPEN_PCM`.
