# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.h

## Purpose
`int-map.h` declares the opaque integer-to-pointer map used by VDO subsystems. It states the key contract: `u64` keys, `void *` values, and no support for NULL values.

## Important APIs, Types, and Functions
The header forward-declares `struct int_map` and exposes creation, free, size, get, put, and remove functions. `vdo_int_map_put()` takes an `update` flag and optional old-value output so callers can either insert-only or replace existing mappings.

## Control Flow
The header defines no logic, but callers follow a lifecycle: create a map, perform get/put/remove operations, then free it after all external value ownership has been handled.

## State and Persistence Behavior
Map state is private to `int-map.c`; the header enforces opacity. Persistence is not involved. Since values are not owned by the map, freeing a map does not free stored objects.

## Dependencies and Integration Points
It includes Linux compiler and type definitions. The interface is used by zone lock tables and bio submission merge tables.

## Risks and Edge Cases
Callers must not store NULL values, must serialize concurrent access, and must free or otherwise own mapped values separately. `update=false` is important for lock-acquisition races because it returns the existing holder without overwriting it.

## Test Signals
Compile-time API compatibility plus integration tests for physical/logical zone lock maps and I/O submitter merge maps are the main signals.
