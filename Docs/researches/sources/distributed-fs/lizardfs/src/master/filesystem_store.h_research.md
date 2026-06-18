# sources/distributed-fs/lizardfs/src/master/filesystem_store.h

Purpose: declares metadata persistence exceptions and top-level load/store helpers for the master filesystem.

Important APIs/types/functions: defines `MetadataException`, `MetadataFsConsistencyException`, and `MetadataConsistencyException`; exposes `fs_commit_metadata_dump()`, `fs_emergency_saves()`, `fs_broadcast_metadata_saved()`, changelog load helpers, `fs_loadall()`, and `fs_store_fd()`.

Control flow: callers use `fs_loadall()` during startup/metarestore, `fs_store_fd()` for writing to an already opened stream, and `fs_commit_metadata_dump()`/`fs_emergency_saves()` around dump commit failures.

State and persistence behavior: the header itself has no state; declared functions read and write the complete metadata image and changelogs.

Dependencies/integration: includes the shared exception base and `MetadataDumper` type. It is included by initialization, dump, restore, and storage modules.

Risks and test signals: exception taxonomy is broad and consumers need to distinguish structure/read consistency errors from lower-level I/O. Tests should assert thrown exception classes/messages for bad headers, missing files, and corrupted metadata.
