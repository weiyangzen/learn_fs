# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.h

## Purpose

This header defines the ctxfi mixer object and its public creation/destruction API.

## Important APIs, types, and functions

`INIT_VOL` is the default hardware mixer gain. `enum MIXER_PORT_T` names logical mixer ports for wave, SPDIF, PCM, mic, and line paths. `struct ct_mixer` stores the parent ATC, AMIXER/SUM resource arrays, switch bitmap, routing callbacks, and optional PM resume callback. It declares `ct_alsa_mix_create()`, `ct_mixer_create()`, and `ct_mixer_destroy()`.

## Control flow

ATC creates a `ct_mixer`, then ALSA device setup calls `ct_alsa_mix_create()` to register controls. PCM and routing code use the callback members rather than reaching into AMIXER internals.

## State and persistence behavior

The header describes mixer-owned state but does not allocate it. The switch bitmap is the persistent software source for replaying hardware mute/source state after resume.

## Dependencies and integration points

It depends on `ctatc.h` and `ctresource.h`. It is consumed by ATC setup and PCM/routing code that needs mixer endpoints as generic `struct rsc` objects.

## Risks and test signals

Enum order is ABI-like within the driver because implementation tables depend on it. Compile coverage plus smoke tests for all exposed ALSA controls catch mismatches.
