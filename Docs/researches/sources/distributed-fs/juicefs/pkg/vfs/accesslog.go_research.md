# sources/distributed-fs/juicefs/pkg/vfs/accesslog.go

Purpose: implements VFS access logging and related Prometheus operation metrics exposed through the internal `.accesslog` file.

Important APIs and types: global histograms/counters track operation durations, totals, and IO errors. `logReader` holds a buffered channel and partial `last` bytes. Functions are `logit`, `openAccessLog`, `closeAccessLog`, and `readAccessLog`.

Control flow and state: `logit` observes metrics for every operation, skips log line construction when there are no readers and the operation is not slow, quotes string arguments when needed, logs slow operations to the normal logger, and non-blockingly fan-outs formatted lines to all active readers. Reader state is held in the package map guarded by `readerLock`. `readAccessLog` first drains partial leftovers, then waits up to one second for log lines, returning `#\n` as a heartbeat on timeout.

Persistence and integration: access log state is in memory but can be captured into handle dumps in `handle.go`. Metrics integrate with Prometheus collection in `internal.go`.

Risks and test signals: reader buffers drop log lines when full. `readAccessLog` serializes reads per handle with a mutex. Tests in `accesslog_test.go` verify formatting, partial reads, invalid handles, and heartbeat behavior.
