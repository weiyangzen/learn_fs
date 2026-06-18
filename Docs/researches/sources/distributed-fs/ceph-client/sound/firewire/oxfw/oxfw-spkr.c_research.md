# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-spkr.c

## Purpose

This file provides legacy ALSA mixer controls for Griffin FireWave and LaCie FireWire Speakers, preserving compatibility with older firewire-speaker behavior.

## Important APIs, types, and functions

`struct fw_spkr` caches mute, per-channel volume, min/max, channel count, and AV/C feature block IDs. `snd_oxfw_add_spkr()` allocates speaker state, reads min/max/current values from the device, and adds "PCM Playback Switch" and "PCM Playback Volume" controls. `avc_audio_feature_mute()` and `avc_audio_feature_volume()` implement AV/C feature function block transactions.

## Control flow

Control get callbacks return cached state. Put callbacks validate requested values, issue AV/C CONTROL transactions for changed mute or volume fields, and update the cache only on success. Volume writes optimize equal multi-channel values by writing master channel zero when possible, otherwise per-channel writes use a channel map that matches ALSA-visible order.

## State and persistence behavior

The cache in `oxfw->spec` persists for the ALSA card lifetime. Successful writes persist device mixer state. There is no notification path for out-of-band device changes.

## Dependencies and integration points

`oxfw.c` calls this during quirk detection for Griffin/LaCie IDs. It depends on `fcp_avc_transaction()` and ALSA control core.

## Risks and test signals

Risks include stale cached controls, channel-map mistakes, devices rejecting feature-block commands, and sign extension in 16-bit volume handling. Tests should read/write mute and volume on both models, validate channel ordering, reject out-of-range values, and handle short/failed FCP responses.
