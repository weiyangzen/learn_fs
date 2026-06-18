# sources/distributed-fs/ceph-client/tools/mm/thpmaps

Purpose: Python utility that prints smaps-like transparent hugepage and contiguous-block mapping statistics per VMA, per process/cgroup, or as a rollup.

Important APIs and types: `BinArrayFile` abstracts binary array reads from pagemap and kpageflags using `preadv`; `PageMap` and `KPageFlags` specialize it. `VMAList` parses `/proc/<pid>/smaps` into `VMA` namedtuples. `thp_parse`, `cont_parse`, and `vma_parse` derive THP/contiguous mapping statistics using numpy arrays. `do_main` selects pids and output mode.

Control flow: Module import reads base page size and PMD size from sysfs. CLI parsing validates `--pid`, `--cgroup`, `--rollup`, `--cont`, `--inc-smaps`, `--inc-empty`, and `--periodic`. Each VMA with RSS is mapped through pagemap to PFNs, present THP pages are filtered by kpageflags, contiguous ranges are identified, PMD-mapped pages from smaps are subtracted to avoid double counting, and stats are printed.

State and persistence behavior: Read-only against `/proc`, `/proc/kpageflags`, cgroup `cgroup.procs`, and THP sysfs. Periodic mode repeats with no persisted cache.

Dependencies and integration points: Requires Python 3, numpy, root privileges for pagemap/kpageflags, and Linux THP sysfs/procfs formats.

Risks: Races with process exit and VMA changes are partly handled but can skew counts. PFN visibility is privilege-dependent. Numpy operations assume same-sized arrays and power-of-two cont sizes. Import-time sysfs read fails on systems without THP hpage PMD size.

Test signals: Run on self, selected pids, cgroup subtrees, rollup, `--cont 64K`, `--inc-smaps`, periodic mode, and non-root error cases; compare totals against smaps.
