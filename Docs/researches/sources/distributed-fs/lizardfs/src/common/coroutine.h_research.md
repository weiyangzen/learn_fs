# sources/distributed-fs/lizardfs/src/common/coroutine.h

Purpose: provides stackless coroutine macros adapted from Boost.Asio-style coroutine support.

Important APIs/types/functions: `coroutine` stores an integer continuation value and reports parent/child/complete state. `detail::coroutine_ref` updates the stored state and marks coroutines complete when a reenter block exits without modification. Macros `CORO_REENTER`, `CORO_YIELD`, `CORO_FORK`, and aliases `reenter`/`yield` implement switch/goto-based suspension.

Control flow: user code wraps a stateful function body in `reenter(c)`, where `yield` stores a unique line/counter value and returns to the caller. Re-entry switches back to that case label. `fork` stores negative continuation values to distinguish child and parent flows.

State and persistence: state is a single integer in a `coroutine` object; no heap, no persistence, no thread safety.

Dependencies and integration: only depends on `platform.h`. It is meant for event-driven code that needs resumable logic without C++20 coroutines.

Risks: macro control flow is fragile: yields must not share line numbers on non-MSVC builds, scopes/cases can surprise users, and normal C++ lifetime rules around local variables crossing yields require care. It is not exception-aware beyond RAII of `coroutine_ref`.

Test signals: no direct test in this group; the code is a known pattern but should be exercised by users that depend on resumable protocol state machines.
