<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioprio.c -->
# sources/distributed-fs/ceph-client/block/ioprio.c

## Purpose
`ioprio.c` implements the `ioprio_set` and `ioprio_get` system calls and capability validation for process, process-group, and user scoped I/O priorities.

## Important APIs, Types, and Functions
- `ioprio_check_cap()` validates encoded I/O priority class and level and enforces `CAP_SYS_ADMIN` or `CAP_SYS_NICE` for real-time I/O priority.
- `SYSCALL_DEFINE3(ioprio_set, which, who, ioprio)` applies priority to a process, process group, or user’s tasks through `set_task_ioprio()`.
- `SYSCALL_DEFINE2(ioprio_get, which, who)` returns raw process priority or the best effective priority across group/user scopes.
- `get_task_ioprio()` and `get_task_raw_ioprio()` wrap LSM checks and task locking.

## Control Flow
`ioprio_set()` first validates the requested priority. Under RCU, it resolves `which`: current or target pid, current or target pgrp, or current/target uid. Process-group iteration uses `tasklist_lock`; user iteration walks every process/thread and filters by uid and visible pid. Each selected task is updated until an error aborts the operation.

`ioprio_get()` similarly resolves scope. For a single process it returns the raw userspace-set value so callers can distinguish default/unset from an explicit class. For pgrp/user scopes it obtains effective task priorities, skips tasks that fail per-task security checks, and returns the numerically best priority via `min()`.

## State and Persistence Behavior
I/O priority is task/io-context runtime state, not durable storage. The syscalls can allocate or update task `io_context` state through lower-level helpers. User references from `find_user()` are released after iteration.

## Dependencies and Integration Points
The file depends on scheduler task iteration, pid namespaces, credentials/user namespaces, Linux Security Module hooks (`security_task_getioprio` and checks inside setters), capabilities, and block I/O scheduler interpretation of encoded `IOPRIO_*` values. Schedulers such as mq-deadline use request ioprio to select priority classes.

## Risks and Edge Cases
RT priority permission checks intentionally check `CAP_SYS_ADMIN` before `CAP_SYS_NICE` for historical SELinux behavior. `IOPRIO_CLASS_NONE` is valid only with level zero. User namespace uid conversion can fail. Group/user scans under RCU and tasklist locking must avoid use-after-free while still tolerating tasks disappearing. `ioprio_best()` uses numeric minimum, matching encoded-priority ordering assumptions.

## Test Signals
Use syscall tests for all `which` scopes, invalid class/level encodings, RT priority with and without capabilities, uid namespace behavior, raw default priority reads, LSM denial paths, pgrp/user aggregation, and scheduler-visible behavior under mq-deadline or BFQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioprio.c -->
