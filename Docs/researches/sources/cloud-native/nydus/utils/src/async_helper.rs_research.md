# sources/cloud-native/nydus/utils/src/async_helper.rs

Purpose: provides a thread-local Tokio current-thread runtime for synchronous code that needs to execute async operations.

Important APIs/types/functions: `CURRENT_THREAD_RT` is a `thread_local!` `Runtime` built with `Builder::new_current_thread().enable_all()`. `with_runtime<F, R>(f)` passes the runtime reference to a callback.

Control flow: first use on each thread constructs a current-thread runtime or panics with a clear message. Callers run async work through the callback, usually `rt.block_on(...)`.

State and persistence: runtime state is thread-local and lives for the lifetime of the thread. No persistence.

Dependencies and integration points: depends on Tokio runtime builder. Used by synchronous Nydus code paths that need timers, IO, or async primitives without owning a global multi-thread runtime.

Risks: nested Tokio runtime/blocking interactions can panic or deadlock if called from incompatible async contexts. One runtime per thread may increase resource usage in thread-heavy paths. Panic on runtime construction failure is acceptable for utility initialization but not recoverable.

Test signals: unit test calls `with_runtime` twice and verifies simple `block_on` results.
