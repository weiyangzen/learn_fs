# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/top/base.c

## Purpose
Implements common GPU topology parsing storage and lookup helpers for engine addresses, reset bits, interrupt masks, and fault IDs.

## Important APIs, Types, And Functions
Important functions are `nvkm_top_device_new()`, `nvkm_top_addr()`, `nvkm_top_reset()`, `nvkm_top_intr_mask()`, `nvkm_top_fault_id()`, `nvkm_top_fault()`, `nvkm_top_parse()`, and `nvkm_top_new_()`.

## Control Flow
Construction initializes the topology list. `nvkm_top_parse()` lazily invokes the chip parser only once. Lookup helpers scan the list for matching type/instance and return encoded address, reset, interrupt, or fault mapping.

## State, Persistence, And Dependencies
State is the `nvkm_top` subdev and its linked list of `nvkm_top_device` records, freed at dtor.

## Integration Points
Depends on chip parsers in GK104/GA100 files and on `nvkm_device_subdev()` for reverse fault mapping.

## Risks
Lookups return zero or `-ENOENT` for missing data, so callers must distinguish absent topology from valid zero address where relevant. Parser allocation failures stop topology discovery.

## Test Signals
Signals include parsed debug lines, correct engine reset/intr/fault mapping, and no duplicate parse after the list is populated.
