# sources/distributed-fs/lizardfs/src/protocol/matocl.h

Purpose: Central master-to-client protocol header. It defines versioned responses for FUSE operations, quota/goal/eattr/trash tools, chunk and tape information, admin commands, metadata server status, lock management, directory listings, task control, and chunk read/write location replies.

Important APIs/types/functions: Packet families include `updateCredentials`, `fuseMknod`, `fuseMkdir`, ACL get/set/delete, quota get/set/delete, `fuseGetGoal`, `fuseSetGoal`, `listGoals`, `chunksHealth`, `cservList`, `metadataserversList`, `chunksInfo`, admin responses, `tapeInfo`, `listTapeservers`, truncate and lock responses, `wholePathLookup`, `recursiveRemove`, `fuseGetDir`, reserved/trash listings, `listTasks`, `stopTask`, `requestTaskId`, `snapshot`, `listDefectiveFiles`, `fuseReadChunk`, `fuseWriteChunk`, and `fuseWriteChunkEnd`.

Control flow: Macro-generated helpers serialize and deserialize typed payloads. Several message families have status and success response versions; callers inspect `PacketVersion` first and then select the matching deserialize overload. Read/write chunk helpers are hand-written to hide message id during deserialization and support legacy server lists and EC-aware server lists.

State and persistence: Stateless serialization definitions. The payloads convey master state such as metadata version, quota entries, directory entries, chunk locations, tape copies, and task ids, but the header does not store state.

Dependencies and integration: Pulls in many common serializable types, including ACLs, attributes, chunk addresses, quota structs, lock info, directory entries, job info, metadata server entries, and tape info. It is consumed by FUSE clients, admin tools, and `src/tools` commands through `ServerConnection`.

Risks and test signals: Biggest risks are version drift, overload ambiguity, and status-vs-response decoding mistakes. Constants such as `chunksInfo::kMaxNumberOfResultEntries` and `fuseGetDir::kMaxNumberOfDirectoryEntries` limit response sizing. `matocl_unittest.cc` covers chunk read/write variants, chunk health, and ACL packets, while tools exercise quota/goal/task packets indirectly.
