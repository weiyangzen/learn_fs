# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.c

## Purpose
Implements the io-threads translator, which decouples most filesystem operations from the caller by wrapping them in call stubs and executing them on a dynamically scaled worker pool with per-priority and per-client queues.

## Important APIs, types, and functions
`IOT_FOP()` creates a FOP stub and schedules it. `iot_schedule()` classifies operations into high, normal, low, or least priority. `__iot_enqueue()` and `__iot_dequeue()` maintain per-priority fair queues grouped by client. `iot_worker()` waits on the condition variable, resumes stubs, handles idle exit, and honors shutdown. `__iot_workers_scale()` starts more worker threads based on queued work and configured limits. `iot_getxattr()` has a special `IO_THREADS_QUEUE_SIZE_KEY` path reporting queue depths. `notify()`, `iot_exit_threads()`, `fini()`, and client callbacks handle graph shutdown and disconnected-client cleanup.

## Control flow
Each FOP wrapper creates a `call_stub_t` that resumes the corresponding default child operation on a worker. Scheduling chooses priority by FOP type or forces least priority for ordinary client PIDs when enabled. Enqueue signals one worker and may scale the pool. Workers dequeue respecting active-thread limits per priority and round-robin among clients for fairness, then call `call_resume()` unless the stub is poisoned. Shutdown marks `down`, wakes workers, and waits for `curr_count` to reach zero.

## State and persistence behavior
Runtime state is `iot_conf_t` in `this->private`: mutex/cond, worker counts, queue depths, per-priority active limits, client queue contexts, watchdog settings, atomic queued stub count, and pass-through/cleanup flags. Client-specific queue arrays are stored in client context and freed on client destroy. No durable state is persisted.

## Dependencies and integration points
Depends on Gluster call stubs, default resume/failure callbacks, FOP priority enums, client contexts, atomic counters, pthreads, statedump, option parsing, logging/message IDs, and default event notification. Integrates with io-stats through `IO_THREADS_QUEUE_SIZE_KEY`, with graph teardown via parent/child down notifications, and with clients through disconnect poisoning.

## Risks and test signals
Risks include starvation if priority limits are misconfigured, queue-size/accounting mismatch on poisoned or failed stubs, deadlock during parent-down drain, use-after-free if client contexts are destroyed while queued requests still reference them, watchdog overreaction via `SIGTRAP`, and runtime reconfigure changing limits without waking/scaling enough workers. Tests should cover priority classification, per-client round-robin fairness, worker scale-up/idle scale-down, pass-through startup, queue-size xattr responses, parent/child down cleanup, disconnected-client poisoning, watchdog disabled/enabled behavior, and all FOP wrappers producing the correct default child calls.
