# sources/distributed-fs/beegfs-go/watch/internal/metadata/conn.go

## Purpose

This file provides a small connection helper for the BeeGFS v2 file-event protocol. It serializes outbound control messages, reads inbound packets from a Unix packet connection, deserializes them, and coordinates reads with connection shutdown.

## Important APIs, Types, And Functions

`fileEventConnHandler` contains a `net.Conn`, mutex, reusable `Serializer`, reusable `Deserializer`, and logger. `send` serializes a `Serializable` with `Serializer.Assemble` and writes it to the connection. `recv` repeatedly reads into the deserializer buffer, respecting read deadlines and mutex locking, then calls `Disassemble` into the expected `Deserializable`.

## Control Flow

`recv` locks the connection, sets a one-second read deadline, reads a packet, unlocks, and loops on deadline expiry with no bytes read. It treats `net.ErrClosed` as graceful disconnect, logs other read/deserialization errors, and returns a boolean success/failure to the v2 metadata connection state machine.

## State And Persistence

The handler is stateful only through reusable buffers and the underlying connection. It does not persist event sequence state; that is managed by `metadata.Manager`.

## Dependencies And Integration Points

It is used by `Manager.handleV2Connection` for handshake, range, stream-start, and event packets. It depends on the `serde.go` message interfaces and on Unix packet semantics where a read returns a whole packet.

## Risks And Test Signals

The recover block logs the raw connection buffer but does not return a structured panic error. The code assumes no meaningful partial read occurs on deadline expiry; if that invariant fails, an event is lost. `send` has no mutex, which is fine for current linear use but would matter if multiple goroutines wrote to the same handler. Direct tests are absent; coverage should be added around deadline, closed connection, malformed magic, and packet type mismatch behavior.
