# sources/cloud-native/moby/daemon/logger/internal/logdriver/io.go

Purpose: provides length-prefixed protobuf stream encoding/decoding for `LogEntry`, primarily for log plugin stream transport.

Important APIs/types/functions: `LogEntryEncoder` and `LogEntryDecoder` expose `Encode` and `Decode`. `NewLogEntryEncoder` and `NewLogEntryDecoder` allocate reusable buffers. `binaryEncodeLen` is 4 bytes, big-endian message length.

Control flow/state/persistence: `Encode` calculates protobuf size, grows a reusable buffer, writes the 4-byte length, marshals the protobuf after it, then writes one frame. `Decode` reads exactly 4 bytes, grows a buffer if needed, reads exactly the framed payload, and unmarshals into caller-provided `LogEntry`.

Dependencies/integration: uses standard `encoding/binary` and `io`, plus generated `LogEntry`. `plugin.go` creates an encoder for plugin FIFO streams.

Risks: decoder has no explicit max frame length, so callers must trust the peer or wrap the reader. Short reads surface as `io.ReadFull` errors. The framing format differs from the local driver's size-header-plus-footer disk format.

Test signals: validated indirectly by plugin adapter tests in adjacent code and any plugin stream integration tests.
