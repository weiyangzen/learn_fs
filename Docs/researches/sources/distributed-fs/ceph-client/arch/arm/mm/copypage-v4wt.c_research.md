## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v4wt.c

### Purpose
Provides ARMv4 write-through cache user page copy/clear routines where dirty data does not require write-back handling, but I/D cache freshness still matters.

### Important APIs, Types, And Functions
Exports `v4wt_user_fns`. Public routines are `v4wt_copy_user_highpage` and `v4wt_clear_user_highpage`; private `v4wt_copy_user_page` performs the bulk copy and finishes with a CP15 flush ID cache operation.

### Control Flow
Copy maps source and destination with `kmap_atomic`, performs an unrolled PAGE_SIZE copy, flushes ID cache, and unmaps. Clear maps the destination, stores zeros through the whole page, flushes ID cache, and unmaps.

### State, Dependencies, And Integration
No persistent state. It depends on highmem and ARMv4 CP15 cache maintenance. Integration is through the CPU user function vector.

### Risks And Test Signals
Risks include using this path on a write-back CPU, missing instruction-cache visibility after writing executable pages, and assembly clobber errors. Test write-through ARMv4 configs, page copy/clear selftests, executable anonymous mappings, and repeated fork/exec workloads.
