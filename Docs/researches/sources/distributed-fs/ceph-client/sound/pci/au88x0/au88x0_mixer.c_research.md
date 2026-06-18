# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mixer.c

## Purpose
Creates the ALSA AC97 mixer bus for the Vortex codec and performs small control cleanup after mixer creation.

## Important APIs, Types, And Functions
`remove_ctl()` removes named mixer controls by building a `snd_ctl_elem_id`. `snd_vortex_mixer()` creates an AC97 bus using `vortex_codec_write`/`vortex_codec_read`, instantiates the AC97 mixer, stores `vortex->codec`, detects quad support from the codec extended ID, and removes mono master controls.

## Control Flow
Probe code calls `snd_vortex_mixer()`. It creates an AC97 bus, zeroes an AC97 template, sets `private_data` to `vortex`, disables AC97 SPDIF capability in `scaps`, creates the AC97 mixer, updates `vortex->isquad`, and removes two unwanted controls.

## State And Persistence
Runtime state is `vortex->codec` and `vortex->isquad`. ALSA controls live on the card and are removed with card teardown. There is no persistence beyond ALSA mixer state.

## Dependencies And Integration Points
Depends on core codec accessors from `au88x0_core.c`, ALSA AC97 APIs, and `au88x0.h`. Quad detection affects PCM channel constraints and routing in other files.

## Risks
`remove_ctl()` ignores missing-control errors, which is acceptable cleanup but can hide unexpected mixer topology changes. `vortex->isquad` is set to zero if mixer creation leaves codec NULL; route/channel behavior depends on this flag.

## Test Signals
Expected signals are AC97 mixer creation, usable playback/capture mixer controls, absent mono master controls, and correct quad/stereo channel limits based on codec capabilities.
