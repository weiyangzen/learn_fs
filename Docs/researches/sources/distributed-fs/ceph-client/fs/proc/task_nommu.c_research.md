<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/task_nommu.c -->
## sources/distributed-fs/ceph-client/fs/proc/task_nommu.c

Purpose: implements NOMMU per-task memory reporting for `/proc/<pid>/maps`, task memory summaries, virtual size, and statm-like values.

Important APIs and functions: exports `task_mem`, `task_vsize`, `task_statm`, and `proc_pid_maps_operations`. Internals include `nommu_vma_show`, `proc_get_vma`, seq iterator functions `m_start/m_next/m_stop`, `maps_open`, `map_release`, and `pid_maps_open`.

Control flow: task memory helpers take `mmap_read_lock`, iterate VMAs, and account VMA objects, backing `vm_region` allocations, region spans, mm/fs/files/sighand/task object sizes, and shared versus private ownership heuristics. The maps file opens by pinning the target mm with ptrace read permission, then seq iteration locks the mm, initializes a VMA iterator from the file position, formats each VMA, and releases task/mm refs at stop.

State and persistence behavior: no persistent mutations occur. Per-open seq private state stores the proc inode and pinned mm reference until release. Reported memory is an approximate live accounting based on object sizes and NOMMU region sharing.

Dependencies and integration points: depends on NOMMU VMA/region structures, `kobjsize`, VFS file path formatting, proc PID task/mm access, ptrace permission, mmap locking, and seq_file. It is the NOMMU counterpart to `task_mmu.c`.

Risks: memory accounting is approximate and can double-count or classify shared objects based on reference counts. Iterator positions use virtual addresses and `-1UL` sentinel semantics. Output must stay maps-compatible despite NOMMU-specific `S/s` shared flags.

Test signals: NOMMU builds with private and shared mappings; task exit during maps read; mmap changes while reading; statm/memory summary sanity; file-backed and stack VMA formatting; ptrace permission denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/task_nommu.c -->
