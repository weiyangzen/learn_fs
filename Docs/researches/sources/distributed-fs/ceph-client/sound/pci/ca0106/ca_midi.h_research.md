# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca_midi.h

## Purpose

`ca_midi.h` declares the CA0106 MIDI adapter contract used by `ca_midi.c` and the parent CA0106 hardware driver. It maps CA0106 MIDI mode constants to MPU-401 mode bits, defines the per-MIDI-port state structure, and exports `ca_midi_init()`.

## Important APIs, Types, and Fields

- `CA_MIDI_MODE_INPUT` and `CA_MIDI_MODE_OUTPUT` alias `MPU401_MODE_INPUT` and `MPU401_MODE_OUTPUT`, keeping raw MIDI mode semantics compatible with ALSA MPU-401 conventions.
- `struct snd_ca_midi` is the central integration type. It contains:
  - ALSA rawmidi objects: `rmidi`, `substream_input`, and `substream_output`.
  - Parent device identity: `void *dev_id`, `channel`, and `port`.
  - Synchronization: `input_lock`, `output_lock`, and `open_lock`.
  - Runtime mode: `midi_mode`.
  - Hardware constants: interrupt enable masks, interrupt pending bits, status masks, and MPU command bytes (`ack`, `reset`, `enter_uart`).
  - Callback hooks: parent interrupt callback, interrupt enable/disable functions, byte read/write functions, and helpers to derive `struct snd_card *` and port number from `dev_id`.
- `ca_midi_init(void *card, struct snd_ca_midi *midi, int device, char *name)` is the exported initializer implemented in `ca_midi.c`.

## Control Flow and Integration

The parent CA0106 driver allocates or embeds `struct snd_ca_midi`, fills the hardware-specific masks and callbacks, then calls `ca_midi_init()`. After initialization, ALSA owns rawmidi stream dispatch while the CA0106 parent owns PCI interrupt dispatch and calls `midi->interrupt()` with hardware interrupt status.

The read/write callbacks are indexed by `idx`: `0` for MIDI data and `1` for command/status in `ca_midi.c`'s macros. That index convention is an implicit API between this header's callback signatures and the implementation.

## State and Persistence Behavior

The structure is persistent for the lifetime of the sound card and is mutable at runtime. It stores substream pointers, mode flags, and function pointers. There is no disk persistence. Hardware state is represented by callback-accessed registers rather than cached directly, except for mode and substream state.

## Dependencies

The header includes Linux spinlocks, ALSA rawmidi, and ALSA MPU-401 definitions. It intentionally avoids including CA0106 core headers by using `void *dev_id` and callback accessors, keeping the MIDI helper generic across parent implementations that satisfy the same contract.

## Risks and Edge Cases

- The header does not validate callback initialization. `ca_midi_init()` assumes `get_dev_id_card()` is already valid before it assigns `midi->dev_id = dev_id`, so callers must initialize both `midi->dev_id` and callback pointers consistently before calling.
- Status-mask semantics are inverted by `ca_midi.c`: input/output availability macros test for cleared bits after applying `input_avail` or `output_ready`. Parent-provided masks must match that convention.
- The `char *name` parameter is mutable in the prototype even though the initializer only copies it; a `const char *` would describe usage more accurately but would change the exported signature.

## Test Signals

Compile coverage should verify all parent users populate the struct fields expected by `ca_midi.c`. Runtime validation comes from successful rawmidi registration, stable interrupt handling, and absence of NULL callback crashes when probing or removing CA0106 devices.
