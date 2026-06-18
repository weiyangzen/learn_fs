# sources/distributed-fs/ceph-client/rust/proc-macro2/detection.rs

## Purpose
`detection.rs` determines whether the compiler's real `proc_macro` API is available in the current context. `proc-macro2` uses this to choose between compiler-backed and fallback token implementations.

## Important APIs, Types, And Functions
`inside_proc_macro() -> bool` is the main query. `force_fallback()` stores a forced-fallback state. `unforce_fallback()` reruns detection. `WORKS: AtomicUsize` stores unknown/false/true as `0/1/2`, and `INIT: Once` ensures detection happens once in normal operation. `initialize()` has two cfg variants.

## Control Flow
`inside_proc_macro` first reads `WORKS`; if unknown, it calls `INIT.call_once(initialize)` and recurses. With modern `proc_macro::is_available()`, initialization stores availability plus one. On older compilers, initialization temporarily installs a null panic hook, calls `proc_macro::Span::call_site` inside `catch_unwind`, stores success/failure, restores the hook, and panics if another thread disturbed the hook sequence.

## State And Persistence
Detection result is process-global atomic state. `Once` prevents repeated normal detection; `force_fallback` can override the state to false, and `unforce_fallback` attempts to refresh it.

## Dependencies And Integration Points
It depends on `proc_macro`, `std::sync::Once`, atomics, and optionally `std::panic`. `fallback.rs::force` and `unforce` call these functions under `wrap_proc_macro`.

## Risks And Edge Cases
The old panic-hook probing path has a known race window where another thread's panic hook can be missed, and it detects hook tampering with a panic. `unforce_fallback()` calls `initialize()` directly rather than resetting `Once`. Relaxed atomics are enough for a cached availability flag but should not be used for richer state.

## Test Signals
Signals include behavior inside and outside proc macro contexts, forced fallback and unforce transitions, old-compiler cfg path with panic-hook restoration, multi-threaded first calls, and ensuring no spurious stderr panic output during detection.
