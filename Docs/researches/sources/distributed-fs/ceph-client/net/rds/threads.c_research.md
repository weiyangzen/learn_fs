# sources/distributed-fs/ceph-client/net/rds/threads.c

## Purpose
Provides the shared RDS workqueue and worker functions that serialize connection management, send retry, receive retry, shutdown, reconnect backoff, and address ordering.

## Important APIs, Types, and Functions
Defines exported `struct workqueue_struct *rds_wq`, `rds_connect_path_complete()`, `rds_connect_complete()`, and `rds_addr_cmp()`. Worker functions are `rds_connect_worker()`, `rds_send_worker()`, `rds_recv_worker()`, and `rds_shutdown_worker()`. Init/exit are `rds_threads_init()` and `rds_threads_exit()`. Reconnect scheduling is handled by `rds_queue_reconnect()`.

## Control Flow
Successful connect transitions a path to `RDS_CONN_UP`, queues congestion map send and receive work, clears reconnect delay, and resets protocol proposal state. Reconnect scheduling uses an initial immediate attempt followed by randomized exponential backoff capped by sysctl max, while TCP peers with the larger address defer initiation to avoid dueling connects. Send and receive workers only run while the path is up, invoke transport callbacks, and reschedule immediately for `-EAGAIN` or after a short delay for `-ENOMEM`. The shutdown worker delegates to `rds_conn_shutdown()`.

## State and Persistence
State lives in per-path delayed works, `cp_state`, `cp_flags`, `cp_reconnect_jiffies`, and global `rds_wq`. No durable persistence is used.

## Dependencies and Integration
Depends on RDS connection state helpers, transport callback tables, sysctl reconnect values, random bytes, RCU destroy-pending checks, and the singlethread workqueue named `krdsd`.

## Risks and Test Signals
Risks include reconnect livelock, workqueue serialization bottlenecks, address-comparison asymmetry across architectures, and missed retries if destroy-pending races are mishandled. Test signals are transition coverage for DOWN/CONNECTING/UP/DISCONNECTING/ERROR, randomized reconnect delay growth, TCP address-order deferral, send/recv retry stats, and correct IPv6 comparison for both aligned 64-bit and fallback 32-bit paths.
