# sources/distributed-fs/lizardfs/src/master/filesystem_node_types.h

## Purpose
`filesystem_node_types.h` defines the core in-memory node types, hash constants, session/operation enums, stats records, and detached-container key types used by the filesystem metadata layer.

## Important types and fields
Constants define node and edge hash sizes, checksum seeds, and `MAX_INDEX`. Enums include `AclInheritance`, `SessionType`, `OperationMode`, and `ExpectedNodeType`. `statsrecord` stores recursive counts and sizes. `FSNode` stores common inode metadata, parent ids, hash-chain link, and per-node checksum, with factory/destructor methods. `FSNodeFile` adds file length, open session ids, and chunk ids with `chunkCount()`. `FSNodeSymlink` stores a string handle and path length. `FSNodeDevice` stores `rdev`. `FSNodeDirectory` stores an ordered/flat/Judy entry map, subtree stats, nlink, and `entries_hash`, with name and node lookup helpers. `TrashPathKey` sorts trash by expiration timestamp and inode id, with endian-aware field order.

## State and persistence behavior
These structs are the shape of loaded metadata in memory. Directory entries use `hstorage::Handle` for names and compact vectors for parent/session/chunk storage to reduce memory footprint. Trash and reserved containers map detached files to their original paths and are persisted through metadata/changelogs.

## Dependencies and integration points
The file integrates common access-control, attributes, goals, compact vector, Judy/flat maps, FsContext, and string-handle storage. It is foundational for checksum, operations, dumping, load/store, and quota code.

## Risks and test signals
Memory layout and container choice affect master scalability. `FSNodeDirectory::find` scans the equal-name-hash range, so hash collisions must be handled correctly. Tests should cover name hash collisions, directory ordering/readdir indexes, `chunkCount` with trailing zero chunks, endian behavior for trash key ordering, and correct factory/destructor pairing for every node type.
