<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_to_hugetlbfs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_to_hugetlbfs.c

## Purpose
Helper program that reserves, maps, optionally populates, writes, and optionally holds hugetlb memory using hugetlbfs files, anonymous `MAP_HUGETLB`, or SysV shared memory. It supports scenarios needed by hugetlb cgroup charge/reservation tests.

## Important APIs, Types, and Functions
- `enum method` selects `HUGETLBFS`, `MMAP_MAP_HUGETLB`, or `SHM`.
- `exit_usage()` reports accepted flags: path, size, method, sleep, private, populate, write, and no-reserve.
- `sig_handler()` cleans up SysV shared memory on SIGINT.
- `main()` parses options, validates path/size/method, maps using the selected method, optionally `memset()`s the range, and optionally sleeps forever after printing `DONE`.

## Control Flow
After option parsing, the program prints selected behavior. For hugetlbfs it opens/creates the target path and mmaps it. For `MAP_HUGETLB` it maps anonymous or shared huge pages. For SysV SHM it tries key 0 and then key 1, attaches with `shmat()`, and records global cleanup pointers. It writes the range if requested and either exits or holds memory until signaled.

## State and Persistence Behavior
Hugetlbfs mode creates or opens a file at the provided path and maps it. SysV mode creates a shared memory segment and removes it on SIGINT cleanup. Sleep mode intentionally keeps hugepage reservations/charges alive. The program does not unlink hugetlbfs files on normal exit.

## Dependencies and Integration Points
Uses hugetlbfs, `MAP_HUGETLB`, `MAP_POPULATE`, `MAP_NORESERVE`, SysV SHM with `SHM_HUGETLB`, signals, and standard mmap/file APIs. It is invoked by `write_hugetlb_memory.sh` and larger hugetlb accounting tests.

## Risks and Edge Cases
Requires hugepage availability and usually elevated privileges/configuration. The `-r` case formatting is unusual but sets private mode. SysV cleanup is only implemented for SIGINT; other termination paths may leave segments until system cleanup or manual removal. Path length is capped by the fixed 256-byte buffer.

## Test Signals
Prints allocation choices, returned addresses or SHM ids, `Writing to memory`, and `DONE` when holding memory. Failures use `err()`/`perror()` with nonzero exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/write_to_hugetlbfs.c -->
