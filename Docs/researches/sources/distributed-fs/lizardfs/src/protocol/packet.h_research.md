# sources/distributed-fs/lizardfs/src/protocol/packet.h

Purpose: Defines the core LizardFS packet header, packet version type, message buffer type, and generic serialization/deserialization helpers for both legacy MooseFS packets and versioned LizardFS packets.

Important APIs/types/functions: `PacketHeader`; `PacketVersion`; `MessageBuffer`; `serializePacket`; `buildPacket`; `serializePacketPrefix`; `serializeMooseFsPacket`; `buildMooseFsPacket`; `serializeMooseFsPacketPrefix`; `deserializePacketHeader`; `deserializePacketVersionNoHeader`; `deserializePacketVersionSkipHeader`; data deserialization helpers; `verifyPacketVersionNoHeader`; `receivePacket`.

Control flow: Serializers compute payload length from serialized fields, then prepend `PacketHeader` and optionally packet version. Versioned packet helpers assert type is in the LizardFS range; MooseFS helpers assert old packet range. Deserializers either skip or preserve headers, optionally require full buffer consumption, and throw on trailing bytes or version mismatches.

State and persistence: Stateless helpers over byte buffers. The format is the durable network ABI for protocol messages but this header does not store persistent data.

Dependencies and integration: Uses `MFSCommunication.h` for packet type ranges and `common/serialization.h` for field encoding. Every protocol header in this subset builds on these helpers.

Risks and test signals: Compatibility relies on `PacketHeader::kSize == 8`, old/new packet type ranges, and length semantics where version is included in LizardFS payload length. `packet_unittest.cc` verifies header size; broader malformed-buffer behavior is tested elsewhere if at all.
