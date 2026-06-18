# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mlock-random-test.c

## Purpose

`mlock-random-test.c` randomly exercises `mlock()` and `mlock2(MLOCK_ONFAULT)` on regions inside and outside a reduced `RLIMIT_MEMLOCK`. It validates both successful locking and failure without side effects.

## Important APIs, Types, and Functions

The file uses `setrlimit(RLIMIT_MEMLOCK)`, libcap `cap_set_proc()` to drop `CAP_IPC_LOCK`, `mlock()`, the local `mlock2_()` wrapper, `munlock()`, `/proc/self/status` `VmLck`, and `/proc/self/smaps` `MMUPageSize` through `seek_to_smaps_entry()`. Helpers are `set_cap_limits()`, `get_proc_locked_vm_size()`, `get_proc_page_size()`, `test_mlock_within_limit()`, and `test_mlock_outof_limit()`.

## Control Flow

`main()` drops privileges to a 256 KiB memlock limit, runs a 128 KiB within-limit allocation through 100 random lock ranges, unlocks and frees it, then runs a 384 KiB allocation where randomly chosen lock ranges always exceed the limit and must fail. The within-limit path checks final locked bytes are bounded by aligned allocation size plus a page. The out-of-limit path checks `VmLck` is unchanged after repeated failures.

## State and Persistence Behavior

The process permanently reduces its memlock rlimit and capabilities. Memory comes from `malloc()` and is unlocked/freed between tests. The test reads kernel accounting from `/proc/self/status` and `/proc/self/smaps`.

## Dependencies and Integration Points

It depends on libcap, `mlock2.h`, kselftest, and procfs. It integrates with memory locking accounting and on-fault locking paths.

## Risks and Edge Cases

Random seeds use `time(NULL)` in each test, which can repeat if calls happen in the same second. `mlock2_()` in the header maps syscall return values unusually by assigning `errno = ret`, so negative syscall error handling can be misleading. The test assumes no unrelated locked memory in the process.

## Test Signals

There are two planned results: all random in-limit locks succeed and leave bounded `VmLck`, while all out-of-limit random locks fail and leave `VmLck` unchanged.
