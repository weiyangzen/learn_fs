# sources/distributed-fs/lizardfs/src/master/filesystem_operations.cc

## Purpose
`filesystem_operations.cc` implements the high-level filesystem API declared in `filesystem.h` and `filesystem_operations.h`. It translates protocol-level requests into validated metadata mutations or reads, emits changelog records on the master, applies changelog records on shadow/metarestore, updates operation statistics, and coordinates locks, quotas, chunks, ACLs, xattrs, tape copies, and background tasks.

## Important APIs and control flow
The file starts with `fs_changelog`, which prepends timestamps, increments `metaversion`, writes changelog records, and broadcasts them to metaloggers/shadows. Namespace operations include lookup/path lookup/getattr, create (`fs_mknod`, `fs_mkdir`, `fs_symlink`, `fs_apply_create`), unlink/rmdir/recursive remove/apply unlink, rename, hard link, and append. File content operations include set length/truncate/unlock, readchunk/writechunk/writeend, repair/apply repair, and next chunk id. Metadata operations include setattr/apply attr, ACL and RichACL set/delete/get/apply, xattr list/get/set/apply, goal/trashtime/eattr get/set/apply/deprecated recursive paths, quota-related checks through node helpers, and detached trash/reserved operations. Lock APIs wrap flock and POSIX `FileLocks` for lock, probe, clear session, list, unlock inode, and remove pending. End-of-file APIs expose tape copy updates, chunk info, task cancellation/id reservation, version, and rebuilding chunk file references.

## State and persistence behavior
Master operations usually create `ChecksumUpdater`, validate `FsContext` and permissions, mutate nodes through `fsnodes_*` helpers, then write a changelog entry. Shadow/apply variants mutate deterministically, increment `gMetadata->metaversion`, and return mismatch when replayed ids, chunk ids, counters, ACL data, or task results differ from the master. Operation counters in `gFsStatsArray` are incremented for common request classes and retrieved/reset by `fs_retrieve_stats`.

## Dependencies and integration points
This file is the integration hub for protocol handlers. It depends on event-loop time, changelog broadcasting, chunks, filesystem checksum, node helpers, quota helpers, locks, master-client and metalogger services, recursive remove/setgoal/settrashtime task manager, tape server metadata, and protocol constants.

## Risks and test signals
The highest risks are divergent master versus shadow replay, missed changelog entries, stale checksums after early returns, quota deltas around rename/truncate/append, and permissions around rootinode, meta sessions, sticky directories, ACLs, and open file flags. Tests should replay every changelog verb, check mismatch detection, exercise delayed truncation and write locks, test quota failure boundaries, verify lock queue wakeups after unlock/release, validate xattr/ACL string parsing, cover tape-goal write denial, and run metadata checksum comparison after operation sequences.
