# sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/mincore_selftest.c

Purpose: validates `mincore()` interface errors and residency reporting for anonymous, huge, file-backed, and tmpfs-backed mappings.

Important APIs/types/functions: uses `mincore`, `mmap`, `mlock`, `munlock`, `madvise(MADV_DONTNEED)`, `MAP_HUGETLB`, `O_TMPFILE`, `fallocate`, kselftest harness macros, and skip handling.

Control flow: `basic_interface` checks zero-length success and documented errors for unmapped address, unaligned address, too-large length, and bad vec. Anonymous test verifies nonresident before touch, resident after touch/lock, and nonresident after unlock plus `MADV_DONTNEED`. Huge-page test skips if huge pages/config unavailable, then repeats touch/residency logic. File-backed test creates an unnamed file in current directory, fallocates 4MB, maps it, expects no initial residency, touches the middle, and validates the touched page plus readahead window. Tmpfs test repeats simpler file residency checks in `/dev/shm`.

State and persistence: temporary unnamed files and mappings only.

Dependencies and integration points: filesystem support for `O_TMPFILE`/`fallocate`, `/dev/shm`, huge page availability for optional coverage.

Risks: readahead expectations are intentionally broad but still environment-sensitive. `mincore(addr, -1, ...)` relies on unsigned length conversion semantics.

Test signals: harness pass/fail/skip per test.
