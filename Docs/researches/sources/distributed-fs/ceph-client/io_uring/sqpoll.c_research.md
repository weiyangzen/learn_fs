# sources/distributed-fs/ceph-client/io_uring/sqpoll.c

Purpose: implements submission-queue polling, where a kernel thread watches one or more rings and submits SQEs on behalf of userspace.

Important APIs/types/functions: `io_sq_data` is defined in the header. Public functions include `io_sq_offload_create()`, `io_sq_thread_finish()`, `io_sq_thread_stop()`, `io_sq_thread_park()`, `io_sq_thread_unpark()`, `io_put_sq_data()`, `io_sqpoll_wait_sq()`, `io_sqpoll_wq_cpu_affinity()`, and `io_sq_cpu_usec()`. Internal `io_sq_thread()` is the kernel-thread loop.

Control flow: setup validates attach/fd/capability/security, creates or attaches `io_sq_data`, records credentials and idle timeout, optionally validates CPU affinity, creates an io thread, allocates that thread's io_uring task context, and wakes it. The thread loops over attached contexts, caps submit count when sharing, overrides credentials, polls IOPOLL completions, submits SQEs unless refs are dying or ring disabled, runs task_work with a retry cap, does NAPI busy polling, then sleeps with `IORING_SQ_NEED_WAKEUP` set when idle. Park/stop coordinate via state bits, waitqueues, completions, and `park_pending`.

State and persistence: state persists while rings use SQPOLL: shared `io_sq_data`, thread pointer, ctx list, refcount, park/stop bits, CPU, task pid/tgid, idle timeout, work-time accounting, and captured submitter creds in each ctx.

Dependencies/integration: integrates with security hooks, cpusets, io thread creation, io-wq task contexts, SQ ring submit, IOPOLL, NAPI, cancellation, audit, registered attach fd, and ring teardown.

Risks/test signals: risks include park/unpark ref races, attaching to a dying thread, credential override errors, affinity validation, fairness across multiple rings, and wakeup flag ordering. Test SQPOLL creation/teardown, attach WQ, CPU affinity, disabled rings, shared rings, IOPOLL under SQPOLL, cancellation on exit, and fdinfo work-time accounting.
