# sources/distributed-fs/ceph-client/io_uring/waitid.c

Purpose: provides async io_uring support for `waitid`, allowing child-state waits to arm a waitqueue and complete through task_work.

Important APIs/types/functions: `struct io_waitid` stores wait parameters, refs/cancel flag, waitqueue head, user siginfo pointer, and result info. `struct io_waitid_async` is declared in the header. Entry points are `io_waitid_prep()`, `io_waitid()`, `io_waitid_cancel()`, and `io_waitid_remove_all()`.

Control flow: prep allocates async wait options and captures `which`, pid, options, and siginfo pointer. Issue prepares kernel wait options, sets an initial ref, adds the request to `ctx->waitid_list`, arms `current->signal->wait_chldexit`, and calls `__do_wait()`. If it returns `-ERESTARTSYS`, the request remains armed until the wait callback queues task_work or cancellation completes it. Task_work retries `__do_wait()`, handles spurious wakeups by rearming, copies siginfo in native or compat layout, removes waitqueue/list state, drops pid refs, and completes.

State and persistence: transient state includes child waitqueue entry, wait options pid ref, cancel/ref bits, waitid cancel hlist entry, and copied `waitid_info`. Userspace siginfo is updated on completion.

Dependencies/integration: depends on kernel wait/exit internals, compat siginfo layout, io_uring cancellation helpers, task_work, ring submit lock, and request async data lifetime.

Risks/test signals: risks are cancellation/wakeup ref races, waitqueue removal under concurrent child exit, compat siginfo copy faults, pid ref leaks, and task-specific cancellation. Test immediate child reap, async child exit, cancellation by user_data/task exit, compat mode, null siginfo, spurious wake/rearm, and faulted siginfo pointer.
