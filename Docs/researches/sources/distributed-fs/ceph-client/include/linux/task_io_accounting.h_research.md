<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting.h -->
# sources/distributed-fs/ceph-client/include/linux/task_io_accounting.h

## Purpose
defines the per-task I/O accounting record embedded in `task_struct` when extended accounting options are enabled.

## Important APIs, Types, and Functions
The file is 47 lines and exports these visible symbol families: types/enums `task_io_accounting`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Accounting helpers increment character I/O counters (`rchar`, `wchar`, `syscr`, `syscw`) and block I/O counters (`read_bytes`, `write_bytes`, `cancelled_write_bytes`) as syscalls and storage operations proceed. Exit/accounting paths aggregate these fields into taskstats and process summaries.

## State and Persistence Behavior
The structure is persistent for the lifetime of a task. Fields compile in only under CONFIG_TASK_XACCT and CONFIG_TASK_IO_ACCOUNTING, so consumers must tolerate absent or zeroed counters in smaller configurations.

## Dependencies and Integration Points
It is intentionally included through scheduler headers and depends on kernel integer types already available there. Direct includes are none.

## Risks and Edge Cases
Configuration-dependent layout and semantics are the main concern. Cancelled writes are not negative write bytes, and block counters represent bytes caused rather than necessarily completed by the task.

## Test Signals
Build all relevant config combinations, compare `/proc/<pid>/io` and taskstats values with known read/write/truncate workloads, and verify fork/exit aggregation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/task_io_accounting.h -->
