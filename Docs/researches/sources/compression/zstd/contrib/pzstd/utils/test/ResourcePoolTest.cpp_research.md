<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ResourcePoolTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/ResourcePoolTest.cpp

## Purpose
This test verifies `ResourcePool` reuse, cleanup, and thread safety.

## Important APIs, Types, And Functions
It creates integer resources through factory/free lambdas and exercises `ResourcePool<int>::get` with nested scopes and multiple threads.

## Control Flow
The full test checks that returned resources are reused and freed once at pool destruction. The thread-safe test concurrently checks out resources and validates expected values/counters.

## State And Persistence
State is local counters and heap integers owned by the pool. No disk persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/ResourcePool.h`. It supports confidence in zstd stream pooling used by pzstd workers.

## Risks
The tests cover simple resources, not zstd stream reset discipline.

## Test Signals
Passing tests validate the pool's lock-protected checkout/return lifecycle.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ResourcePoolTest.cpp -->
