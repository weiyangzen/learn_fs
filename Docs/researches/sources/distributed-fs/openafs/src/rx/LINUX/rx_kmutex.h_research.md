# sources/distributed-fs/openafs/src/rx/LINUX/rx_kmutex.h

Purpose: Linux declarations/macros for Rx kernel mutexes and condition variables.

Important APIs/types/functions: `struct afs_kmutex` with `struct mutex` and owner pid; `struct afs_kcondvar` with sequence and `wait_queue_head_t`; `MUTEX_*`, `CV_*`, `CV_WAIT`, and `CV_WAIT_SIG` macros.

Control flow: macro calls route to implementation functions in `rx_kmutex.c`; signal and broadcast increment the CV sequence and wake one/all waiters.

State/persistence: no global state; types define per-lock and per-CV runtime state.

Dependencies/integration: Linux version, wait, sched, mutex headers, coda inode workaround, and OpenAFS Rx kernel panic/assert infrastructure.

Risks: casts between `struct iovec`/`struct kvec` in networking depend on compatible layout but this header only sets sync primitives; kernel API compatibility macros can rot. Test signals are Linux kernel module compilation across supported versions and lock/CV behavior tests.
