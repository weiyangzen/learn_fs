# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-proc.c

Read completely: 532 lines.

This implements SPL procfs and sysctl setup on Linux. It creates `/proc/spl`, `/proc/spl/kmem/slab`, `/proc/spl/kstat`, and `/proc/sys/kernel/spl` sysctl entries for hostid, git revision, and kmem/slab statistics.

Key responsibilities:
- Registers sysctl tables, with compatibility for old `register_sysctl_table()` and newer `register_sysctl_sz()` APIs.
- Creates proc directories and the slab seq_file.
- Implements proc handlers for debug kmem usage, aggregated slab statistics, and hostid reads/writes.
- Provides slab cache reporting by iterating `spl_kmem_cache_list`.
- Cleans up proc and sysctl entries on failure or module unload.

Important implementation details:
- `proc_doslab()` sums selected cache fields across caches matching `KMC_KVMEM` and total/alloc/max masks.
- `proc_dohostid()` prints hostid as hex without a `0x` prefix and parses writes the same way to preserve existing behavior.
- The slab seq_file prints a header and then one line per cache. Linux slab-backed caches report active-object accounting only; custom kvmem slabs report slab/object/emergency/deadlock statistics.
- The Linux 6.6/6.11 sysctl sentinel compatibility block keeps sentinel-terminated arrays for older kernels but registers size-minus-one when `register_sysctl_sz()` is available.
- `spl_proc_cleanup()` removes proc entries and unregisters sysctl tables, and is reused for partial init failure cleanup.

Dependencies and interactions:
- Depends on `spl-kmem-cache.c` global cache list/stat fields and on `spl-generic.c` hostid state.
- Creates `proc_spl_kstat`, which `spl-kstat.c` uses as the kstat namespace root.

Reliability notes:
- Proc/sysctl init has multiple failure points and central cleanup; teardown assumes entries may or may not have been created.
- Some proc handlers ignore writes by consuming the write length without changing read-only aggregate values.
