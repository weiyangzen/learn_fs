# sources/distributed-fs/lizardfs/src/master/filesystem_checksum.h

## Purpose
`filesystem_checksum.h` declares the filesystem checksum entry points shared by metadata mutation code, periodic background workers, and public filesystem APIs.

## Important APIs
`fsnodes_checksum_add_to_background(FSNode *node)` contributes a node to the background checksum pass. `fsnodes_update_checksum(FSNode *node)` is the normal post-mutation hook for refreshing node checksum state and aggregate checksum values. `fs_checksum(ChecksumMode mode)` returns the current or force-recalculated metadata checksum. `fs_start_checksum_recalculation()` starts the asynchronous checksum recalculation pass in normal master builds.

## Control flow and dependencies
The header includes checksum primitives, metadata, node types, version/personality helpers, and master status macros. It is consumed by node mutation, filesystem operation, periodic maintenance, and lifecycle code. The API intentionally hides the exact node hashing algorithm from callers, so callers only need to remember to invoke update hooks around metadata changes.

## State and persistence behavior
The functions operate on `gMetadata` aggregate checksum fields and, when relevant, `gChecksumBackgroundUpdater`. Checksum values are persisted indirectly through changelog `CHECKSUM` entries and metadata dumps; this header provides the hooks but not changelog emission.

## Risks and test signals
The main risk is missing this hook from a metadata mutation path. Static or review tests should flag direct changes to `FSNode` fields, directory entries, file chunks, or xattr/quota state that lack checksum updates. Build tests should include `METARESTORE` and master personalities because availability of `fs_start_checksum_recalculation` depends on compile mode.
