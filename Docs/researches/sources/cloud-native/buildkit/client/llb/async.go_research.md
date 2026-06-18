# sources/cloud-native/buildkit/client/llb/async.go

Purpose: lazy asynchronous state transformation support for LLB states, used for operations such as image metadata resolution.

Important APIs/types/functions: `asyncState` stores a transformation function, previous state, and `flightcontrol.CachedGroup` to deduplicate execution. It implements `Output`, `Vertex`, `ToInput`, and `Do`. `errVertex` adapts async errors into a `Vertex` that fails validation/marshal.

Control flow: async callbacks are not run when the state chain is created. During vertex/input/value resolution, `Do` calls the transformation once per constraints through the cached group; successful target state delegates output and input behavior. Errors return `errVertex` or propagate from `ToInput`.

State and persistence: in-memory cached result/error on the async state; `CacheError` is set by `State.Async` in `state.go`. No external persistence.

Dependencies/integration points: `flightcontrol.CachedGroup`, `solver/pb`, digest, and state value lookup/marshal paths.

Risks/test signals: cache key is empty string, so an `asyncState` caches one result independent of constraints passed to `Do`; correctness relies on the state instance being used consistently or callback considering constraints at first resolution. `async_test.go` verifies callbacks are lazy/nonblocking until marshal.
