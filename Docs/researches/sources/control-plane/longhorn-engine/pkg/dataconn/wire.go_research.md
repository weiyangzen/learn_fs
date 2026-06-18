# sources/control-plane/longhorn-engine/pkg/dataconn/wire.go

Purpose: serializes and deserializes `Message` headers and payloads over a `net.Conn` using fixed little-endian fields plus a variable-length data payload.

Important APIs/types/functions: `Wire` wraps a connection, buffered writer/reader, and reusable header buffers. `NewWire` sizes buffers using package constants. `Write` emits `MagicVersion`, `Seq`, `Type`, `Offset`, `Size`, and payload length, then writes payload bytes and flushes. `Read` uses `io.ReadFull` for the header and payload, validates `MagicVersion`, allocates payload memory when length is nonzero, and converts mid-payload EOF into `io.ErrUnexpectedEOF`. `Close` closes the underlying connection. `getRequestHeaderSize` computes the fixed header size from Go field sizes plus a uint32 payload length.

Control flow: every read is all-or-error for the header. A clean EOF before any header byte propagates as `io.EOF`; partial header reads are wrapped. Payload allocation is based solely on the length field, then read fully.

State and persistence: no durable state. Header byte slices are reused per `Wire`, so concurrent calls to `Read` or concurrent calls to `Write` on the same `Wire` would race.

Dependencies and integration points: used by dataconn client/server and therefore by replica data server and socket frontend. It depends on `encoding/binary`, `bufio`, and `unsafe.Sizeof` for field widths.

Risks: there is no maximum payload length check before allocation, so a malformed peer can request large memory. The `Size` field and payload length can disagree; consumers decide what that means. Offset is serialized as uint64 then cast to int64, so negative offsets round-trip by two's-complement behavior but are not semantically validated here. The reusable buffers mean callers must serialize access externally.

Test signals: no direct tests. The robust distinction between clean EOF and unexpected payload EOF is a useful behavior to cover in dataconn tests.
