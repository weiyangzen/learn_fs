# sources/distributed-fs/glusterfs/libglusterfs/src/syncop.c

## Purpose

`syncop.c` provides Gluster's cooperative synchronous-operation runtime. It implements synctask fibers on top of `ucontext`, a dynamically sized sync processor thread pool, synctask-aware locks, condition variables and barriers, sync operation context setters, and synchronous wrappers around translator FOP callbacks.

## Important APIs, Types, and Functions

Context APIs are `syncopctx_setfsuid()`, `syncopctx_setfsgid()`, `syncopctx_setfsgroups()`, `syncopctx_setfspid()`, and `syncopctx_setfslkowner()`. Synctask APIs include `syncenv_new()`, `syncenv_destroy()`, `synctask_new()`, `synctask_new1()`, `synctask_join()`, `synctask_yield()`, `synctask_sleep()`, `synctask_usleep()`, `synctask_wake()`, and `synctask_setid()`. Synchronization APIs include `synclock_*`, `synccond_*`, and `syncbarrier_*`.

The FOP wrapper surface includes `syncop_lookup`, `readdir`, `readdirp`, `opendir`, `fsyncdir`, xattr operations, `statfs`, `setattr`, `open`, `readv`, `writev`, `write`, `create`, `put`, `unlink`, `rmdir`, `link`, `rename`, `truncate`, `ftruncate`, `fsync`, `flush`, `stat`, `fstat`, symlink/readlink/mknod/mkdir/access, fallocate/discard/zerofill, ipc, seek, lease, locks, xattrop/fxattrop, active lock migration, and copy-file-range helpers.

## Control Flow and Data Flow

Sync environments own run and wait queues plus processor threads. `synctask_create()` allocates a task and stack, creates or reuses a call frame, installs sanitizer/Valgrind fiber metadata when enabled, builds a `ucontext` that starts at `synctask_wrap()`, and wakes the task into the run queue. `__run()` moves a task to the run queue and may create more processor threads up to `procmax`; `syncenv_task()` picks runnable tasks, idles or scales down processors, and exits during destroy once queues drain. `synctask_switchto()` installs task-local state and `THIS`, swaps into the task context, and after yield either reruns the task, moves it to the wait queue, or installs a timer for sleep.

When a synctask yields, `synctask_yield()` stores an optional delay, marks the task suspended unless done, swaps back to the scheduler context, and restores `THIS`. Timed sleeps are implemented by scheduling `synctask_timer()` with `gf_timer_call_after()`. Wakeup cancels pending timers when possible and broadcasts the syncenv condition.

Synclock and synccond bridge fiber and pthread worlds. A lock can be held by either a synctask or a pthread and can be recursive depending on attributes. Synctask waiters yield instead of blocking a processor thread; pthread waiters use pthread condvars. `synccond_timedwait()` releases the supplied synclock around the wait and reacquires it after wake, setting `-ETIMEDOUT` through the task result when timer wake fires.

FOP wrappers use the `SYNCOP` macro from `syncop.h`: initialize `syncargs`, wind the async translator operation, yield until the callback wakes the task, copy callback payloads into caller buffers, manage dict/iobref/iovec references, and convert callback `op_ret/op_errno` into synchronous return values.

## State and Persistence Behavior

Runtime state is in memory: syncenv queues, task stacks, timers, wait queues, TLS syncop context, call frames, copied callback payloads, and references to dicts/iobrefs/inodes/fds. No state is persisted directly by this file. The wrapped FOPs can persist filesystem changes through translators. Context setters update thread-local `syncopctx`; group storage may allocate memory that is cleaned up by thread cleanup hooks.

## Dependencies and Integration Points

The file depends on `ucontext`, pthreads, Gluster timers, call frames from `stack.c`, translator FOP tables, dict/inode/fd/iobref helpers, sanitizer fiber APIs, Valgrind stack registration, `timespec.c`, and `syncop.h` macros. It is a core integration point for code that wants linear synchronous control flow while still using Gluster's asynchronous translator callback model.

## Risks and Edge Cases

`ucontext` and sanitizer fiber switching are portability-sensitive. New synctasks are rejected during syncenv destroy, but tasks already in wait queues must be woken or completed for destruction to finish. Timer cancellation races are handled by checking cancel return values, but task pointers remain sensitive after callbacks. Mixing synctask-aware waits with normal pthread waits requires correct lock ownership; unlocking from the wrong owner logs warnings and may leave state unchanged. Many wrappers return `-op_errno` while a few, such as `syncop_access()` and `syncop_copy_file_range()`, have special return semantics. Dict, iovec, iobref, and lock-list ownership is transferred selectively and callers must unref/free only when they receive ownership.

## Test Signals

Scheduler tests should cover task creation with and without callbacks, blocking joins, sleep/usleep timers, wake-before-sleep, destroy while queues contain work, processor scaling, and sanitizer-enabled builds. Synchronization tests should exercise synctask and pthread lock waiters, recursive locks, timed condition waits, broadcasts, and barriers. FOP wrapper tests can use fake translators to verify callback payload copying, `op_errno` mapping, xdata ownership, dirent copying, readv iovec/iobref ownership, lock-list migration copying, and special access/copy-file-range returns.
