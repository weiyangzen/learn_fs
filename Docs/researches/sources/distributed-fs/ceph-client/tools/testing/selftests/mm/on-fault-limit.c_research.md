# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/on-fault-limit.c

## Purpose

`on-fault-limit.c` verifies that `mlockall(MCL_ONFAULT | MCL_FUTURE)` still respects the process memlock limit when a future `MAP_POPULATE` mapping would fault and lock more memory than allowed.

## Important APIs, Types, and Functions

The test uses `getrlimit(RLIMIT_MEMLOCK)`, `mlockall()`, `mmap(MAP_POPULATE)`, `munmap()`, `munlockall()`, and kselftest helpers. `test_limit()` contains the single behavior check.

## Control Flow

`main()` sets a one-test plan. Root is skipped because privileged locking can bypass the intended limit. Non-root runs `test_limit()`, which enables future on-fault locking and attempts to map twice the hard memlock limit with populate. The expected result is `MAP_FAILED`.

## State and Persistence Behavior

The test sets process-wide mlockall state and clears it with `munlockall()`. If the mapping unexpectedly succeeds, it is unmapped.

## Dependencies and Integration Points

It depends on normal-user execution and kernel support for `MCL_ONFAULT`. It integrates with memlock rlimit enforcement during populate faults.

## Risks and Edge Cases

If `rlim_max` is unlimited or extremely large, the requested mapping can be impractical or overflow size expectations. Running as root always skips. The test checks failure but not a specific `errno`.

## Test Signals

The single pass signal is that the populated mapping fails while future on-fault locking is active.
