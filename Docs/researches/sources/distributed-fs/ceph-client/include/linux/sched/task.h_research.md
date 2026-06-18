# sources/distributed-fs/ceph-client/include/linux/sched/task.h

Purpose: declares task lifetime, fork/clone, exit, wait, task reference, initial task, tasklist locking, and task allocation/stack interfaces.

Important APIs and types: `CLONE_LEGACY_FLAGS`, `struct kernel_clone_args`, `tasklist_lock`, `mmlist_lock`, `init_thread_union`, `init_task`, `schedule_tail()`, scheduler fork hooks, `do_task_dead()`, `make_task_dead()`, cache init, `release_task()`, `copy_thread()`, `do_group_exit()`, `kernel_clone()`, `copy_process()`, `create_io_thread()`, `fork_idle()`, `kernel_thread()`, `user_mode_thread()`, wait helpers, task refcount helpers, `release_thread()`, `task_stack_vm_area()`, and `task_lock()` are central.

Control flow: clone/fork code fills `kernel_clone_args`, creates/copies tasks, calls scheduler and architecture hooks, publishes tasks under tasklist locking, and releases resources on exit. References are acquired with `get_task_struct()` and dropped through RCU-delayed freeing when needed.

State and persistence: state includes task references, global task list, initial task, kernel stacks, task caches, and per-task resources protected by `alloc_lock`. It lasts for task lifetime and RCU grace periods after final put.

Dependencies and integration points: integrates scheduler with fork/exit, MM, files/fs, cgroups, architecture thread setup, wait/rusage, RCU, and procfs locking.

Risks and test signals: risks include clone flag ABI mistakes, task refcount underflow, freeing in atomic/RT contexts, tasklist lock nesting violations, and resource leaks on fork failure. Test fork/clone variants, io threads, kernel threads, wait4, exit races, RCU ref users, PREEMPT_RT, and lockdep.
