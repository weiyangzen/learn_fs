# sources/distributed-fs/ceph-client/arch/um/os-Linux/helper.c

## Purpose
Runs external helper programs and helper threads while respecting UML allocation/signal constraints.

## Important APIs, Types, and Functions
`run_helper()` clones a child with a small allocated stack, optionally runs a pre-exec callback, calls `execvp_noalloc()`, and reports exec errno through a close-on-exec socketpair. `run_helper_thread()` runs a clone child with optional stack ownership. `helper_wait()` validates exit status. `os_run_helper_thread()`/`os_kill_helper_thread()` manage pthread helpers. `os_fix_helper_thread_signals()` masks UML signals in helper threads.

## Control Flow, State, and Persistence
State is transient per helper: allocated stack, socketpair, PID or pthread handle, and a PATH buffer. Pthread helper descriptors persist until killed/joined.

## Dependencies and Integration Points
Used by SIGIO workaround threads, host command helpers, and callbacks that need execution on the initial thread. Depends on `alloc_stack()`, `execvp_noalloc()`, signal masking, pthreads, clone, and `um_malloc`.

## Risks and Test Signals
Risks are stack leaks, exec errno races, helper thread signal handling, and using `CLONE_VM` in the wrong API. Test successful/missing helpers, pre-exec callbacks, cancellation cleanup, signal storms, and atomic allocation contexts.
