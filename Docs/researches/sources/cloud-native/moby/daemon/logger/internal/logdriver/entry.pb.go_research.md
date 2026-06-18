# sources/cloud-native/moby/daemon/logger/internal/logdriver/entry.pb.go

Purpose: generated gogofaster protobuf support for the internal `logdriver` wire schema used by local logging and plugin stream encoding. It materializes `LogAttr`, `LogEntry`, and `PartialLogEntryMetadata` with getters, protobuf descriptor registration, marshal, size, skip, and unmarshal routines.

Important APIs/types/functions: `LogAttr` carries immutable key/value metadata. `LogEntry` carries source stream, nanosecond timestamp, raw line bytes, partial-message flag, optional partial metadata, and repeated attrs. `PartialLogEntryMetadata` mirrors `backend.PartialLogMetaData`. `MarshalToSizedBuffer`, `Size`, and `Unmarshal` are the hot path for local log writes and reads.

Control flow/state/persistence: the file is stateless generated codec code. Persistence behavior is determined by callers: `local.marshal` serializes `LogEntry` into a length-delimited on-disk record; `internal/logdriver/io.go` serializes entries into plugin streams. Unknown field skipping and varint parsing are generated defensively but assume valid protobuf framing from callers.

Dependencies/integration: imports `github.com/gogo/protobuf/proto` and is generated from `entry.proto`. It is consumed by `daemon/logger/local` and `daemon/logger/plugin`.

Risks: hand-editing is unsafe because generated field numbers and marshal logic define the on-disk and plugin wire contract. Corrupt or malicious input is bounded mostly by caller-side size checks; local decoder caps records before calling `Unmarshal`.

Test signals: no direct tests in this file, but local logger read/write tests, local incomplete-record tests, and plugin/logdriver users validate round trip behavior.
