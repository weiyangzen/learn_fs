# sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize.go

## Purpose

This file decodes raw BeeGFS metadata event payloads into generated BeeWatch protobuf `Event` messages. It supports both legacy v1 packets and v2 packets introduced with BeeGFS 8.

## Important APIs, Types, And Functions

`deserializeEvent(buf, expectedSize)` is the main entry point. `parseV1Event` maps v1 dropped/missed sequence fields, event type, entry IDs, paths, and target fields. `parseV2Event` maps event flags, link count, v2 event type, identifiers, paths, message user ID, and timestamp. `parseCStrings` and `parseCString` decode length-prefixed null-terminated strings shared by both versions.

## Control Flow

The decoder reads the first uint16 as a major version. Version 1 additionally validates minor version zero and uses the embedded packet size to ensure enough bytes were read before parsing. Version 2 reads event flags, delegates to `parseV2Event`, and verifies the parsed byte count equals the size passed by the caller. Unsupported versions return errors.

## State And Persistence

All decoding is stateless. It returns a freshly allocated protobuf event while reading from a caller-owned reusable byte buffer. Sequence ID assignment for v1 and v2 stream packet sequence IDs happen outside this file.

## Dependencies And Integration Points

It depends on little-endian BeeGFS metadata protocol layout and generated `beewatch` protobuf types. `metadata.serde.SendMessage.Deserialize` reuses it for v2 streamed events, and `Manager.handleV1Connection` uses it directly for v1 socket packets.

## Risks And Test Signals

The low-level parsing performs unchecked slicing and relies on upstream packet size validation; malformed short buffers can panic rather than return an error. `parseCString` assumes the encoded length excludes the null terminator and that the terminator exists. Tests cover representative v1 and v2 packets and selected error cases for unsupported version and v2 size mismatch, but not truncated string fields or oversized lengths.
