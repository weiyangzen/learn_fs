# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/config

## Purpose
Declares the kernel configuration dependency for syscall user dispatch selftests.

## Important APIs, Types, And Functions
Contains `CONFIG_GENERIC_ENTRY=y`, the infrastructure required by syscall user dispatch entry handling.

## Control Flow
No control flow. The kselftest configuration tooling reads this file to indicate required kernel support.

## State And Persistence
No state.

## Dependencies And Integration Points
Pairs with `sud_test.c` and `sud_benchmark.c`, which call `prctl(PR_SET_SYSCALL_USER_DISPATCH, ...)`.

## Risks
This config is necessary but not a complete guarantee that the runtime architecture supports all tested dispatcher modes or signal-return behavior.

## Test Signals
The requested config appears in the kernel build configuration; runtime tests then confirm actual support.
