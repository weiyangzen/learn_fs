
# sources/distributed-fs/ceph-client/tools/perf/util/path.h

Purpose: declares perf path join and file-type helper APIs.

Important APIs/types/functions: exposes `path__join`, `path__join3`, `is_regular_file`, `is_directory`, and `is_directory_at`; forward-declares `struct dirent`.

Control flow: no executable flow.

State and persistence: helpers operate on caller buffers or live filesystem metadata only.

Dependencies: `stddef.h` and `stdbool.h`.

Integration points: included by utilities doing source-tree/sysfs/procfs traversal.

Risks: no declaration for `mkpath` despite implementation in `path.c`, implying legacy declaration elsewhere or dead use. Test signals are compile coverage and path helper unit/smoke tests.
