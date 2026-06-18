# sources/distributed-fs/beegfs-go/watch/internal/metadata/serde.go

## Purpose

This file defines the BeeGFS v2 file-event control protocol serialization/deserialization layer used between BeeWatch and the metadata service.

## Important APIs, Types, And Functions

`MsgID` enumerates packet types and has a `String` method. `Serializable` and `Deserializable` define message interfaces. `Serializer.Assemble` writes message ID, magic string `events\x00`, and message-specific payload. `Deserializer.Disassemble` validates packet type and magic, then calls message-specific `Deserialize`. Message structs include `HandshakeRequest`, `HandshakeResponse`, `RequestMessageNewest`, `SendMessageNewest`, `RequestMessageRange`, `SendMessageRange`, `RequestMessageStreamStart`, `SendMessage`, `CloseRequest`, and `SendClose`.

## Control Flow

Outbound messages are serialized through little-endian binary writes into a reusable buffer. Inbound messages are first copied from a raw connection buffer into a parsing buffer, then decoded by expected type. `SendMessage.Deserialize` reads the stream sequence ID and event size, decodes the remaining bytes with `deserializeEvent`, assigns `Event.SeqId`, and leaves metadata ID/mirror assignment to the manager.

## State And Persistence

The serializer/deserializer hold reusable memory but no durable state. Deserialization panics are treated as fatal: the deferred recover in `Disassemble` prints diagnostic hex and exits the process.

## Dependencies And Integration Points

It depends on the same raw protocol as BeeGFS metadata and on generated `beewatch` protobuf event types. `conn.go` uses it for all v2 connection packets, while `manager.go` defines protocol sequencing.

## Risks And Test Signals

The fatal `os.Exit(1)` on deserialize panic can terminate BeeWatch on malformed input; returning an error would be safer for a network-facing parser. Many `binary.Write`/`binary.Read` calls ignore errors in message-specific methods. Magic/type validation is a useful guard, but tests for it are not present. The generated `SendMessage` event-size field is uint16, so event payloads above that limit are unsupported by protocol design.
