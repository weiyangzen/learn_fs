<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/singleflight.rs -->
## sources/cloud-native/nydus/utils/src/singleflight.rs

### Purpose
This module implements Go-style singleflight for async Rust: concurrent calls with the same key collapse to one executor future, and waiters receive the same cloned result.

### APIs, Types, and Control Flow
`Group` owns an `Arc<tokio::sync::Mutex<HashMap<String, CallState>>>`. `do_call()` locks the map, detects an existing `InFlight` watch receiver, removes stale cancelled receivers, or waits for the shared result. If no call is live, it inserts a `watch::Receiver<Option<Result<BoxedResult, String>>>`, drops the lock, awaits the user future, wraps the cloned `Result<T,E>` in a type-erased `Arc<ResultWrapper<T,E>>`, sends it to waiters, removes the key, and returns `CallResult { shared: false }`. `wait_for_result()` repeatedly inspects the watch value, downcasts to `ResultWrapper<T,E>`, maps function errors, or returns `Cancelled` when the sender is gone without a result. `forget()` removes an in-flight key to force a fresh call.

### State, Dependencies, and Integration
The state is transient and in-memory. Results require `T` and `E` to be `Clone + Send + Sync + 'static` because waiters receive cloned typed values from type-erased storage. The stale receiver path is important for integration with externally timed-out operations such as DNS resolution or HTTP connection attempts where the executor future can be dropped before publishing.

### Risks and Test Signals
Calling the same key with inconsistent result or error types yields `TypeMismatch`; this is a contract risk because the key namespace is not type-scoped. If `forget()` is used while an old executor is still running, old and new computations can overlap. Tests cover single and concurrent calls, independent keys, shared errors, sequential re-execution, custom result types, watch channel races, type mismatch, cancellation, externally aborted executor futures, waiting callers during cancellation, and repeated stale-entry recovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/singleflight.rs -->
