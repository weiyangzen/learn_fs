# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.h

## Purpose

This header exposes ALSA PCM creation for ctxfi logical devices.

## Important APIs, types, and functions

It includes `ctatc.h` and declares `ct_alsa_pcm_create(struct ct_atc *atc, enum CTALSADEVS device, const char *device_name)`.

## Control flow

ATC device setup calls this function for each logical PCM device it wants to register.

## State and persistence behavior

The header owns no state; PCM runtime state is allocated by `ctpcm.c` callbacks.

## Dependencies and integration points

It couples PCM registration to the ATC device enum and ALSA card stored in `struct ct_atc`.

## Risks and test signals

The main risk is enum/device mismatch with ATC callers. Build tests and ALSA PCM enumeration catch regressions.
