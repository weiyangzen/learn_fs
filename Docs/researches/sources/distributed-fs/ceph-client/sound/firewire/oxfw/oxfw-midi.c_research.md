# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-midi.c

## Purpose

This file creates standard ALSA RawMIDI ports for OXFW devices whose AM824 stream formats advertise MIDI channels. MIDI bytes are transported inside the same duplex AMDTP streams as audio.

## Important APIs, types, and functions

`snd_oxfw_create_midi()` allocates a RawMIDI device according to `midi_input_ports` and `midi_output_ports`. Open callbacks reserve and start duplex streaming with current stream parameters. Trigger callbacks call `amdtp_am824_midi_trigger()` on the transmit or receive stream with the substream number.

## Control flow

Capture/playback open first take the stream lock, reserve duplex resources at current rate/format, increment `substreams_count`, and start the domain. Close decrements the count, stops the domain if this was the last user, and releases the stream lock. Trigger just attaches or detaches the RawMIDI substream under the driver spinlock.

## State and persistence behavior

This file mutates `substreams_count`, stream lock state, and AM824 MIDI substream pointers. RawMIDI port names persist for the ALSA card lifetime.

## Dependencies and integration points

It depends on format discovery in `oxfw-stream.c`, AM824 MIDI helper routines, and ALSA RawMIDI core. It shares stream reservation with PCM users, so counters and lock semantics must match `oxfw-pcm.c`.

## Risks and test signals

Risks include counter imbalance when start fails, MIDI-only opens forcing audio resources, and mismatched port counts from malformed stream formats. Test signals include MIDI-only capture/playback, duplex MIDI plus PCM, trigger start/stop without close, and disconnect/bus reset during active MIDI.
