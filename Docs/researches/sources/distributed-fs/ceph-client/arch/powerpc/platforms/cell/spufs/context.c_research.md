# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/context.c

Purpose: manages the lifecycle and locking discipline for `struct spu_context`. It allocates a context, initializes its CSA and wait queues, holds the owner `mm_struct`, and tears everything down when the final reference is dropped.

Important APIs: `alloc_spu_context`, `destroy_spu_context`, `get_spu_context`, `put_spu_context`, `spu_forget`, `spu_unmap_mappings`, `spu_acquire_saved`, and `spu_release_saved`. `nr_spu_contexts` tracks live contexts for scheduler/proc reporting.

Control flow: allocation initializes `mmio_lock`, mapping/state/run mutexes, wait queues, scheduler lists, saved state, backing ops, owner mm, statistics, and optional gang membership. Destruction acquires `state_mutex`, deactivates any hardware binding, finalizes the CSA, removes gang membership, releases profiling private data, validates runqueue removal, frees switch log storage, and drops memory. `spu_forget()` is used at directory removal to deactivate and release the owner mm before context release.

State and dependencies: mappings are tracked through address_space pointers and invalidated by `spu_unmap_mappings()` during switches or isolate setup. The file depends on scheduler helpers, gang helpers, `spu_init_csa`, and `spu_deactivate`. Risks cluster around lock ordering, use-after-free through mmap faults, and releasing `owner` exactly once. Test signals include create/close loops, mmap invalidation during deactivation, and `nr_spu_contexts` returning to baseline.
