## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4mc.c

### Purpose
Implements ARMv4 mini-dcache user-page copy/clear routines for CPUs where using a mini-cache mapping avoids thrashing the main data cache during page faults.

### Important APIs, Types, And Functions
Exports `v4_mc_user_fns`. Important items are `minicache_pgprot`, `minicache_lock`, `v4_mc_copy_user_highpage`, `v4_mc_clear_user_highpage`, private `mc_copy_user_page`, and `set_top_pte(COPYPAGE_MINICACHE, ...)`.

### Control Flow
Copy ensures source folio D-cache cleanliness via `PG_dcache_clean` and `__flush_dcache_folio`, locks the mini-cache mapping, installs a temporary top-level PTE for the source page, copies from the fixed alias to the destination, unlocks, and unmaps. Clear stores zeros to the destination while invalidating D-cache lines.

### State, Dependencies, And Integration
Persistent state is only the raw spinlock. It depends on `mm.h` fixed copy-page addresses, page-table helper `set_top_pte`, highmem, folio cache-clean flags, and ARMv4 cache operations. It integrates with CPU user function selection.

### Risks And Test Signals
Risks include fixed-alias races without the lock, wrong mini-cache PTE attributes, and stale source data if folio clean state is mishandled. Test page COW, tmpfs/page-cache mappings, highmem, VIPT/VIVT alias workloads, and ARMv4 mini-cache builds.
