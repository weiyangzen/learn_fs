# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/rmap.c

Purpose: reverse-map functional test ensuring page migration of a shared physical page remains visible through a randomly generated process tree for anonymous, POSIX shm, regular file, and KSM-merged mappings.

Important APIs and functions: `propagate_children()` builds a multi-level fork tree and chooses one worker; `try_to_move_page()` uses `move_pages()`; `move_region()` records the migrated PFN from pagemap; `has_same_pfn()` validates other processes; KSM paths use `ksm_start()` and `PR_SET_MEMORY_MERGE`.

Control flow: fixture setup requires NUMA with multiple nodes, initializes shared expected-PFN storage, semaphore, pipe, random seed, and worker level. Each test configures mapping backend and callbacks, then calls `propagate_children()`.

State and dependencies: state spans a process tree, SYSV semaphore, pipe, shared PFN mapping, temp shm/file names, KSM sysfs state, and page migration. Depends on libnuma, pagemap, `move_pages(2)`, KSM helpers, and sufficient NUMA permissions.

Risks and test signals: failures distinguish worker migration failure from checker PFN mismatch. Migration is best-effort and environment-sensitive under NUMA policy, pressure, permissions, and KSM timing.
