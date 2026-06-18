<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/output_packet.h -->
# sources/distributed-fs/lizardfs/src/common/output_packet.h

## Purpose
Defines a move-only outgoing packet container used by servers writing protocol messages to clients. The source was read completely for this report.

## Important APIs, Types, And Functions
`OutputPacket(PacketHeader)`, `OutputPacket(MessageBuffer)`, default constructor, move operations, deleted copy operations, `packet`, and `bytesSent` are the contract.

## Control Flow
The header constructor reserves header+payload size, serializes the header, and resizes the buffer to include payload space. MessageBuffer constructor takes ownership of an existing serialized message.

## State And Persistence Behavior
State is an owned message buffer and byte progress counter; no persistence.

## Dependencies And Integration Points
Depends on `protocol/packet.h` and serialization helpers. Used by network output queues.

## Risks And Edge Cases
Payload bytes after the header are uninitialized/resized placeholders until callers fill them. `bytesSent` must be maintained by send loops.

## Test Signals
Tests should cover move-only behavior, header serialization size, and partial-send progress handling in output queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/output_packet.h -->
