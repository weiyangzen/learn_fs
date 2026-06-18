# sources/distributed-fs/ceph-client/sound/ac97_bus.c

## Purpose

This file implements the legacy AC97 bus interface: a simple driver-model bus type and a reset helper for old `struct snd_ac97` users.

## Important APIs, types, and functions

Public exports are `snd_ac97_reset` and `ac97_bus_type`. Internal `snd_ac97_check_id()` reads vendor ID registers and validates them against an optional expected ID and mask. Module init and exit register and unregister the bus.

## Control Flow

`snd_ac97_reset()` optionally performs a warm reset, checks the vendor ID, and returns `1` if warm reset was enough. Otherwise it performs cold reset if available, then warm reset if available, checks the vendor ID again, and returns `0` on success or `-ENODEV` on mismatch. Bus registration happens at `subsys_initcall`.

## State and Persistence

The only persistent state is the globally exported `ac97_bus_type`. Individual `snd_ac97` state is owned by callers and updated with the read vendor ID.

## Dependencies and Integration Points

It depends on legacy `<sound/ac97_codec.h>`, driver core bus registration, and AC97 bus ops supplied by controller drivers. It is selected by the top-level sound Makefile through `CONFIG_AC97_BUS`.

## Risks and Test Signals

Risks include invalid vendor ID handling, optional reset callbacks being NULL, and symbol conflicts with new-bus compatibility. Tests should cover reset paths with warm-only success, cold fallback, missing callbacks, invalid IDs, and masked expected IDs.
