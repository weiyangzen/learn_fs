# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam-pcm.c

## Purpose

This file exposes TASCAM FireWire audio as an ALSA duplex PCM device with fixed channel counts derived from model capabilities.

## Important APIs, types, and functions

`snd_tscm_create_pcm_devices()` creates one playback and one capture substream. `pcm_init_hw_params()` selects S32 format, derives channel count from analog plus optional ADAT/S/PDIF channels, enables 44.1/48/88.2/96 kHz, and adds TASCAM AMDTP constraints. Prepare, trigger, pointer, and ack callbacks bind ALSA operations to `tx_stream` and `rx_stream`.

## Control flow

Open takes the stream lock, initializes hardware params, reads clock source, and when externally clocked or already streaming, constrains rate/period/buffer to current domain values. `pcm_hw_params()` reserves duplex resources and increments `substreams_counter`. `pcm_hw_free()` decrements and stops when the last substream is freed. Prepare starts the duplex stream at the runtime rate and prepares the selected AMDTP stream.

## State and persistence behavior

The file mutates runtime constraints, `substreams_counter`, stream lock state, and AMDTP PCM trigger state. Hardware rate and stream resources are managed by `tascam-stream.c`.

## Dependencies and integration points

It depends on model specs in `tascam.c`, stream helpers, AMDTP TASCAM constraints, and ALSA PCM core. Hwdep lock notifications share the same `dev_lock_count`.

## Risks and test signals

Risks include constraint attempts with zero period/buffer before reservation, counter imbalance, and wrong fixed channel counts for model specs. Tests should cover all models, external clock mode, duplex opens, rate changes, ADAT/S/PDIF variants, and xrun recovery.
