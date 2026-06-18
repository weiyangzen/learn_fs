<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ResourcePool.h -->
# sources/compression/zstd/contrib/pzstd/utils/ResourcePool.h

## Purpose
`ResourcePool.h` provides a thread-safe reusable pool for expensive mutable resources such as zstd streams.

## Important APIs, Types, And Functions
`ResourcePool<T>` takes a factory and free function, exposes `get()` returning `unique_ptr<T, Deleter>`, and returns resources to the pool when the custom deleter runs.

## Control Flow
`get` pops an available resource or creates one, increments `inUse_`, and hands it out. The deleter pushes non-null resources back and decrements `inUse_`. Destruction asserts no resources are checked out and frees cached resources.

## State And Persistence
State is a mutex, resource vector, factory/free closures, and in-use count. No disk persistence exists.

## Dependencies And Integration Points
`SharedState` uses it for `ZSTD_CStream` and `ZSTD_DStream` reuse across worker tasks.

## Risks
The pool must outlive all returned unique pointers. Resources must be reset by callers before reuse because the pool does not sanitize them.

## Test Signals
`ResourcePoolTest.cpp` covers reuse, factory/free counts, and thread safety.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ResourcePool.h -->
