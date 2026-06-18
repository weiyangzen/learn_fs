# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma.c

## Purpose
`svc_rdma.c` is the server-side module initialization, teardown, sysctl, and statistics entry point for the RPC/RDMA service transport. It exposes tunables for server RDMA credits and inline request sizing, owns per-CPU service counters, creates the shared `svcrdma` workqueue, and registers/unregisters the server transport class.

## Important APIs, types, and functions
Global tunables include `svcrdma_ord`, `svcrdma_max_requests`, `svcrdma_max_bc_requests`, and `svcrdma_max_req_size`. Per-CPU counters include `svcrdma_stat_read`, `svcrdma_stat_recv`, `svcrdma_stat_sq_starve`, and `svcrdma_stat_write`. `svcrdma_counter_handler()` implements sysctl read/reset behavior for counters. `svc_rdma_proc_init()` initializes counters and registers the `sunrpc/svc_rdma` sysctl table. `svc_rdma_proc_cleanup()` unregisters the table and destroys counters. `svc_rdma_init()` allocates the `svcrdma_wq` workqueue and registers `svc_rdma_class`; `svc_rdma_cleanup()` reverses this.

## Control flow
Module/service startup calls `svc_rdma_init()`. It first allocates an unbound workqueue, then initializes proc/sysctl state. Only after sysctl setup succeeds does it publish `svcrdma_wq` and register the transport class so server listeners can be created. Cleanup unregisters the transport class first to stop new users, tears down proc counters, nulls the global workqueue pointer, and destroys the old workqueue.

## State and persistence behavior
State is kernel runtime state only. Tunables live in global variables and are exposed through sysctl while the module is active. Counters are per-CPU and can be reset by writing to their sysctl entries. `svcrdma_wq` is a global workqueue used by later async cleanup paths in send and RW code. There is no disk persistence.

## Dependencies and integration points
The file depends on Linux sysctl, per-CPU counters, workqueues, and SunRPC service transport registration. It references `svc_rdma_class` from the transport implementation and is used by `svc_rdma_rw.c` and `svc_rdma_sendto.c` through the exported `svcrdma_wq` and counters. The tunables feed listener/connection setup in `svc_rdma_transport.c`.

## Risks and edge cases
Initialization order matters: `svcrdma_wq` must not be visible before sysctl setup succeeds. Error unwind in `svc_rdma_proc_init()` must destroy only counters that were initialized. Counter sysctl reads use a fixed buffer sized for unsigned long long text and return `-EFAULT` if formatting overflows. Cleanup must handle partially initialized module state and avoid destroying a NULL workqueue.

## Test signals
Tests should check module init/cleanup under allocation failures, sysctl min/max enforcement, counter reset-by-write behavior, transport class registration presence, and use-after-free absence when async work is queued before cleanup. Runtime signals are `svcrdma_stat_*` counters, debug prints, and registration failures from `svc_rdma_init()`.
