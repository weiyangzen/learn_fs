# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_kstat.c

FreeBSD kstat compatibility layer implemented over `sysctl`.

Key behavior:
- `__kstat_create()` allocates `kstat_t`, computes data size by kstat type, creates `kstat.<module>.<class>` sysctl nodes, and initializes locks.
- Named kstats become individual sysctl procs, with handlers for numeric and string data.
- Dataset-class handlers check `zone_dataset_visible()` before exposing dataset stats.
- Raw kstats use `sbuf` output and dynamic buffer growth up to `KSTAT_RAW_MAX`; they support traditional raw callbacks and `seq_file`-style headers.
- IO kstats are formatted as a text line of read/write counters and timing fields.
- `kstat_delete()` frees sysctl context, data, lock, and kstat structure.

Unsupported kstat types panic during creation or installation.
