# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mmu.c

## Purpose
This file constructs and destroys the NVIF MMU object and discovers supported heaps, memory types, compression kinds, and memory object class.

## Important APIs, Types, and Functions
Public functions are `nvif_mmu_ctor` and `nvif_mmu_dtor`.

## Control Flow
Constructor creates the MMU object, records DMA bits and counts, selects a supported memory class, allocates heap/type/kind arrays, queries each heap and type, translates type booleans into `NVIF_MEM_*` flags, optionally queries kind data, and tears down on failure. Destructor frees arrays and destroys the object if constructed.

## State and Persistence Behavior
State includes `dmabits`, memory object class, heap/type/kind arrays, kind inversion value, and object handle. It persists for the client/device lifetime.

## Dependencies and Integration Points
It depends on NVIF object methods, MMU class ABI, memory class IDs, and memory constructors that consume type/kind metadata.

## Risks
Partial allocation failure must free all arrays. Backend count values drive allocation sizes. Kind query handling must preserve `kind_inv` even when there are no kinds.

## Test Signals
Signals include MMU construction on NV04/NV50/GF100 class backends, type flag correctness, kind discovery, low-memory failure injection, and destructor idempotence.
