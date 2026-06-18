# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/transhuge-stress.c

Purpose: long-running transparent hugepage stress tool that repeatedly allocates THPs, records physical distribution, and splits most of each THP with `MADV_DONTNEED` to exercise compaction, allocation, and migration paths.

Important APIs and functions: `main()` parses optional `-f` backing file, `-d` duration, and size MiB; uses `allocate_transhuge()` from `vm_util.h`, `/proc/self/pagemap`, `MADV_HUGEPAGE`, and a PFN-index bitmap to count distinct hugepage frames.

Control flow and state: after THP availability and mapping setup, an infinite loop touches each hugepage chunk, records successes/failures, discards all but the last base page, prints throughput and counts, and exits successfully only when a positive duration elapses.

Dependencies and risks: depends on THP policy, physical memory, pagemap access, and optional prepared backing file. It can create heavy memory pressure; without `-d`, it intentionally runs forever.
