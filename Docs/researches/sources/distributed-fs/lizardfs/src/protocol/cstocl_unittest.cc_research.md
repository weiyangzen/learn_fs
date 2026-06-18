# sources/distributed-fs/lizardfs/src/protocol/cstocl_unittest.cc

Purpose: Exercises chunkserver-to-client packet helpers from `protocol/cstocl.h`, focused on read data prefix handling and simple status replies. The tests build serialized buffers, verify packet type headers, strip headers, and deserialize back into typed fields.

Important APIs/types/functions: GoogleTest cases `ReadData`, `ReadStatus`, and `WriteStatus`; `cstocl::readData::serializePrefix`/`deserializePrefix`; `cstocl::readStatus`; `cstocl::writeStatus`; `LIZARDFS_DEFINE_INOUT_PAIR`; `verifyHeader`; `removeHeaderInPlace`.

Control flow: Each test defines input/output pairs, serializes into a `std::vector<uint8_t>`, optionally appends CRC and block data, verifies the LizardFS packet type, removes the header, then deserializes and compares values. `ReadData` deliberately tests prefix parsing rather than full block payload parsing.

State and persistence: No persistent state. Buffers are in-memory packet fixtures; the only state mutation is replacement of output variables by deserialization.

Dependencies and integration: Depends on packet constants from `MFSCommunication.h`, block size constants, CRC serialization, and unittest packet helpers. It validates contracts consumed by clients reading from chunkservers.

Risks and test signals: Gives good coverage for field order and packet type, but only covers selected cstocl messages. It does not validate malformed packets, short payloads, or actual data block CRC verification.
