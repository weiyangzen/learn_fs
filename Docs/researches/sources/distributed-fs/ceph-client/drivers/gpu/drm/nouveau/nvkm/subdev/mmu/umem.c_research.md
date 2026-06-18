# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.c

## Purpose
Implements the user-visible NVIF memory object that allocates MMU memory, maps it to CPU or BAR1 IO, unmaps it, and lets VMM objects look it up by handle.

## Important APIs, Types, and Functions
Key symbols are `nvkm_umem_new`, `nvkm_umem_search`, `nvkm_umem_map`, `nvkm_umem_unmap`, and `nvkm_umem_dtor`. The object function table exposes map/unmap/dtor.

## Control Flow, State, and Persistence
Creation validates a user type index, records the resolved memory type flags, forces mappable memory to at least PAGE_SHIFT, allocates memory through `nvkm_mem_new_type`, links the object into the client `umem` list, and returns page/address/size. Map supports host `vmap` for host memory without extra args or BAR1 IO mapping for VRAM/kind memory. Unmap releases BAR1 VMA or CPU vmap. Search can find memory in the local client or the master client list.

## Dependencies and Integration Points
Depends on `ummu`, `nvkm_mem_new_type`, BAR1 VMM, client object lookup, NVIF memory ABI, and VMM mapping code.

## Risks and Test Signals
Risks include stale client list entries, map/unmap state confusion, master-client handle exposure, BAR1 VMA leaks, and host map lifetime issues. Test user memory allocation, cross-client lookup rules, repeated map/unmap errors, host vmap, VRAM BAR1 map, and destructor cleanup.
