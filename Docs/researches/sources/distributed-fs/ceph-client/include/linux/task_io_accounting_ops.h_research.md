<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting_ops.h -->
# sources/distributed-fs/ceph-client/include/linux/task_io_accounting_ops.h

## Purpose
provides inline helpers that initialize, increment, convert, and aggregate `struct task_io_accounting` fields.

## Important APIs, Types, and Functions
The file is 115 lines and exports these visible symbol families: types/enums none; macros/constants `__TASK_IO_ACCOUNTING_OPS_INCLUDED`; function-like macros none; inline helpers `task_io_account_read`, `task_io_get_inblock`, `task_io_account_write`, `task_io_get_oublock`, `task_io_account_cancelled_write`, `task_io_accounting_init`, `task_blk_io_accounting_add`, `task_chr_io_accounting_add`, `task_io_accounting_add`; external prototypes none.

## Control Flow
Callers use `task_io_account_read/write/cancelled_write()` against `current`, convert byte counters to 512-byte block counts with `task_io_get_inblock()` and `task_io_get_oublock()`, initialize records, and aggregate character plus block accounting through `task_io_accounting_add()`.

## State and Persistence Behavior
The helpers mutate per-task accounting in `current->ioac` when enabled. Disabled configurations compile to no-op or zero-return helpers, preserving call-site code without collecting state.

## Dependencies and Integration Points
It depends on `linux/sched.h`, `current`, `task_struct`, and the configuration-selected fields from `task_io_accounting.h`. Direct includes are `linux/sched.h`.

## Risks and Edge Cases
Counters are plain increments and rely on appropriate task context; using the helpers for another task without locking is not supported. The block conversion is approximate because it shifts byte counters by nine.

## Test Signals
Compile CONFIG_TASK_IO_ACCOUNTING and CONFIG_TASK_XACCT combinations, run accounting selftests or proc/taskstats checks, and cover aggregation from child to group statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting_ops.h -->
