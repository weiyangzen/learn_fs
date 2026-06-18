<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.c -->
# sources/distributed-fs/ceph-client/security/landlock/tsync.c

## Purpose

`tsync.c` implements Landlock's cross-thread synchronization path for `LANDLOCK_RESTRICT_SELF_TSYNC`. It updates sibling threads in the current thread group to the same tentative Landlock credentials with all-or-nothing semantics, using task work callbacks and completion barriers rather than directly modifying another task's credentials.

## Important APIs, Types, and Functions

- `landlock_restrict_sibling_threads()` is the exported internal entry point called by `landlock_restrict_self`.
- `struct tsync_shared_context` coordinates old/new credentials, no-new-privs propagation, preparation errors, and preparation/commit completion barriers.
- `struct tsync_work` carries per-task `task_work` state and a task reference.
- `restrict_one_thread()` prepares or reuses credentials in each sibling, waits for the global commit/abort decision, sets `no_new_privs` when needed, and commits or aborts.
- `tsync_works_grow_by()`, `tsync_works_provide()`, `tsync_works_trim()`, and `tsync_works_release()` manage a growable preallocated work array.
- `count_additional_threads()`, `schedule_task_work()`, and `cancel_tsync_works()` discover, schedule, and opportunistically cancel sibling task work.

## Control Flow

The initiating thread tries to take `current->signal->exec_update_lock` with `down_write_trylock()`. If another TSYNC or exec-style update owns it, the syscall is restarted so pending task work can run. The function then repeatedly counts sibling threads not yet scheduled, grows the work array, schedules a signaled `task_work` on each newly discovered non-exiting sibling, and waits until all scheduled siblings have reached the preparation barrier.

Each sibling callback either reuses the caller's prepared `new_cred` when it still has `old_cred`, or allocates fresh credentials and copies the Landlock credential blob. Any allocation failure records an atomic preparation error but still follows the barrier protocol. After all discovered threads are prepared and no further unscheduled siblings remain, the caller completes `ready_to_commit`; all callbacks either commit credentials or abort based on the shared error, then signal `all_finished`.

If the caller is interrupted while waiting for preparation, it stores `-ERESTARTNOINTR`, tries to cancel queued task work that has not run, and still releases all in-flight callbacks through the commit/abort barrier before returning.

## State and Persistence Behavior

All synchronization state is stack-local to `landlock_restrict_sibling_threads()` except referenced task and credential objects. The shared context uses atomics and completions for phase transitions. The persistent effect, on success, is that every participating sibling commits credentials containing the new Landlock domain and possibly `no_new_privs`. On failure, every prepared credential is aborted and the caller later aborts its own pending credentials in `sys_landlock_restrict_self()`.

## Dependencies and Integration Points

This file depends on the credential API, task iteration under RCU, `task_work_add()`/`task_work_cancel()`, completions, atomics, `exec_update_lock`, and Landlock credential-copy helpers. It is integrated only through `tsync.h` and the restrict-self syscall path.

## Risks and Edge Cases

Thread creation races are handled by looping until no new siblings are found, but this relies on scheduled siblings being unable to spawn new threads while blocked in task work. The preallocation logic must keep task references and work slots consistent across races with exiting tasks. Deadlock avoidance depends on restarting instead of blocking when `exec_update_lock` is already held. A failure in any sibling must abort all siblings, so barrier counters and cancellation paths are security-critical.

## Test Signals

Tests should create multithreaded processes that enforce Landlock with TSYNC while threads are creating more threads, exiting, blocking in syscalls, or racing another TSYNC call. Signals interrupting the caller should return restartable errors without partial enforcement. Observing all threads' Landlock status after success and no thread changed after injected allocation/task-work failure are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.c -->
