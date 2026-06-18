# sources/distributed-fs/ceph-client/sound/ac97/ac97_core.h

## Purpose

This private header shares minimal helpers between the new AC97 bus core and compatibility layer.

## Important APIs, types, and functions

It declares `snd_ac97_bus_scan_one()` and defines `ac97_ids_match(id1, id2, mask)`, which compares two vendor IDs under a mask.

## Control Flow

There is no complex control flow. The inline helper performs a masked equality check; the scan declaration is implemented in `bus.c`.

## State and Persistence

No state is stored.

## Dependencies and Integration Points

It integrates `bus.c` with `snd_ac97_compat.c`, letting compatibility reset code reuse new-bus scanning and ID matching.

## Risks and Test Signals

Risks include mask direction mistakes and mismatched declarations if scan semantics change. Tests should check exact, masked, invalid, and zero vendor ID reset cases.
