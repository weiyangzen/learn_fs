# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_cap_checkpoint_restore.c

## Purpose

`clone3_cap_checkpoint_restore.c` verifies that `clone3()` `set_tid` requires `CAP_CHECKPOINT_RESTORE` and that this capability works for a non-root process after dropping UID/GID while keeping capabilities. The complete 178-line file was read.

## Important APIs, Types, and Functions

Important helpers are `child_exit()`, `call_clone3_set_tid()`, `test_clone3_set_tid()`, `struct libcap`, and `set_capability()`. The single harness test is `TEST(clone3_cap_checkpoint_restore)`.

## Control Flow

The test verifies clone3 support and root execution, forks once to learn a free PID, sets a capability set containing `CAP_SETUID`, `CAP_SETGID`, and manually-added `CAP_CHECKPOINT_RESTORE`, enables `PR_SET_KEEPCAPS`, drops to UID/GID 65534, verifies `set_tid` fails without effective checkpoint-restore, restores the capability, and verifies the same `set_tid` succeeds.

## State and Persistence Behavior

It changes process capabilities, UID/GID, and keepcaps state inside the test process; it also creates short-lived clone3 children with requested PIDs.

## Dependencies and Integration Points

It depends on libcap, `prctl(PR_SET_KEEPCAPS)`, clone3 `set_tid`, root privileges, kselftest harness, and `clone3_selftests.h`.

## Risks and Edge Cases

The code manually sets capability bit 40 because userspace headers may not expose `CAP_CHECKPOINT_RESTORE`. This is sensitive to libcap internals and capability numbering. PID reuse expectations assume the forked child PID becomes available quickly.

## Test Signals

Pass requires `set_tid` returning `-EPERM` without the effective capability after dropping privileges and returning success after `CAP_CHECKPOINT_RESTORE` is restored.
