## sources/cloud-native/moby/daemon/logger/copier.go

Purpose: Copies container stdout/stderr streams into a `Logger`, assigning timestamps, source names, and partial-log metadata for overlong or unterminated lines.

Important APIs and types: `Copier` holds source readers, destination logger, wait group, close once, and closed channel. `NewCopier`, `Run`, `copySrc`, `Wait`, and `Close` form the lifecycle. Constants `readSize` and `defaultBufSize` define incremental read size and default log line buffer.

Control flow and state: `Run` launches one goroutine per source. `copySrc` chooses buffer size from `SizedLogger` when available, reads up to `readSize` increments, scans buffered bytes for newlines, emits complete messages with current UTC timestamp, and emits partial messages when EOF or full buffer occurs without newline. Partial messages share a generated ID and timestamp across chunks, increment ordinal, and mark the final chunk on the next newline. `Close` closes the shared channel once and causes copy loops to return.

Dependencies and integration points: Uses logger message pooling, `SizedLogger`, daemon backend `PartialLogMetaData`, string ID generation, metrics counters (`totalPartialLogs`, `logReadsFailedCount`), and log driver error reporting.

Risks: Partial metadata logic is subtle around EOF, full buffers, and newline finalization. Destination `Log` errors require returning messages to the pool to avoid leaks. Slow or blocking loggers can stall copy goroutines until `Close` is observed between operations.

Test signals: `copier_test.go` covers normal streams, long lines, slow logger close, sized loggers and ring wrappers, partial metadata, and benchmarks across message sizes.
