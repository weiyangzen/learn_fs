# sources/distributed-fs/lizardfs/src/master/filesystem_metadata.h

## Purpose
`filesystem_metadata.h` defines `FilesystemMetadata`, the central in-memory state container for LizardFS master filesystem metadata, plus the global metadata and configuration symbols shared across the master.

## Important types and fields
`FilesystemMetadata` holds tape copy records, xattr inode/data hash tables, the inode pool, ACL storage, trash and reserved detached path containers, root directory pointer, node hash table, task manager, flock and POSIX lock databases, max inode id, next session id, node counters, metadata version, trash/reserved space and node counters, file/dir counters, quota database, and aggregate checksums for nodes, xattrs, and quotas. The constructor zero-initializes pointer arrays and counters, initializes `inode_pool` with reuse delay/capacity settings, and seeds quota checksum from the quota database. The destructor frees xattr linked lists and destroys every node in the node hash table with type-aware `FSNode::destroy`.

## State and persistence behavior
This struct is the authoritative mutable metadata loaded from `metadata.mfs` and changelogs and later dumped back to persistent metadata. `metaversion` is the changelog version cursor. Aggregate checksum fields are updated by mutation paths and verified through checksum changelog entries.

## Dependencies and integration points
It integrates storage for ACLs, chunks, xattrs, quota, locks, tasks, free inode detaining, tape copy tracking, background checksum updating, and node types. Globals include `gMetadata`, `gChecksumBackgroundUpdater`, `gDisableChecksumVerification`, and master-only goal definitions, dumper, atime, and auto-repair flags.

## Risks and test signals
Because it owns raw pointer hash tables and C-style linked lists, destructor coverage and ownership boundaries matter. Tests should load and unload metadata under ASAN/Valgrind, exercise xattr and node allocation/deletion, verify no double frees after trash/reserved transitions, and check that newly constructed metadata starts with consistent counters and checksum seeds.
