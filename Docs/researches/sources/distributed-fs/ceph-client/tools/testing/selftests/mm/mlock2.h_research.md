# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock2.h

## Purpose

`mlock2.h` provides small shared helpers for mlock selftests: a direct `mlock2` syscall wrapper and a `/proc/self/smaps` positioning helper.

## Important APIs, Types, and Functions

`mlock2_()` calls `syscall(__NR_mlock2, start, len, flags)` and returns 0 or -1. `seek_to_smaps_entry()` opens `/proc/self/smaps`, scans VMA header lines, and returns a `FILE *` positioned at the entry containing the requested address.

## Control Flow

The wrapper performs one syscall and maps any nonzero return to `-1`. The smaps helper loops through lines, parses start/end/perms/offset/dev/inode/path fields, and stops once `start <= addr < end`; the caller continues reading subsequent lines for attributes.

## State and Persistence Behavior

The only persistent state is the returned open `FILE *`, which callers must close. The function frees temporary line storage and closes the file when no matching entry is found.

## Dependencies and Integration Points

The header assumes inclusion from kselftest files that provide `ksft_exit_fail_msg()` and standard headers for `size_t`/`strerror()`. It is included by `mlock-random-test.c` and `mlock2-tests.c`.

## Risks and Edge Cases

`mlock2_()` assigns `errno = ret`, but Linux syscall failure returns `-1` and sets errno through libc `syscall()`, so this code can overwrite errno with `-1`. `seek_to_smaps_entry()` has permissive parsing and a fixed `path` buffer, but it only needs address ranges. Returning a file positioned after the header is intentional.

## Test Signals

This header has no standalone tests. Its signals are the correctness of mlock syscall behavior and smaps parsing in the two including tests.
