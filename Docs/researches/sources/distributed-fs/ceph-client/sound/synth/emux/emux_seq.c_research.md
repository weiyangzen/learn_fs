# sources/distributed-fs/ceph-client/sound/synth/emux/emux_seq.c

## Purpose
This file implements the ALSA sequencer and virtual-MIDI interface for the EMUX synth. It creates kernel sequencer clients and ports, processes MIDI events through ALSA MIDI emulation callbacks, manages port reset/use counts, and attaches optional virtual raw MIDI devices.

## Important APIs, types, and functions
`emux_ops` maps MIDI note/control/NRPN/SYSEX callbacks to EMUX synth functions. `snd_emux_init_seq` creates the kernel client and configured MIDI ports. `snd_emux_create_port` allocates an EMUX port and channel set, optionally creates raw effect tables, and attaches a sequencer port. `snd_emux_reset_port`, `snd_emux_event_input`, `snd_emux_inc_count`, `snd_emux_dec_count`, `snd_emux_init_virmidi`, and `snd_emux_delete_virmidi` form the public control surface.

## Control flow
Initialization creates a kernel sequencer client named after the device, clamps `num_ports` to valid limits, builds callbacks, and attaches one 16-channel port per configured port. Each non-OSS port is writable/subscribable and advertises MIDI GM/GS/XG hardware synth types. On first subscription, `snd_emux_use` resets the port and increments hardware/card module refs; on unuse it silences the port and decrements refs. Incoming sequencer events are passed to `snd_midi_process_event`, which invokes `emux_ops`. Virmidi initialization creates rawmidi devices and points them at sequencer ports.

## State and persistence behavior
State persists in `emu->client`, `emu->ports`, `emu->portptrs`, `emu->used`, port channel sets, per-port controls, drum flags, optional effect tables, and virtual rawmidi pointers. No disk persistence exists. When usage count drops to zero, all voices are terminated.

## Dependencies and integration points
This file integrates ALSA sequencer kernel clients, MIDI event parsing, virmidi, module reference counting, EMUX synth voice callbacks, optional raw effects, and OSS-created ports.

## Risks and edge cases
`snd_emux_create_port` does not free the allocated port if `snd_seq_event_port_attach` fails and returns a negative port id. Registration callers do not always check `snd_emux_init_seq` failures. Module reference handling must remain balanced across use/unuse and OSS open/close. Virmidi port indexing assumes `midi_ports` does not exceed created sequencer ports.

## Test signals
Test sequencer client creation, port counts and caps, subscription use/unuse, MIDI note/control routing, port reset drum flags, module ref behavior, virmidi creation/deletion, failure injection for port attach and rawmidi registration, and teardown terminating active voices.
