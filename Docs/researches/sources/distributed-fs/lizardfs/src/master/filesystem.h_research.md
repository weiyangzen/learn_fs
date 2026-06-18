# sources/distributed-fs/lizardfs/src/master/filesystem.h

## Purpose
`filesystem.h` is the broad public interface to the LizardFS master filesystem layer. It declares metadata lifecycle, checksum, load/store, changelog-apply, client-visible filesystem operations, metadata-only trash/reserved operations, quota, ACL, xattr, lock, chunk, tape, and task APIs. It is the contract used by master server modules, shadow/metarestore replay code, and protocol handlers.

## Important APIs and types
The file exposes lifecycle functions such as `fs_getversion`, `fs_checksum`, `fs_start_checksum_recalculation`, `fs_load_changelogs`, `fs_loadall`, `fs_storeall`, `fs_unload`, and `fs_unlock`. Mutating operations include create-like calls (`fs_mknod`, `fs_mkdir`, `fs_symlink`, `fs_link`), namespace calls (`fs_rename`, `fs_unlink`, `fs_rmdir`, `fs_recursive_remove`), file content calls (`fs_writechunk`, `fs_try_setlength`, `fs_do_setlength`, `fs_writeend`), attribute calls (`fs_setattr`, `fs_setgoal`, `fs_settrashtime`, `fs_seteattr`, ACL and xattr calls), and detached-node calls (`fs_settrashpath`, `fs_undel`, `fs_purge`). Read APIs include lookup, getattr, readlink, statfs, readdir, checkfile, goal/trashtime/eattr summaries, quota queries, chunk info, and tape copy locations. The apply namespace mirrors changelog entries for shadow masters and metarestore.

## Control flow and persistence behavior
The header makes the split between direct client/master operations and changelog application explicit. Normal master operations validate context, update in-memory metadata, and append/broadcast changelog entries. Apply functions consume changelog payloads, increment `gMetadata->metaversion`, and verify deterministic replay through mismatch returns. `METARESTORE` excludes server-only APIs and exposes `fs_dump`, `fs_term(fname, noLock)`, `fs_init(fname, ignoreflag, noLock)`, and checksum verification toggling.

## Dependencies and integration points
The interface depends on shared protocol and common types: `FsContext`, `Attributes`, `HString`, ACL/RichACL, goals, quota entries, named inode entries, tape keys, checksum mode, metadata dumper, and async task stats for setgoal/settrashtime. It is the central include point for master request handlers and changelog parsing.

## Risks and test signals
Because this header is a wide ABI within the master, signature drift or personality guards can break many call sites. Tests should exercise both master and shadow replay paths for each changelog-producing operation, verify return codes match protocol expectations, instantiate both legacy and current `fs_readdir` templates, and build both normal and `METARESTORE` targets.
