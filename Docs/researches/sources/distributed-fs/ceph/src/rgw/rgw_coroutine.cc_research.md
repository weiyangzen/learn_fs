# sources/distributed-fs/ceph/src/rgw/rgw_coroutine.cc

## Purpose
`rgw_coroutine.cc` implements RGW's cooperative coroutine scheduler and completion bridge. It coordinates stacks of `RGWCoroutine` operations, child stack spawning/collection, asynchronous RADOS completion notifications, timer wakeups, admin-socket dumps, deadlock detection, and the `RGWSimpleCoroutine` request lifecycle helper.

## Important APIs, Types, And Functions
`RGWCompletionManager` owns a completion queue, a set of active `RGWAioCompletionNotifier`s, a timer, and waiter mapping. `complete()`, `get_next()`, `try_get_next()`, `wait_interval()`, `wakeup()`, and `go_down()` coordinate IO/timer completions with scheduler wakeups.

`RGWAioCompletionNotifier` wraps a single librados `AioCompletion`. Its callback unregisters itself, completes the associated stack through `RGWCompletionManager`, and balances intrusive references.

`RGWCoroutinesStack::operate()` runs the current coroutine, unwinds finished calls, propagates retcodes, and marks done/error states. `spawn()`, `collect()`, `collect_next()`, `wait()`, `io_complete()`, `try_io_unblock()`, and `consume_io_finish()` manage child stacks and IO completion masks.

`RGWCoroutinesManager::run()` is the main scheduler loop. It tracks a run context, scheduled stacks, blocked counts, interval-wait counts, and completion events. It reschedules runnable stacks, waits when too many real IOs are outstanding (`ops_window`), unblocks dependent stacks, cancels on shutdown, and asserts if stacks remain with no progress.

`RGWCoroutinesManagerRegistry` publishes scheduler state through the admin socket. `RGWSimpleCoroutine` provides a template state machine: `init()`, `send_request()`, wait for IO, `request_complete()`, optional retry for `-ERR_INTERNAL_ERROR`, `finish()`, drain children, and cleanup.

## Control Flow
Callers allocate a manager and run either a single coroutine or a list of stacks. A coroutine can `call()` another coroutine on the same stack, `spawn()` a child stack, `wait()` on a timer, or `io_block()` until its assigned IO id completes. The manager repeatedly pops scheduled stacks, runs one coroutine step, records whether the stack is done, blocked, sleeping, or runnable, then drains queued completions. Completion events carry a `user_info` pointer to the stack and an `rgw_io_id`; masks that do not match the current blocked id are stored for later consumption.

`drain_children()` is itself a boost coroutine state machine. It yields until children finish, calls `collect()`, records errors in the coroutine error stream, and optionally lets callbacks force an exit after all children are drained.

## State And Persistence Behavior
All state is in-memory process state. There is no persistent storage. Correctness depends on intrusive reference counts on coroutines, stacks, notifiers, completion managers, and registries. The manager's `run_contexts` map exists for active scheduler runs and admin dumps only.

## Dependencies And Integration Points
The implementation depends on Boost.Asio coroutine macros, librados AIO completions, Ceph `SafeTimer`, admin socket hooks, Ceph locks/condition variables, debug formatting, and `rgw_asio_thread` blocking warnings. It is used by RGW RADOS coroutine code, REST replication/resource coroutines, metadata log services, admin operations, and SAL drivers with coroutine registry support.

## Risks And Edge Cases
Reference-counting and cancellation are high risk: notifiers call `get()`/`put()` around callbacks and destructors unregister under locks. `RGWCompletionManager::_complete()` checks `complete_reqs_set` but does not insert into it in the shown implementation, so duplicate suppression depends on behavior outside this set or may be incomplete. Deadlock detection asserts if no scheduled or blocked progress remains while context stacks still exist. Blocked counters must stay balanced when stacks are interval waits versus real IO waits. Raw `void*` stack pointers in completion user data require stack lifetime to be protected by scheduler references.

## Test Signals
Tests should cover single coroutine completion, nested `call()` unwind, child `spawn()` with wait and collect, IO completion before and after `io_block()`, completion masks/channels, interval wait wakeup, shutdown cancellation, admin dump output, deadlock detection scenarios, and `RGWSimpleCoroutine` retry/cleanup semantics.
