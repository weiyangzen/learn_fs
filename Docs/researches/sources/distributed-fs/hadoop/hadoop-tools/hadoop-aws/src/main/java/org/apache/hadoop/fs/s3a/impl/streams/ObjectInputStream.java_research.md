# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStream.java

## Purpose
`ObjectInputStream` is the common base class for streams reading S3 objects. It stores immutable object/read context, statistics, callbacks, leak reporting, vectored IO configuration, and base capabilities shared by classic, prefetch, analytics, and custom streams.

## Important APIs and Types
The constructor takes `InputStreamType` and `ObjectReadParameters`, validates bucket/key/content length, captures callbacks, stream statistics, bounded thread pool, thread IO statistics aggregator, and vectored context. It defines abstract `isStreamOpen()` and `abortInFinalizer()`, implements synchronized `close()`, `finalize()` leak reporting, `getInputPolicy()/setInputPolicy()`, `getS3AStreamStatistics()`, `getIOStatistics()`, `hasCapability()`, vectored read size methods, `streamType()`, and protected accessors for context/callbacks/object identity.

## Control Flow
Subclasses perform actual reads. On close, base class closes callbacks, closes stream statistics, and aggregates stream IO stats into the current thread statistics context. The finalizer asks `LeakReporter` to warn and call subclass abort behavior if the stream remains open. Capability queries advertise IO statistics, stream leaks, and the configured stream-type capability.

## State and Persistence
It stores per-stream state and updates in-memory statistics. It does not directly issue S3 requests or persist data. Close merges metrics back to filesystem/thread aggregates.

## Dependencies and Integration Points
It depends on Hadoop `FSInputStream`, `StreamCapabilities`, `LeakReporter`, S3A read context/object attributes/statistics, IO statistics aggregator, and vectored IO context. Subclasses like `S3AInputStream` and `AnalyticsStream` build on it.

## Risks and Edge Cases
Finalizers are defensive and not deterministic; applications must close streams. Subclasses must ensure `isStreamOpen()` is cheap and thread-safe enough for leak reporting. Base `close()` does not guard idempotence itself; subclasses should avoid double-closing resources. Content length must be non-negative at construction.

## Test Signals
Tests should validate constructor validation, base capabilities, input policy statistic updates, close callback/stat merge behavior, leak reporter invocation, vectored min/max propagation, and subclass close idempotence.
