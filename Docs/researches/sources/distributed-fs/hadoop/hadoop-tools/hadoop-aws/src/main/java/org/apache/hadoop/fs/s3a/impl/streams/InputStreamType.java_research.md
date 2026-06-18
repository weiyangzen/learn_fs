# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/InputStreamType.java

## Purpose
`InputStreamType` enumerates S3A object input stream implementations and maps each type to a factory-construction function, numeric stream ID, and capability name.

## Important APIs and Types
Values are `Classic`, `Prefetch`, `Analytics`, and `Custom`. Each has a config name, stable stream ID, and `Function<Configuration,ObjectInputStreamFactory>`. Methods expose `getName()`, `streamID()`, `capability()`, and `factory()`.

## Control Flow
Stream integration code selects an enum value from configuration and invokes `factory()` to create the selected factory. `Custom` delegates to `StreamIntegration.loadCustomFactory()`.

## State and Persistence
Enum constants are immutable. No persistence.

## Dependencies and Integration Points
It depends on stream integration constants, `PrefetchingInputStreamFactory`, classic and analytics factories, and Hadoop `Configuration`. It drives `fs.s3a.input.stream.type` behavior and capability reporting.

## Risks and Edge Cases
Numeric IDs are intentionally decoupled from enum ordinals; metrics should use `streamID()` rather than `ordinal()` if stable IDs are needed. Custom factory loading can fail due to classpath/configuration errors.

## Test Signals
Tests should validate name-to-factory mapping, capability strings, stable IDs, custom factory loading, and configured stream selection.
