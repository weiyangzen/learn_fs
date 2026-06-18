# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalOutputStream.java

## Purpose
`JournalOutputStream` is the legacy entry-level write abstraction for checkpoint and log output.

## Important APIs, Types, and Functions
It extends `AutoCloseable` and defines `write(JournalEntry)`, `close()`, and `flush()`.

## Control Flow, State, and Persistence
Implementations write entries, may assign sequence numbers, flush buffered bytes, and close physical resources. Checkpoint and log implementations can enforce different ordering rules behind the same interface.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry` and `IOException`. It is returned by `JournalWriter.getCheckpointOutputStream()` and implemented by UFS checkpoint/log streams.

## Risks and Test Signals
Risks include writing after close, forgetting to flush log entries, and differing durability semantics on UFS backends that do not support flush. Signals are write-after-close failures, forced log rotation on no-flush stores, and checkpoint close updating the active checkpoint atomically.
