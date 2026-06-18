# sources/distributed-fs/ceph-client/lib/is_single_threaded.c

Purpose: implements `current_is_single_threaded()`, which decides whether the current task is the only live user of its `mm_struct` across the system.

Important API: `current_is_single_threaded()` returns false if the thread group has multiple live threads, true if `mm_users == 1`, otherwise scans processes and threads for another task sharing the same `mm`.

Control flow: first checks `signal->live`, then fast-paths `mm_users == 1`, then performs an RCU-protected walk over all processes. It skips kernel threads and the current group leader, scans threads for `t->mm == mm`, and uses `smp_rmb()` when seeing `NULL` mm to order against concurrent CLONE_VM/exiting transitions.

State and persistence: reads scheduler/task/mm reference counters and task lists; no mutation.

Dependencies and integration: depends on scheduler signal/task/mm headers, RCU task traversal, and memory barriers. Security and process-management code can use it before operations requiring private address-space ownership.

Risks: correctness depends on subtle task-list and mm lifetime ordering; the full process scan is expensive; `current->mm` must be valid for callers; racing clone/exit paths rely on the documented barrier.

Test signals: fork/clone/thread stress tests, SELinux or credential-changing paths that require single-thread checks, and lockdep/RCU validation.
