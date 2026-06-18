# sources/distributed-fs/lizardfs/src/protocol/cstoma.h

Purpose: Defines chunkserver-to-master packet contracts for chunkserver registration, space/label reporting, chunk lifecycle status replies, chunk damage/loss reporting, and load status. It is a macro-heavy header that centralizes the wire format for chunkserver reports to the master.

Important APIs/types/functions: `cstoma::overwriteStatusField`; packet families `chunkNew`, `registerHost`, `registerChunks`, `registerSpace`, `registerLabel`, `setVersion`, `deleteChunk`, `createChunk`, `truncate`, `duplicateChunk`, `duptruncChunk`, `replicateChunk`, `chunkDamaged`, `chunkLost`, and `status`. Multiple families expose legacy standard/XOR versions and EC versions.

Control flow: `LIZARDFS_DEFINE_PACKET_SERIALIZATION` generates build/serialize/deserialize helpers for each message. Callers select overloads through field types and packet versions. `overwriteStatusField` mutates an already serialized packet status byte using a fixed offset that assumes chunk id and chunk type precede status.

State and persistence: Stateless serialization except for explicit in-place buffer mutation in `overwriteStatusField`. No disk persistence; messages report master-visible chunkserver state such as chunks, space, and failures.

Dependencies and integration: Depends on chunk type wrappers, chunk-with-version structs, `chunks_with_type`, serialization macros, and packet constants. It is integrated by chunkserver code that announces inventory and operation results to the master.

Risks and test signals: The fixed status offset is fragile and depends on field order and serialized size of `ChunkPartType`; comments on `replicateChunk` warn status must remain the third field. Tests cover registration, status overwrite, register-space, lifecycle replies, replication, and load status.
