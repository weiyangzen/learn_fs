# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/droppable.c

Purpose: tests `MAP_DROPPABLE` anonymous mappings by forcing memory pressure until pages are dropped.

Important APIs/types/functions: uses `mmap(PROT_READ|PROT_WRITE, MAP_ANONYMOUS|MAP_DROPPABLE)`, `fork`, `malloc` pressure loop, `kill(SIGTERM)`, and kselftest output.

Control flow: maps 128 MiB droppable memory, fills and verifies it, forks a child that continuously allocates/touches pages, parent scans the droppable mapping until it observes a zeroed page, kills the child, and reports pass.

State and persistence: consumes memory aggressively and relies on kernel reclamation of droppable pages. No persistent files.

Dependencies and integration points: kernel support for `MAP_DROPPABLE` and enough memory pressure to reclaim pages.

Risks: child allocation loop is unbounded until parent detects a drop; on unsupported or misbehaving kernels the test may hang or trigger OOM behavior.

Test signals: pass when any previously filled page reads zero; assertions abort on setup failures.
