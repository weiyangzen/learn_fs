# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-pcm.c

## Purpose

This file exposes OXFW devices as ALSA PCM streams and converts discovered AV/C stream formats into ALSA hardware constraints.

## Important APIs, types, and functions

`snd_oxfw_create_pcm()` creates playback and optional capture streams. `hw_rule_rate()` and `hw_rule_channels()` constrain valid rate/channel pairs from stream-format arrays. `init_hw_params()` selects AM824 sample format bits and adds AM824 constraints. Capture maps to `tx_stream`; playback maps to `rx_stream`.

## Control flow

Open takes the stream lock, initializes runtime constraints, and if streams are already reserved, limits the new substream to the current formation and domain period/buffer size. `pcm_capture_hw_params()` and `pcm_playback_hw_params()` reserve the duplex stream with selected rate/channels and increment `substreams_count`. Prepare starts duplex streaming and prepares the corresponding AMDTP stream. Trigger attaches/detaches substreams; pointer/ack delegate to the domain.

## State and persistence behavior

The file updates ALSA runtime constraints, `substreams_count`, and AM824 PCM trigger state. Stream formats themselves were discovered earlier and stored in `struct snd_oxfw`.

## Dependencies and integration points

It depends on `oxfw-stream.c` formation parsing/reservation, AM824 helpers, and the hwdep lock model. It is sensitive to `has_output`, because some devices only support playback to the device.

## Risks and test signals

Risks include invalid interval lists, no format entries leaving min/max at sentinel values, and capture availability confusion when `has_output` is false. Tests should cover all advertised formations, simultaneous PCM directions, rate/channel changes, MIDI coexistence, and devices with playback-only or assumed formats.
