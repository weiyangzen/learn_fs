# sources/cloud-native/moby/daemon/logger/local/read.go

Purpose: read and tail implementation for local protobuf log files.

Important APIs/types/functions: `ReadLogs`, `getTailReader`, `decoder`, `readRecord`, `Decode`, `Reset`, `Close`, `decodeSizeHeader`, and `decodeLogEntry`. `maxMsgLen` caps serialized records at 1 MB.

Control flow/state/persistence: `getTailReader` walks backward through footer/header pairs to find the requested number of records and returns a section reader. The decoder reads a size header, enforces max size, reads payload plus footer into a reusable buffer, unmarshals protobuf, reconstructs a message, and appends newline for non-partial or final partial entries.

Dependencies/integration: uses `loggerutils.LogFile` hooks and generated `logdriver.LogEntry`.

Risks: corrupt size headers/footers become data-loss or decode errors. `readRecord` retries `io.ErrUnexpectedEOF` up to `maxDecodeRetry`, which supports append-in-progress reads but can spin on permanently truncated records.

Test signals: `read_test.go` specifically covers incomplete records; local and loggerutils tests cover tail/follow behavior.
