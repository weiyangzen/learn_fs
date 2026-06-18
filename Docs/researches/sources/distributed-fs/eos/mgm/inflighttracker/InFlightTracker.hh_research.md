# sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.hh

## Purpose

`InFlightTracker.hh` defines request admission and accounting primitives for MGM code that needs to know how many requests are currently inside a critical path. It also provides a shutdown barrier: after accepting is disabled, new registrations are refused and callers can spin until all accepted requests have exited.

## Important APIs, Types, and Functions

- `class InFlightTracker` holds the accepting flag, atomic in-flight count, per-thread recursion/request counts, per-thread uid mappings, per-uid counts, and per-uid stall counts.
- `Up(const VirtualIdentity&)` attempts to register the current thread/uid as in-flight and returns false when request acceptance is disabled.
- `Down()` unregisters the current thread and decrements per-thread/per-uid state.
- `SetAcceptingRequests()`, `IsAcceptingRequests()`, `SpinUntilNoRequestsInFlight()`, and `GetInFlight()` form the shutdown barrier surface.
- `getInFlightThreads()`, `getInFlightUids()`, `getInFlight(uid)`, `incStalls(uid)`, and `getStalls(uid)` expose accounting snapshots.
- `getStallTime()`, `PrintOut()`, and `ShouldStall()` are declared here and implemented in the `.cc` file.
- `class InFlightRegistration` is an RAII helper that calls `Up()` in its constructor and `Down()` in its destructor when registration succeeded.

## Control Flow

`Up()` has a carefully documented sequence around `mAcceptingRequests` and `mInFlight`. It first rejects if accepting is already false, increments `mInFlight`, checks accepting again, and rolls back if shutdown won the race. Only after this double-check does it record the current `pthread_t` and uid under `mInFlightPidMutex`. This ensures that once accepting is disabled and `mInFlight` reaches zero, no future request can be admitted without incrementing the counter first.

`Down()` decrements `mInFlight`, asserts non-negative state, locks the maps, decrements the current thread's nested count, and removes thread and uid accounting when the last nested registration exits. It also clears stall counters for a uid when no in-flight request remains for that uid.

`SpinUntilNoRequestsInFlight()` asserts accepting is disabled, repeatedly reads `GetInFlight()`, optionally logs waiting progress, optionally sleeps, and exits only when the count reaches zero.

`InFlightRegistration` packages this protocol for scope-based use. Consumers can check `IsOK()` to reject work that was not admitted.

## State and Persistence Behavior

All state is process-local and in memory. `mAcceptingRequests` and `mInFlight` are atomic. Detailed per-thread and per-uid maps are protected by `mInFlightPidMutex`. No state survives process restart.

The tracker allows nested registrations on the same thread: `mInFlightPids[pthread_self()]` increments on each successful registration, but `mInFlightVids[uid]` increments only when the thread first appears. `mInFlight` increments for every successful `Up()`, so global request count and per-uid/thread maps measure slightly different concepts under nested use.

## Dependencies and Integration Points

The header depends on EOS namespace macros, logging, `VirtualIdentity`, table formatter declarations, atomics, pthread thread IDs, standard maps/sets, and mutexes. It integrates with request-processing code by wrapping request scopes in `InFlightRegistration` and with admission control by using `ShouldStall()`.

## Risks and Edge Cases

- `Down()` uses `mInFlightUid[mythread]` and `mInFlightPids[mythread]`, which default-insert entries if `Down()` is called without a matching successful `Up()` on the same thread. The RAII helper prevents this when used correctly, but direct calls are risky.
- The assertion `mInFlight >= 0` on an atomic relies on signed atomic conversion and is debug-only protection.
- Per-uid counts are incremented only for the first registration per thread, while `mInFlight` increments for nested registrations. That distinction must be understood by callers interpreting user counts.
- `SpinUntilNoRequestsInFlight()` has no timeout or cancellation parameter.
- `pthread_t` as a `std::map` key assumes comparable thread ID semantics for the platform.

## Test Signals

Tests should cover acceptance on/off race behavior, RAII success/failure, nested registration on one thread, multi-thread registration, `SpinUntilNoRequestsInFlight()` after disabling acceptance, direct misuse of `Down()` if supported, per-uid map cleanup, and stall-counter cleanup when uid activity drains.
