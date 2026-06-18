# sources/distributed-fs/ceph-client/kernel/async.c

## Purpose
`async.c` implements the kernel's asynchronous function call facility used primarily to improve boot performance. It lets initialization code schedule independent work on a dedicated workqueue while preserving externally visible ordering through monotonically increasing cookies and synchronization APIs.

## Important APIs, types, and functions
The core state includes global `next_cookie`, `async_global_pending`, default domain `async_dfl_domain`, `async_lock`, dedicated `async_wq`, waitqueue `async_done`, and `entry_count`. Each `struct async_entry` links into a domain pending list and the global pending list, stores the work item, cookie, callback, data, and domain.

Exported APIs include `async_schedule_node_domain()`, `async_schedule_node()`, `async_schedule_dev_nocall()`, `async_synchronize_full()`, `async_synchronize_full_domain()`, `async_synchronize_cookie_domain()`, `async_synchronize_cookie()`, and `current_is_async()`. `async_init()` allocates the dedicated unbound workqueue and raises its minimum active worker count.

## Control flow
Scheduling allocates an `async_entry`, initializes list and work fields, takes `async_lock`, assigns a cookie, appends to the domain list and possibly the global list, increments the pending count, releases the lock, and queues work on the requested NUMA node. If allocation fails or pending work exceeds `MAX_WORK`, `async_schedule_node_domain()` executes the callback synchronously after still assigning a cookie.

Execution in `async_run_entry_fn()` invokes the callback with data and cookie, logs debug timing, removes the entry from pending lists under lock, frees it, decrements the pending count, and wakes waiters. Synchronization waits until `lowest_in_progress(domain)` is at or beyond the requested cookie; a `NULL` domain means all registered domains through the global pending list.

## State and persistence behavior
All state is in-memory. Cookies are monotonic `async_cookie_t` values and represent ordering checkpoints, not durable IDs. Pending list membership is the source of truth for synchronization. The workqueue exists for the life of the kernel after `async_init()`.

## Dependencies and integration points
This file depends on workqueues, waitqueues, spinlocks, atomics, NUMA-aware `queue_work_node()`, device NUMA helpers, task PID debug output, and `workqueue_internal.h` to identify current worker functions. Boot and driver initialization code integrate by scheduling callbacks and synchronizing before publishing ordered side effects.

## Risks and invariants
The main invariant is that pending-list insertion happens before work can complete, and removal+wakeup happens after callback completion. Cookie ordering must remain consistent even for synchronous fallback. `async_schedule_dev_nocall()` intentionally differs from `async_schedule_dev()`-style behavior by returning false instead of running synchronously, so callers must handle dropped async attempts. Deadlocks are possible if callbacks wait on cookies that include themselves or if domains are misused.

## Test signals
Boot-time initcall ordering tests, driver probe tests using cookies, stress with many scheduled async jobs, allocation-failure injection, NUMA node scheduling smoke tests, and synchronization tests for domain-specific and global waits are relevant. Debug logs showing call and completion cookie order are useful for diagnosing regressions.
