# sources/distributed-fs/lizardfs/src/protocol/matocs.h

Purpose: Defines master-to-chunkserver command packets for chunk lifecycle operations: set version, delete, create, truncate, duplicate, duplicate-and-truncate, and replicate.

Important APIs/types/functions: Packet families `matocs::setVersion`, `deleteChunk`, `createChunk`, `truncateChunk`, `duplicateChunk`, `duptruncChunk`, `replicateChunk`; versions `kStandardAndXorChunks` and `kECChunks`; `replicateChunk::deserializePartial`.

Control flow: Serializers choose legacy or EC layout by chunk type. Deserializers verify version and fully consume buffers. `deserializePartial` decodes the fixed prefix of a replicate request and returns a pointer to the source list payload for code that wants to parse sources separately.

State and persistence: Stateless wire helpers. The messages command chunkserver state changes but do not persist anything directly.

Dependencies and integration: Depends on `common/chunk_type_with_address.h`, `protocol/packet.h`, and serialization macros. Used by master scheduling code to tell chunkservers how to mutate chunk replicas.

Risks and test signals: These operations can cause data movement or deletion, so field order and version correctness are high risk. Partial deserialization has pointer lifetime and buffer-layout assumptions. `matocs_unittest.cc` covers set-version, delete, and replicate EC paths.
