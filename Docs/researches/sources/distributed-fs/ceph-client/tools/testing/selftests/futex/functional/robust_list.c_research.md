<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/robust_list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/robust_list.c

## Purpose
This kselftest validates the robust futex list ABI, including owner-death wakeups, list registration size validation, `get_robust_list()`, pending operations, multiple list elements, and circular list handling.

## Important APIs, Types, And Functions
Important functions are `set_robust_list()`, `get_robust_list()`, `create_child()`, `set_list()`, `mutex_lock()`, `child_fn_lock()`, `child_list()`, `child_fn_lock_with_error()`, `child_lock_holder()`, `child_wait_lock()`, and `child_circular_list()`. Important types are `struct lock_struct` and `struct robust_list_head`.

## Control Flow
Tests clone child tasks sharing VM, register robust lists, have children exit while holding futexes, and verify waiters wake with `FUTEX_OWNER_DIED`. Other tests validate exact `set_robust_list()` size, self and child `get_robust_list()`, `list_op_pending` owner death, multiple held locks waking multiple waiters, and kernel handling of circular robust lists.

## State And Persistence
State is shared process memory, robust list head pointers registered with the kernel per thread, clone stacks, barriers, and futex words. Kernel robust-list registration persists per thread until replaced or thread exit.

## Dependencies And Integration Points
It depends on `SYS_set_robust_list`, `SYS_get_robust_list`, clone with `CLONE_VM`, robust futex ABI structures from Linux headers, pthread barriers, and kselftest harness.

## Risks
The test uses handmade robust mutex logic that is intentionally incomplete; it only validates ABI behavior. Race avoidance relies on barriers plus short sleeps before child death. Some child cleanup paths can leak mmaped stacks.

## Test Signals
Pass signals include `FUTEX_OWNER_DIED` set after owner death, `EINVAL` for invalid robust-list sizes, correct robust-list pointer returned for self/child, pending-op death handled, all multiple waiters waking, and circular list child exiting without kernel hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/robust_list.c -->
