# sources/distributed-fs/ceph-client/kernel/exit.h

Purpose: private header for the kernel exit/wait implementation. It defines the data structures used to pass wait options and wait results between syscall wrappers and shared wait helpers.

Important APIs/types/functions: `struct waitid_info` carries pid, uid, status, and cause fields for `siginfo`-style wait results. `struct wait_opts` carries PID selection, flags, optional result destinations, waitqueue entry, and `notask_error`. Declarations expose `pid_child_should_wake()`, `__do_wait()`, and `kernel_waitid_prepare()`.

Control flow: wait syscall entry points fill `wait_opts` directly or through `kernel_waitid_prepare()`, then pass it into `do_wait()`/`__do_wait()`. The child waitqueue callback uses `pid_child_should_wake()` to filter wakeups.

State and persistence: the header owns no storage. Instances are caller-owned, typically stack-allocated, and `child_wait` is temporarily linked into `current->signal->wait_chldexit`.

Dependencies and integration points: depends on pid types, `struct pid`, `struct rusage`, wait queues, task structs, and UAPI wait constants. It bridges syscall and core wait scanner code.

Risks: `wo_pid` reference ownership, nullable output pointers, and `notask_error` semantics are easy to misuse. Incorrect flag or PID-type initialization changes visible wait behavior.

Test signals: broad compile and behavioral coverage comes through `wait4()`, `waitid()`, pidfd waits, option validation, and child wake filtering tests.
