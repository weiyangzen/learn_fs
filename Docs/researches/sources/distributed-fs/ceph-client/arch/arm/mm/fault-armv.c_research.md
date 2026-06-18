## sources/distributed-fs/ceph-client/arch/arm/mm/fault-armv.c

### Purpose
Implements ARMv4/v5-era cache and write-buffer coherency fixups used when installing PTEs and checking legacy write-buffer aliasing behavior.

### Important APIs, Types, And Functions
Main exported hook is `update_mmu_cache_range` for `__LINUX_ARM_ARCH__ < 6`. Helpers include `do_adjust_pte`, `adjust_pte`, `make_coherent`, `check_writebuffer`, and `check_writebuffer_bugs`. Important state is `shared_pte_mask`, initially bufferable and downgraded to uncached if write-buffer coherency fails.

### Control Flow
When a valid PTE is installed, `update_mmu_cache_range` ignores invalid/zero PFNs, flushes dirty kernel D-cache data for the folio, then handles mapping aliases: VIVT shared mappings may be walked through `mapping->i_mmap` and converted to `shared_pte_mask`; executable mappings may trigger full I-cache flush. Boot-time `check_writebuffer_bugs` maps the same page twice, probes whether writes remain coherent, and changes the shared PTE policy if not.

### State, Dependencies, And Integration
State is `shared_pte_mask`. Depends on folio cache-clean flags, interval-tree VMA mapping locks, PTE locks, outer cache, vmap, and TLB/cache flushes. Integrates with generic MM fault/PTE installation.

### Risks And Test Signals
Risks include PTE-lock deadlocks, missing alias conversion, stale I-cache for executable mappings, and false write-buffer test results. Test old ARM builds, shared mmap aliasing, executable file mappings, fork/COW, and boot log write-buffer coherency result.
