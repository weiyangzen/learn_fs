# sources/distributed-fs/ceph/src/rgw/rgw_coroutine.h

## Purpose
`rgw_coroutine.h` declares the cooperative coroutine framework used by RGW asynchronous services. It defines the scheduler-facing abstractions for coroutines, stacks, completion notifications, manager registries, consumer coroutines, and a simple request coroutine base class.

## Important APIs, Types, And Functions
`RGWCompletionManager` exposes completion queue operations and timer wakeups. `RGWAioCompletionNotifier` and `RGWAioCompletionNotifierWith<T>` adapt librados completions to that queue.

`RGWCoroutinesEnv` carries the active run context, manager, scheduled stack list, and current stack. `RGWCoroutineState` defines run/done/error states. `rgw_spawned_stacks` tracks child stacks that must be collected.

`RGWCoroutine` derives from `RefCountedObject` and `boost::asio::coroutine`. Subclasses implement `operate()`. The base class provides status/history reporting, error logging, `call()`, `spawn()`, `collect()`, `collect_next()`, `wait()`, child draining helpers, sleep/wakeup, IO blocking/completion, and IO provider initialization. Macros such as `yield_until_true`, `drain_all`, and `yield_spawn_window` encode common Boost.Asio coroutine patterns.

`RGWConsumerCR<T>` is a coroutine with an in-memory product queue and wakeup-on-receive behavior. `RGWCoroutinesStack` is the executable stack of coroutine calls plus child-stack and IO-blocking state. `RGWCoroutinesManagerRegistry` tracks active managers and implements `AdminSocketHook`. `RGWCoroutinesManager` owns completion management, run contexts, IO/stack id providers, scheduling, notifier creation, and stack allocation. `RGWSimpleCoroutine` is a base for one-shot async requests with init/send/complete/finish/cleanup hooks.

## Control Flow
Subclasses generally use Boost.Asio `reenter/yield` macros in `operate()`. A coroutine can yield on `io_block()`, wait on child completion through drain macros, or sleep until another component calls `receive()` or `wakeup()`. The stack and manager track whether the coroutine is runnable, IO-blocked, sleeping, blocked by a child stack, or waiting for any child to complete.

## State And Persistence Behavior
All declared state is transient scheduler state. Status history stores the last ten status strings by default for diagnostics. Stacks own lists of coroutine pointers and spawned stack refs. Managers own active run contexts and id counters. No data is persisted across process restarts.

## Dependencies And Integration Points
The header depends on Boost.Asio coroutine support, Ceph refcounting, timers, admin socket, debug locks, `rgw_common.h`, and `rgw_http_client_types.h` for IO identifiers/providers. It is inherited by many RGW async RADOS, REST, metadata, and service coroutines.

## Risks And Edge Cases
The framework exposes raw pointers and intrusive refs, so caller ownership discipline is central. Macros hide control flow and require callers to understand Boost coroutine reentry semantics. Child draining callbacks can request exit but still drain remaining children. IO id masks allow completion before blocking and channel-specific unblocking, which is powerful but easy to misuse. `RGWConsumerCR` stores products unboundedly unless producers/consumers apply backpressure.

## Test Signals
Header-level test signals include subclass compile coverage, coroutine macro behavior in representative subclasses, status dump history, consumer receive/wakeup behavior, IO provider id assignment, child-drain callbacks, and admin registry add/remove lifetime behavior.
