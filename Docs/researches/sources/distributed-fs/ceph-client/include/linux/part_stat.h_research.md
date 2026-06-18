# Research: sources/distributed-fs/ceph-client/include/linux/part_stat.h

Purpose: `part_stat.h` defines per-CPU block-device partition statistics and macros for efficient updates/readout of I/O counters.

Important APIs/types/functions: `struct disk_stats` contains per-stat-group nanoseconds, sectors, I/O counts, merges, `io_ticks`, and local in-flight counters. Macros include `part_stat_lock()`, `part_stat_unlock()`, `part_stat_get_cpu()`, `part_stat_get()`, `part_stat_read()`, `part_stat_set_all()`, `part_stat_read_accum()`, add/sub/inc/dec helpers, local in-flight helpers, and `bdev_count_inflight()`.

Control flow and state: update callers disable preemption, update the current CPU's `bd_stats`, and mirror normal counters to the whole-disk device when operating on a partition. Reads aggregate all possible CPUs. In-flight uses `local_t` for read/write directions and is read per CPU or aggregated by the external helper.

Dependencies and integration points: depends on `linux/blkdev.h`, `asm/local.h`, per-CPU APIs, block-device partition helpers, and stat group constants. It integrates with block accounting, `/proc/diskstats`, sysfs statistics, and request completion paths.

Risks and test signals: risks include missing preemption protection during updates, double-counting whole-disk stats, field type assumptions in `TYPEOF_UNQUAL`, and stale per-CPU aggregation after CPU hotplug. Tests should validate diskstats under partition and whole-disk I/O, concurrent updates, in-flight counts, reset paths, and CPU-hotplug accounting.
