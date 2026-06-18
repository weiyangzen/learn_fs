# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-pcm.c

## Purpose

This file exposes MOTU FireWire devices as one ALSA PCM device with one playback and one capture substream. It translates model-specific packet-format caches into PCM hardware constraints, coordinates duplex stream reservation/start/stop, and binds ALSA callbacks to the MOTU AMDTP streams.

## Important APIs, types, and functions

`snd_motu_create_pcm_devices()` creates the ALSA PCM, marks it nonatomic, installs capture/playback ops, and uses VMALLOC buffers. `motu_rate_constraint()` and `motu_channels_constraint()` keep rate/channel choices consistent with `snd_motu_packet_format.pcm_chunks`. `init_hw_info()` selects `tx_stream` for capture and `rx_stream` for playback, configures S32 samples, adds MOTU-specific AMDTP constraints, and uses cached packet formats.

## Control flow

`pcm_open()` first takes the device stream lock, refreshes packet formats, initializes runtime hardware limits, reads the clock source, and restricts rate/period/buffer to current values when externally clocked or already reserved. `pcm_hw_params()` reserves the duplex domain and increments `substreams_counter`; `pcm_hw_free()` decrements it and stops/free resources when the last substream leaves. Prepare starts duplex streaming, trigger only attaches or detaches the ALSA substream, and pointer/ack delegate to the shared AMDTP domain.

## State and persistence behavior

The file mutates `substreams_counter`, runtime hardware constraints, and AMDTP PCM trigger state. Long-lived state is in `struct snd_motu`, especially cached formats and domain period/buffer sizing.

## Dependencies and integration points

It depends on `motu.h`, protocol dispatchers, `motu-stream.c`, and `amdtp-motu` helpers. ALSA PCM state is synchronized with the hwdep lock notifications produced by `snd_motu_stream_lock_try/release()`.

## Risks and test signals

The main risks are incorrect channel/rate constraints when optical interface state changes, counter imbalance on error paths, and deadlocks between ALSA open/close and stream mutex paths. Test signals include opening capture/playback in both orders, externally clocked operation, simultaneous duplex use, period/buffer locking, xrun recovery, and changing sample rates between opens.
