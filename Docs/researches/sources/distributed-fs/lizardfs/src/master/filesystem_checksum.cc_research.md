# sources/distributed-fs/lizardfs/src/master/filesystem_checksum.cc

## Purpose
`filesystem_checksum.cc` computes and maintains the metadata checksum components for filesystem nodes, xattrs, quota data, and chunk metadata. It supports both incremental updates during metadata mutation and forced full recalculation for verification or recovery.

## Important APIs and functions
The local `fsnodes_checksum(FSNode *node, bool full_update)` hashes stable node fields: type, id, goal, mode, ownership, timestamps, trash time, directory `entries_hash`, device `rdev`, symlink target hash, or file length plus first and last chunk ids. `fsnodes_update_checksum` removes the old node contribution from aggregate checksums, recomputes the node checksum, and re-adds it, also adjusting the background updater aggregate if the node was already scanned. `fsnodes_checksum_add_to_background` does the same for nodes encountered by the background recalculation pass. `fsnodes_recalculate_checksum` rebuilds `gMetadata->fsNodesChecksum` from all node hash buckets and refreshes directory `entries_hash`. `fs_checksum(ChecksumMode mode)` combines max inode, metadata version, next session id, node checksum, xattr checksum, quota checksum, and `chunk_checksum(mode)`.

## Control flow and state behavior
Incremental mutation paths call `fsnodes_update_checksum` after changing nodes. Force recalculation rebuilds node, xattr, and quota checksums before composing the final checksum. The background updater keeps a separate node and xattr checksum while scanning, then replaces global aggregates if a mismatch is found.

## Dependencies and integration points
This code depends on `hashCombine`, `FSNode` variants, `FilesystemMetadata`, `filesystem_xattr`, chunk checksum support, and `ChecksumBackgroundUpdater`. Master builds expose `fs_start_checksum_recalculation`, which starts the background updater and makes the next event-loop poll nonblocking.

## Risks and test signals
The node checksum is intentionally compact and does not hash every chunk id, only first and last chunk ids plus length. Bugs in directory `entries_hash` maintenance or missed `fsnodes_update_checksum` calls can create false checksum mismatches. Tests should compare incremental and forced checksums after create, rename, link/unlink, chmod/chown, ACL/xattr changes, sparse writes, truncation, trash/reserved transitions, quota changes, and concurrent background recalculation.
