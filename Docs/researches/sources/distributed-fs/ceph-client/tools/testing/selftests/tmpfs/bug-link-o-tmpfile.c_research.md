# sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/bug-link-o-tmpfile.c

## Purpose
This tmpfs regression test verifies that linking an `O_TMPFILE` inode into a tiny tmpfs mount does not corrupt inode accounting. It specifically exercises creating an anonymous tmpfile, linking it, and then creating another anonymous tmpfile when the mount has only three inodes.

## Important APIs, Types, and Functions
The program uses `unshare(CLONE_NEWNS)`, `mount(MS_PRIVATE|MS_REC)`, `mount(..., "tmpfs", ..., "nr_inodes=3")`, `openat(..., O_TMPFILE)`, and `linkat(..., AT_EMPTY_PATH)`. It reports through `kselftest.h`.

## Control Flow
`main()` sets a one-test plan, skips unless running as root, creates a private mount namespace, makes `/` private, mounts a constrained tmpfs on `/tmp`, opens one `O_TMPFILE`, links it to `/tmp/1`, closes it, opens a second `O_TMPFILE`, and passes if that succeeds.

## State and Persistence
The test mutates the process mount namespace and mounts tmpfs over `/tmp`. Because it unshares the mount namespace first, the mount changes should not leak to the parent namespace. File descriptors are closed on normal paths.

## Dependencies and Integration Points
It requires root, mount namespace support, tmpfs, anonymous tmpfile support, `AT_EMPTY_PATH`, and kselftest reporting.

## Risks
If `unshare()` fails due to missing support or permission it skips on expected errors. Running without a private namespace would make `/tmp` mount changes dangerous, but the test fails before mount if namespace setup fails unexpectedly. The `linkat()` failure path calls `ksft_exit_fail_msg()` before a close statement that is effectively unreachable.

## Test Signals
Pass means tmpfs inode accounting allows the second anonymous tmpfile after the first is linked, with one root inode, one permanent inode, and one tmpfile inode. Failure points to tmpfs `O_TMPFILE`/link accounting regressions.
