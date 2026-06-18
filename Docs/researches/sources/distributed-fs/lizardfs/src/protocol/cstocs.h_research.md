# sources/distributed-fs/lizardfs/src/protocol/cstocs.h

Purpose: Defines chunkserver-to-chunkserver wire helpers for asking another chunkserver about chunk block availability and returning that availability/status. It supports both legacy standard/XOR chunk part encoding and newer `ChunkPartType` encoding for erasure-coded chunks.

Important APIs/types/functions: `cstocs::getChunkBlocks::{serialize,deserialize}`; `cstocs::getChunkBlocksStatus::{serialize,deserialize}`; packet versions `kStandardAndXorChunks = 0` and `kECChunks = 1`; packet types `LIZ_CSTOCS_GET_CHUNK_BLOCKS` and `LIZ_CSTOCS_GET_CHUNK_BLOCKS_STATUS`.

Control flow: Callers choose overloads by `legacy::ChunkPartType` or `ChunkPartType`. Serializers emit versioned LizardFS packets; deserializers first verify the expected packet version and then fully deserialize chunk id, version, part type, and for responses block count/status.

State and persistence: Stateless inline serialization layer. It only transforms typed fields into message buffers and back.

Dependencies and integration: Uses `common/chunk_part_type.h`, `protocol/MFSCommunication.h`, and `protocol/packet.h`. It integrates with chunk repair/replication paths that need per-part block information from peer chunkservers.

Risks and test signals: Version mismatch throws `IncorrectDeserializationException`, protecting against decoding legacy and EC layouts interchangeably. Risks are wire compatibility if field order or version constants change; `cstocs_unittest.cc` covers the EC overloads for both request and response.
