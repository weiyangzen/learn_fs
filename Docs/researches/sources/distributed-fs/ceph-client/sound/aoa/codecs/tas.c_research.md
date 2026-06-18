# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas.c

## Purpose

This file implements the Apple Onboard Audio TAS3004 codec driver. It registers an I2C codec, manages TAS hardware reset and register programming, exposes ALSA controls for volume, mute, mixer, dynamic range compression, capture source, treble, and bass, and attaches PCM capabilities to a soundbus device.

## Important APIs, types, and functions

State lives in `struct tas`: AOA codec, I2C client, mute/control/DRC/hardware flags, cached volume, mixer arrays, tone values, analog control register, DRC range, and mutex. Important functions are `tas_write_reg`, `tas3004_set_drc`, `tas_set_treble`, `tas_set_bass`, `tas_set_volume`, `tas_set_mixer`, ALSA control callbacks, `tas_reset_init`, `tas_switch_clock`, PM suspend/resume wrappers, `tas_init_codec`, `tas_exit_codec`, `tas_i2c_probe`, and `tas_i2c_remove`.

## Control Flow

I2C probe allocates and initializes software state, sets default DRC range, fills codec callbacks, and registers with AOA. Fabric init calls `tas_init_codec()`, which resets via GPIO, programs main control, analog power-down/up, DRC, tone, and then attaches to soundbus and creates ALSA controls. Control callbacks update cached software state under the mutex and write hardware only if `hw_enabled`. Clock switch prepare mutes amps and marks hardware disabled; clock restore resets hardware and reapplies cached volume/mixer state.

## State and Persistence

Unlike Onyx, TAS state is mostly software-cached control state rather than register cache. `hw_enabled` gates writes across clock transitions and suspend. `acr`, DRC, volume, mixer, bass, treble, and mute state persist across reinitialization and are replayed on resume or clock restore.

## Dependencies and Integration Points

It depends on I2C SMBus block writes, OF, AOA core, ALSA controls, soundbus attachment, fabric-provided GPIO, and TAS lookup headers. The layout fabric supplies connection data, but this driver notes it does not fully honor `aoa_codec.connected`.

## Risks and Test Signals

Risks include controls not reflecting actual hardware when disconnected endpoints exist, out-of-range mixer writes because mixer put lacks explicit range validation, partial control creation unwind, I2C write errors being ignored in setters, mono microphone assumptions, and reset timing sensitivity. Tests should cover probe/remove, all ALSA controls, cached state replay after clock switch and PM resume, DRC limits, capture source bits, and hardware absent/I2C failure paths.
