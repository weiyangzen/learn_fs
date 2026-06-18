# sources/distributed-fs/ceph-client/sound/aoa/core/alsa.h

## Purpose

This private header declares AOA ALSA card initialization and cleanup helpers for the core.

## Important APIs, types, and functions

It declares `aoa_alsa_init(char *name, struct module *mod, struct device *dev)` and `aoa_alsa_cleanup()`.

## Control Flow

There is no executable logic.

## State and Persistence

No state is stored in the header. The implementation's singleton state is in `alsa.c`.

## Dependencies and Integration Points

It includes `../aoa.h` and is used by `core.c` and `alsa.c`.

## Risks and Test Signals

Risks are limited to prototype drift. Build tests catch mismatches between declarations and implementation.
