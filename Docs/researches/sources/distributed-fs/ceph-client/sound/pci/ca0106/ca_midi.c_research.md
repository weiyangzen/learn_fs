# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.c

## Purpose

`ca_midi.c` implements the raw MIDI UART glue used by the Creative CA0106 ALSA driver. It is not a standalone PCI driver; instead it exposes `ca_midi_init()` and a `struct snd_ca_midi` callback contract supplied by the CA0106 core. The file adapts hardware-specific read/write, interrupt-enable, interrupt-disable, and device-lookup callbacks into ALSA `snd_rawmidi` input/output substreams.

## Important APIs, Types, and Functions

- `ca_midi_init(void *dev_id, struct snd_ca_midi *midi, int device, char *name)` creates the ALSA rawmidi device, initializes locks, assigns rawmidi ops, and stores `midi->interrupt = ca_midi_interrupt`.
- `ca_midi_interrupt(struct snd_ca_midi *midi, unsigned int status)` is called by the parent CA0106 interrupt handler. It drains or receives input bytes and transmits pending output bytes when the relevant interrupt bits are set.
- `ca_midi_input_open()` / `ca_midi_output_open()` mark input or output mode, bind substreams, and issue reset plus UART-enter commands when the first side opens.
- `ca_midi_input_close()` / `ca_midi_output_close()` disable the relevant interrupt, clear mode/substream state, and reset the UART when the last side closes.
- `ca_midi_input_trigger()` and `ca_midi_output_trigger()` gate RX/TX interrupts. Output trigger also primes up to four bytes before enabling TX interrupts.
- `ca_midi_cmd()` writes an MPU-401-style command and optionally waits for an ACK byte.
- `ca_midi_clear_rx()` drains pending receive bytes with a bounded timeout.

The file relies on the data type declared in `ca_midi.h`: `struct snd_ca_midi`, which contains hardware callback pointers, interrupt masks, ACK/reset/enter-UART command bytes, lock fields, rawmidi pointers, and mode flags.

## Control Flow

Initialization starts in `ca_midi_init()`: the parent has already filled the hardware-specific callbacks and constants, then this function creates a duplex rawmidi instance with one input and one output stream. ALSA later calls the rawmidi open/close/trigger handlers. The first input or output open resets the UART and sends the enter-UART command. If the second half opens while the first is active, it only updates state and avoids resetting an already active MIDI session.

Runtime input flow is interrupt-driven. The parent interrupt handler passes hardware status into `ca_midi_interrupt()`. Under `input_lock`, the code checks the RX interrupt bit and hardware availability flag. If ALSA input mode is not enabled, it drains the hardware FIFO; otherwise it reads one byte and passes it to `snd_rawmidi_receive()` when an input substream exists.

Runtime output flow is also interrupt-driven. `ca_midi_output_trigger(..., up=1)` sends a small burst synchronously while the output register is ready, then enables TX interrupts. Later, `ca_midi_interrupt()` checks output readiness, pulls one byte from ALSA through `snd_rawmidi_transmit()`, writes it to hardware, or disables TX interrupts when no data remains.

## State and Persistence Behavior

The persistent state is in the caller-owned `struct snd_ca_midi`. Important fields include `midi_mode`, `substream_input`, `substream_output`, `rmidi`, callback pointers, `dev_id`, and lock instances. No state is written to disk. Hardware state is transient register state controlled through the callback methods. Cleanup via `ca_rmidi_free()` nulls callback pointers and rawmidi references so stale callbacks are less likely after device teardown.

Locking is split by purpose: `open_lock` protects open/close mode transitions, `input_lock` protects RX command/read paths, and `output_lock` protects TX paths. Command ACK polling uses `spinlock_irqsave` on `input_lock`, because command response bytes share the receive path.

## Dependencies and Integration Points

The file depends on Linux spinlock helpers, ALSA core/rawmidi, and the local `ca_midi.h` contract. It expects the CA0106 parent driver to provide `read`, `write`, `interrupt_enable`, `interrupt_disable`, `get_dev_id_card`, and `get_dev_id_port`, plus hardware bit definitions such as `ipr_rx`, `ipr_tx`, `input_avail`, and `output_ready`. ALSA integration is through `snd_rawmidi_new()`, `snd_rawmidi_set_ops()`, `snd_rawmidi_receive()`, and `snd_rawmidi_transmit()`.

## Risks and Edge Cases

- `ca_midi_cmd()` polls for ACK while reading from the MIDI receive path. Unexpected input data during command setup could be consumed as part of ACK handling.
- `ca_midi_interrupt()` reads at most one input byte per interrupt; correctness depends on the parent interrupt cadence or hardware reassertion.
- If `rmidi` is NULL in the interrupt path, both RX and TX interrupts are disabled, which is appropriate for teardown but could hide earlier initialization ordering mistakes.
- Open/close paths return early from inside guarded regions when the opposite direction is still open. This preserves the active UART but makes lock-scope clarity important.
- Debug-only timeout logging in `ca_midi_clear_rx()` helps detect a stuck input-ready status bit.

## Test Signals

Useful validation includes loading the CA0106 driver with MIDI hardware present, confirming a duplex rawmidi device is registered, opening input and output concurrently, sending and receiving MIDI bytes, and checking that TX interrupts stop when output buffers drain. Kernel logs should be checked for `ca_midi_cmd` ACK failures or clear-RX timeouts. Race-sensitive testing should exercise open/close while traffic is active.
