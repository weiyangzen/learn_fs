# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/thread-self.c

Purpose: verifies `/proc/thread-self` resolves to `tgid/task/tid` for both the main thread and a cloned thread.

Important APIs and functions: helper `f()` uses `sys_getpid()`, `sys_gettid()`, `readlink`, and string comparison. `main()` uses `mmap` for a stack and `clone(CLONE_THREAD|CLONE_SIGHAND|CLONE_VM)`.

Control flow: validate in the main thread, allocate a stack, clone a side thread that validates and exits the process, then pause in main.

State and persistence: transient stack mapping and thread only.

Dependencies and integration: depends on procfs `thread-self`, raw clone threading semantics, and the shared signal/VM flags used.

Risks and test signals: the child calls `exit(0)`, terminating the process after success. Failure indicates wrong TID/TGID symlink resolution.
