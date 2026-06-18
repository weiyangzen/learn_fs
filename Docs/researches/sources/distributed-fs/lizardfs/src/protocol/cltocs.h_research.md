# sources/distributed-fs/lizardfs/src/protocol/cltocs.h

## Purpose
Defines typed serializers/deserializers for client-to-chunkserver packets.

## Important APIs, Types, And Functions
Supports prefetch, read, write init, write data prefix, write end, and test chunk messages. Packet versions distinguish standard/xor legacy chunk types from EC-capable `ChunkPartType` and `ChunkTypeWithAddress` chains. `writeData::kPrefixSize` defines the headerless prefix length for write data before payload bytes.

## Control Flow
Inline serializers call `serializePacket` or `serializePacketPrefix` with the correct command id and version. Deserializers verify packet version then unpack fields with `deserializeAllPacketDataNoHeader` or `deserializePacketDataNoHeader`.

## State And Persistence Behavior
No state. It defines wire encoding for read/write operations used by chunkserver clients and write paths.

## Dependencies And Integration Points
Depends on serialization macros, chunk part/address types, `protocol/packet.h`, and IDs from `MFSCommunication.h`. Integrated by chunk IO code, including mount write/read logic.

## Risks And Edge Cases
Correct packet version selection is critical for EC chunks. `writeData::serializePrefix` reserves `size` bytes of extra payload, so callers must append exactly matching data and CRC semantics. Prefix size constants must stay synchronized with field layout.

## Test Signals
`cltocs_unittest.cc` exercises read, write init, write data prefix, write end, and test chunk round trips and header ids.
