# sources/distributed-fs/ceph-client/include/linux/hung_task.h

## Purpose
Defines lightweight blocker tracking for hung task diagnostics, encoding the lock pointer and blocking primitive type into `current->blocker`.

## APIs, Control Flow, and State
Blocker type constants use the two low pointer bits for mutex, semaphore, rwsem reader, and rwsem writer. With `CONFIG_DETECT_HUNG_TASK_BLOCKER`, `hung_task_set_blocker()` validates non-null input, warns if a blocker is already set, skips unaligned locks whose low bits are unavailable, and writes `lock_ptr | type` to the current task. `hung_task_clear_blocker()` clears the field. `hung_task_get_blocker_type()` masks the low bits, and `hung_task_blocker_to_lock()` recovers the aligned pointer. Disabled builds are no-ops or return neutral values.

## Dependencies, Integration, Risks, and Tests
Depends on task state in `sched.h`, compiler READ/WRITE_ONCE, and warning helpers. It integrates with locking slow paths that want hung-task reports to identify the contested lock. Risks are missing clear calls, nested blocker writes, lock pointers with low bits set, and reading blocker values without checking zero. Test signals include hung-task diagnostics showing expected lock type, lockdep/hung-task stress, and config builds with blocker tracking disabled.
