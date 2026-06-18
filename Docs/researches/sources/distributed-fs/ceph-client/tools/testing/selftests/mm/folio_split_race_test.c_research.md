# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/folio_split_race_test.c

Purpose: stress test for race conditions between shmem folio splitting via `MADV_REMOVE` and concurrent pagecache reads via `filemap_get_entry()`.

Important APIs/types/functions: uses `mmap(MAP_SHARED|MAP_ANONYMOUS)`, `madvise(MADV_HUGEPAGE)`, `madvise(MADV_REMOVE)`, `pthread` reader threads, C11 atomics, barriers, THP settings helpers, `check_huge_shmem()`, and kselftest.

Control flow: main verifies THP/root prerequisites, saves THP settings, sets shmem THP to advise mode, and runs 100 iterations. Each iteration maps five PMD-sized shmem huge pages, fills every base page with a marker containing its page index, verifies shmem THP allocation, starts 16 reader threads, then punches non-hugepage-aligned hole ranges every 50 pages. Readers continuously verify all non-punched pages and record corruption. Any corruption breaks the iteration loop and fails the single planned test; otherwise all iterations pass.

State and persistence: temporarily changes THP shmem settings and restores them through `atexit` and signal handlers. Allocates transient shared memory only.

Dependencies and integration points: root, THP support, PMD page size detection, shmem huge pages, pthreads.

Risks: timing/race stress can be CPU-heavy. If interrupted by unhandled signals, THP settings restoration may not run beyond configured handlers.

Test signals: failure prints corrupted page details; pass requires zero reader failures across all iterations.
