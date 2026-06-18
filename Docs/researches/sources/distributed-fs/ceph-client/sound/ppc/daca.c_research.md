# sources/distributed-fs/ceph-client/sound/ppc/daca.c

## Purpose

This file implements support for the PowerMac DACA I2C audio codec, including I2C initialization, output volume, deemphasis, amplifier switch, cleanup, and resume replay.

## Important APIs, types, and functions

`struct pmac_daca` embeds `struct pmac_keywest` and caches left/right volume, deemphasis, and amplifier state. `snd_pmac_daca_init()` loads `i2c-powermac`, allocates mixer state, initializes Keywest I2C at address `0x4d`, creates three ALSA mixer controls, and installs cleanup/resume callbacks. `daca_init_client()` programs sample-rate and global config registers; `daca_set_volume()` writes the two-byte analog volume/deemphasis register.

## Control flow

Probe initializes the I2C client, writes DACA defaults, then adds `Deemphasis Switch`, `Master Playback Volume`, and `Power Amplifier Switch`. Control puts validate values, update cached state, and write the affected DACA register. Resume replays sample-rate, amplifier config, and cached volume/deemphasis.

## State and persistence behavior

Mixer state persists in `chip->mixer_data` as `struct pmac_daca`. Hardware state is replayed from that cache because the codec is controlled over I2C and may lose configuration over suspend.

## Dependencies and integration points

It depends on `keywest.c` for dynamic Keywest I2C client discovery, ALSA control APIs, and `pmac.c` model selection. DACA systems are playback-only in `snd_pmac_detect()`, so this codec integrates with PowerMac PCM without capture.

## Risks and test signals

Risks include deferred or missing I2C adapter discovery, leaked mixer data when `snd_pmac_keywest_init()` fails after allocation, unchecked I2C errors in some control paths, and cache mismatch after failed writes. Test DACA probe deferral, mixer writes, amplifier off/on, resume replay, and module removal.
