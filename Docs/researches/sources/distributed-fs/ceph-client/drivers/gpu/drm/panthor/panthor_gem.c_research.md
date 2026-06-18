# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.c

`panthor_gem.c` implements Panthor GEM object creation, kernel BO allocation and VM mapping, PRIME import/export with cache maintenance, CPU cache sync ioctl support, BO labels, transparent hugepage setup, and debugfs accounting.

Public APIs include `panthor_gem_init()`, `panthor_gem_create_object()`, `panthor_gem_create_with_handle()`, `panthor_kernel_bo_create()`, `panthor_kernel_bo_destroy()`, `panthor_gem_prime_import()`, label helpers, `panthor_gem_sync()`, and debugfs printing. Important internals are `should_map_wc()`, object free, custom dma-buf ops, object status, and `panthor_gem_funcs`.

User BO creation allocates shmem, stores flags, chooses WC versus WB mapping, optionally ties reservations to an exclusive VM root GEM, forces page allocation/cache flush for WC mappings, creates a handle, and drops the allocation ref. Kernel BO creation labels/debug-tags the BO, allocates GPU VA, maps it into a VM, and returns a wrapper; destroy unmaps VA, frees VA, drops GEM/VM refs, and frees the wrapper. BO sync validates ranges and performs DMA cache maintenance over sg segments.

Persistent state is `struct panthor_gem_object`: shmem base, flags, exclusive VM root GEM, label, and debugfs metadata; `struct panthor_kernel_bo` stores VM, VA node, object, and vmap. Dependencies are DRM shmem, dma-buf, DMA API, Panthor VM/FW/driver parameter, and debugfs. Risks are cache coherency on coherent/noncoherent systems, exclusive VM sharing/export, reservation substitution, and label lifetime. Tests should cover BO flags, PRIME, BO_SYNC ranges, kernel BO lifecycle, labels, hugepage parameter, and noncoherent correctness.
