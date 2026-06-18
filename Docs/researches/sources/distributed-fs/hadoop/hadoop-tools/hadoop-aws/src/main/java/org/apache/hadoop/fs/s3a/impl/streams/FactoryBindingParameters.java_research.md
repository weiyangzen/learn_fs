# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/FactoryBindingParameters.java

## Purpose
`FactoryBindingParameters` packages callbacks supplied to object input stream factories during binding.

## Important APIs and Types
The constructor requires `ObjectInputStreamFactory.StreamFactoryCallbacks`. Package-private `callbacks()` returns the stored callbacks.

## Control Flow
`S3AStoreImpl.finishStreamFactoryInit()` creates this object and passes it to `ObjectInputStreamFactory.bind()`. Factories extract callbacks for client access and statistics.

## State and Persistence
It is an immutable in-memory holder. No persistence.

## Dependencies and Integration Points
It depends on `ObjectInputStreamFactory.StreamFactoryCallbacks` and Java `requireNonNull`. It is part of stream factory lifecycle wiring.

## Risks and Edge Cases
Callback visibility is package-private, so only stream package code can access it. Null callbacks fail immediately.

## Test Signals
Tests should verify null rejection and callback identity propagation through factory binding.
