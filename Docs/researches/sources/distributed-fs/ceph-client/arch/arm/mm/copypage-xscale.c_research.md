## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-xscale.c

### Purpose
Implements XScale mini-dcache optimized user highpage copy/clear, reducing main D-cache thrash during page faults.

### Important APIs, Types, And Functions
Exports `xscale_mc_user_fns`. Important items include `minicache_pgprot`, `minicache_lock`, `xscale_mc_copy_user_highpage`, `xscale_mc_clear_user_highpage`, private `mc_copy_user_page`, and `set_top_pte(COPYPAGE_MINICACHE, ...)`.

### Control Flow
Copy flushes the source folio if `PG_dcache_clean` was not already set, locks the single fixed mini-cache alias, maps the source page there, copies with XScale prefetch/doubleword assembly into the destination, and unlocks. Clear writes zero doublewords and performs D-line clean/invalidate operations.

### State, Dependencies, And Integration
Persistent state is `minicache_lock`. It depends on highmem, folio cache-clean tracking, `mm.h` fixed alias helpers, XScale CP15 operations, and generic ARM CPU user-vector setup.

### Risks And Test Signals
Risks include alias serialization bugs, incorrect mini-cache memory type, source folio clean-bit misuse, and assembly portability. Test XScale configs, highmem COW, page-cache aliases, fork/exec loops, and cache-coherency stress.
