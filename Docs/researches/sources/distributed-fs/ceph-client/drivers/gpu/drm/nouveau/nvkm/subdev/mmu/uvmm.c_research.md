# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.c

## Purpose
Implements the user-visible VMM object for address-space allocation, mapping user memory, PFN map/clear, raw managed-range operations, backend-specific methods, and VMM lookup by handle.

## Important APIs, Types, and Functions
Key symbols are `nvkm_uvmm_new`, `nvkm_uvmm_search`, `nvkm_uvmm_mthd_get`, `put`, `map`, `unmap`, `pfnmap`, `pfnclr`, `page`, and raw helpers `raw_get`, `raw_put`, `raw_map`, `raw_unmap`, `raw_sparse`.

## Control Flow, State, and Persistence
Creation either constructs a per-user VMM through the chip VMM constructor or references the global MMU VMM, then optionally promotes it and reports page count/address/size. Standard methods lock `vmm->mutex.vmm`, validate managed raw restrictions, split VMAs when needed, mark VMAs busy during asynchronous map work, and use `nvkm_umem_search` to bind memory handles. Raw methods operate only inside managed ranges and require `vmm->managed.raw`.

## Dependencies and Integration Points
Depends on `umem`, `ummu`, `nvkm_vmm_*` core APIs, NVIF VMM ABI, client objects, and chip-specific VMM method hooks.

## Risks and Test Signals
Risks include VMA busy-state leaks on map failure, managed/raw range bypass, handle lifetime races, split/merge bugs, PFN array size validation, and global VMM size misuse. Test get/put/map/unmap sequences, raw managed VMM operations, PFN mapping with invalid entries, backend methods, concurrent maps, and object destruction.
