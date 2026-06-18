# sources/distributed-fs/lizardfs/src/protocol/packet_unittest.cc

Purpose: Minimal unit test validating the serialized size constant for packet headers.

Important APIs/types/functions: `TEST(PacketTests, PacketHeaderSize)`; `PacketHeader::kSize`; `serializedSize(PacketHeader)`.

Control flow: Constructs a packet header, copies the constant to a local variable for GTest compatibility, and asserts serialized size equals the constant.

State and persistence: None.

Dependencies and integration: Depends on GTest and `protocol/packet.h`. It protects a core ABI invariant used by socket readers and packet helpers.

Risks and test signals: The test is narrow but high value: a header-size mismatch would break all packet framing. It does not cover packet range predicates, length semantics, or deserialization helpers.
