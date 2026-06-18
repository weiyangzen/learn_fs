## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataOutputStream.java

Purpose: `FSDataOutputStream` wraps an `OutputStream` as a Hadoop data output stream with byte-position tracking, statistics updates, sync/drop-behind/capability delegation, IO statistics, and optional abort support.

Important APIs and types: the nested `PositionCache` updates an internal position and optional `FileSystem.Statistics` on every write. Public APIs include constructors with optional start position, `getPos`, `getWrappedStream`, `hflush`, `hsync`, `setDropBehind`, `hasCapability`, `getIOStatistics`, and `abort`.

Control flow, state, and persistence: writes go through `PositionCache`, which increments position by written byte count and increments filesystem statistics. `hflush` and `hsync` delegate to `Syncable` streams or fall back to `flush`. Drop-behind and abort require the wrapped stream to implement the corresponding optional interfaces; otherwise they throw `UnsupportedOperationException`. State is in-memory only.

Dependencies and integration: this is the public output stream returned by create/append APIs. It integrates with `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, `Abortable`, `IOStatisticsSupport`, `StoreImplementationUtils`, and `FSExceptionMessages`.

Risks and test signals: risks include position/statistics drift if wrapped streams partially write before throwing, unsupported optional APIs, and closing null or already-closed wrapped streams. Tests should cover single-byte and array writes, start position, statistics increments, sync fallback, capability forwarding, abort success/failure, drop-behind failure, and IO statistics retrieval.
