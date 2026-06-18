<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/nommu.c -->
## sources/distributed-fs/ceph-client/fs/proc/nommu.c

Purpose: implements global `/proc/maps` for NOMMU kernels, listing all `vm_region` objects known to the kernel.

Important APIs and functions: `nommu_region_show` formats one region, `nommu_region_list_start/next/stop/show` implement seq iteration over `nommu_region_tree`, and `proc_nommu_init` registers the file.

Control flow: opening/reading the seq file takes `nommu_region_sem` for the duration of iteration, walks the rb-tree from the first node to the requested position, and formats each region with address range, permissions, offset, device/inode, and optional file path.

State and persistence behavior: no local state persists; the source of truth is the global NOMMU region rb-tree. The read lock stabilizes the region list during seq traversal.

Dependencies and integration points: depends on NOMMU VM region tracking, rb-tree iteration, seq_file, procfs, and VFS path formatting. It is distinct from per-process `task_nommu.c` maps.

Risks: long reads hold `nommu_region_sem`, so very large region sets can delay region mutation. ABI formatting must remain compatible with proc maps parsers while representing NOMMU-specific shared/private flags.

Test signals: NOMMU builds; mapped file and anonymous regions; concurrent mmap/munmap while reading; seq seek behavior; path formatting for deleted or special files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/nommu.c -->
