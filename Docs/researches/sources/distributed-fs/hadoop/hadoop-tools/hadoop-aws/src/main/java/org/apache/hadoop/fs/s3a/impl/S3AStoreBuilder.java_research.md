# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AStoreBuilder.java

## Purpose
`S3AStoreBuilder` is a simple builder for `S3AStoreImpl`, collecting filesystem infrastructure dependencies before constructing the store layer.

## Important APIs and Types
It has fluent `with...` methods for `StoreContextFactory`, `ClientManager`, duration tracking, instrumentation/statistics, storage statistics, read/write rate limiters, audit span source, and optional `FileSystem.Statistics`. `build()` returns a new `S3AStoreImpl`.

## Control Flow
The builder only assigns fields and passes them to the `S3AStoreImpl` constructor. Constructor-level `requireNonNull` checks in `S3AStoreImpl` enforce most required dependencies.

## State and Persistence
Builder state is transient. It creates a service object but does not start it or persist anything.

## Dependencies and Integration Points
It integrates S3A filesystem initialization with the `S3AStore` service abstraction, client manager service, rate limiters, audit spans, and metrics.

## Risks and Edge Cases
Missing dependencies fail at store construction, not at setter time. The builder is reusable but not immutable, so accidental reuse can carry stale dependencies.

## Test Signals
Tests should cover construction with all required dependencies, failure on missing critical dependencies, optional filesystem statistics, and service initialization after build.
