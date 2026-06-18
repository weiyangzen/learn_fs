# sources/distributed-fs/ceph-client/include/linux/sunrpc/sched.h

Purpose: declares the SUNRPC task scheduler, wait queues, timeout strategy, call callback interface, and rpciod/xprtiod workqueue hooks.

Important APIs and types: `struct rpc_message` carries procedure, args, response, and credentials. `struct rpc_timeout` defines initial/max/increment/retry/exponential behavior. `struct rpc_task` is the central asynchronous/synchronous RPC state machine with refcount, status, callbacks/actions, runstate bits, wait/work union, message, client, transport, request, workqueue, owner, retry counters, flags, and priority. `struct rpc_call_ops` provides prepare/done/stats/release callbacks. `struct rpc_task_setup` configures new tasks. `struct rpc_wait_queue` implements priority wait queues and timer lists.

Control flow: callers create or run tasks, scheduler actions sleep tasks on wait queues, timers wake or fail them, transports set send/receive runstate bits, and completion invokes callbacks before releasing calldata.

State and persistence: tasks and wait queues are runtime state. Workqueues `rpciod_workqueue` and `xprtiod_workqueue` execute async work; no state persists beyond client/task lifetime.

Dependencies and integration points: integrates timers, ktime, wait-bit, workqueues, spinlocks, RPC XDR, client/transport/auth code, and optional swap-over-NFS support.

Risks and test signals: risks include task refcount leaks, wakeup races, priority starvation, timeout policy mismatches, cancellation status races, and workqueue shutdown ordering. Test with async/sync RPC, soft/hard timeouts, signal interruption, cancellation, high-priority tasks, swap activation, and debug task dumps.
