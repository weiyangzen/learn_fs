# sources/distributed-fs/ceph-client/sound/core/seq/seq_midi.c

## Purpose
`seq_midi.c` implements the generic MIDI synth sequencer driver that exposes rawmidi devices as ALSA sequencer ports. It creates sequencer kernel clients for rawmidi cards, converts raw MIDI byte streams into sequencer events on input, and converts sequencer events back into MIDI bytes on output.

## Important APIs, Types, and Functions
- `struct seq_midisynth` stores one sequencer port's rawmidi device, input/output files, parser, client id, and port id.
- `struct seq_midisynth_client` groups per-card sequencer clients and their per-device ports.
- `snd_midi_input_event()` reads bytes from a rawmidi input substream and dispatches encoded sequencer events to subscribers.
- `event_process_midi()` receives sequencer events and writes decoded MIDI bytes to the rawmidi output stream, with direct sysex streaming through `snd_seq_dump_var_event()`.
- Subscription/use callbacks open and close rawmidi input/output streams.
- `snd_seq_midisynth_probe()` and `snd_seq_midisynth_remove()` implement the `snd_seq_driver` binding for `SNDRV_SEQ_DEV_ID_MIDISYNTH`.

## Control Flow
Probe inspects rawmidi input and output subdevice counts, creates or reuses a per-card kernel sequencer client, allocates one `seq_midisynth` per port, initializes a `snd_midi_event` parser, and creates sequencer ports with callback tables. Input subscriptions call `midisynth_subscribe()`, which opens rawmidi input, configures buffer parameters, installs `snd_midi_input_event()` as the rawmidi runtime callback, and primes the stream. Output use calls `midisynth_use()`, which opens output and sets buffer/no-active-sensing parameters.

Incoming rawmidi bytes are parsed one byte at a time. A complete MIDI event is dispatched to `SNDRV_SEQ_ADDRESS_SUBSCRIBERS`. Outgoing sequencer events are decoded to MIDI bytes or streamed as sysex, then written through `snd_rawmidi_kernel_write()`.

## State and Persistence
State is per card in the static `synths[]` table and protected by `register_mutex`. Per-port state persists while the sequencer device is bound. Runtime input/output file handles exist only while the port has active subscriptions or users. No persistent storage is used.

## Dependencies and Integration Points
Depends on rawmidi, sequencer kernel client control, `seq_device` bus registration, and MIDI event parser APIs from `seq_midi_event.c`. It integrates with port callbacks from `seq_ports.c` and with rawmidi device-specific `get_port_info()` overrides.

## Risks
Buffer sizing is module-param controlled and can trigger output overrun errors. Probe has several partial-allocation unwind paths, so leaks or stale sequencer clients are the main lifecycle risk. Input and output share one parser per `seq_midisynth`, so concurrent stream usage must respect rawmidi/port callback serialization assumptions.

## Test Signals
Test by registering rawmidi devices with input-only, output-only, duplex, and multiple subdevices; subscribing/unsubscribing sequencer clients; sending sysex and running-status MIDI; and verifying remove tears down ports and the kernel client when the last device is gone.
