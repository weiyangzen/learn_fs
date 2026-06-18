# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/BufferedIOStatisticsOutputStream.java

Purpose: `BufferedOutputStream` subclass that preserves wrapped-stream `IOStatistics`, forwards stream capabilities, and implements `Syncable` with optional downgrade to flush.

Important APIs and types: constructors with default/custom buffer size and `downgradeSyncable`, `getIOStatistics()`, `hasCapability()`, `hflush()`, and `hsync()`.

Control flow: `getIOStatistics()` delegates through `IOStatisticsSupport.retrieveIOStatistics(out)`. `hasCapability()` delegates when wrapped stream implements `StreamCapabilities`. `hflush()` and `hsync()` flush the buffer first, then call the wrapped `Syncable` method if supported; otherwise either throw `UnsupportedOperationException` or just flush when downgrade is enabled.

State and persistence: inherited output buffer plus immutable `downgradeSyncable`. Writes/syncs mutate the wrapped output destination.

Dependencies and integration: implements `IOStatisticsSource`, `Syncable`, and `StreamCapabilities`; mirrors `FsDataOutputStream` downgrade behavior when configured.

Risks: downgrade mode violates strict `Syncable` durability expectations by reducing sync to flush. Capability delegation may claim support based on underlying stream but buffering can affect timing. Unsupported exceptions include wrapped stream `toString()` for diagnostics.

Test signals: cover statistics delegation, capability delegation, hflush/hsync on syncable stream including flush-before-sync, unsupported behavior with downgrade false, flush fallback with downgrade true, custom buffer size, and exception propagation from inner sync.
