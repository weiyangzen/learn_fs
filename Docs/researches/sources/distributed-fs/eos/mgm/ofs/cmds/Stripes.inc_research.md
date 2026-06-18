## sources/distributed-fs/eos/mgm/ofs/cmds/Stripes.inc

Purpose: implements low-level replica/stripe maintenance helpers: verifying stripes on FSTs, dropping individual or all stripes, and scheduling stripe copy/move jobs through the drain engine.

Important APIs and types: `_verifystripe` by path and fid, `_dropstripe`, `_dropallstripes`, `_movestripe`, `_copystripe`, `_replicatestripe` by path and by `IFileMD`, `IFileMD`, `IContainerMD`, `FsView`, `FileSystem`, `DrainTransferJob`, `mFidTracker`, `mDrainEngine`, and `SendQuery`.

Control flow: `_verifystripe(path)` resolves fid then calls fid variant. The fid variant reads file metadata for cid/layout, validates parent-container permissions or root-only detached handling, collects parent attributes, looks up target filesystem in `FsView`, constructs an FST query opaque with fid, manager id, access mode, fsid, optional user tag, cid, sealed namespace path, layout id, and options, then sends `/?fst.pcmd=verify` to the FST host/port. `_dropstripe()` resolves file/cid, checks parent write/execute permission or root-only detached drop, write-locks file metadata, records `sys.fs.tracking`, unlinks and optionally removes the location, persists metadata, and for force removal erases inconsistent fsview entries outside the file lock. `_dropallstripes()` requires parent write/execute permission, skips tape-only files, and unlinks/removes every non-tape location.

Replication behavior: `_movestripe()` and `_copystripe()` call `_replicatestripe()` with `dropsource` true/false. The path overload checks parent permissions and source/target location presence. The metadata overload creates a `DrainTransferJob`, registers the fid in `mFidTracker` as a drain operation to avoid duplicate work, and pushes the job to the drain engine thread pool.

State and persistence behavior: verification sends external FST commands but does not mutate namespace metadata. Drop operations mutate file location/unlinked-location lists, `sys.fs.tracking`, file store, optional fsview entries, and sometimes all disk locations. Replication scheduling mutates tracker state and later asynchronous jobs mutate replicas.

Dependencies and integration points: integrates with FST query protocol, FsView id view, layout id/checksum metadata, directory xattrs (`user.tag`), namespace permissions, quota indirectly through file metadata, drain transfer engine, and MGM stats/timing.

Risks: `_verifystripe` condition `cmd && (vid.token || !access)` appears to deny token-authenticated users even if otherwise privileged. `_dropallstripes()` iterates locations while mutating the same file object, which depends on metadata container semantics. Asynchronous replication returns success once scheduled, not once copied/moved. Force removal can erase fsview entries for rare inconsistency cases and needs careful audit.

Test signals: verify by path and fid, missing file/parent/filesystem, permission denial, sealed path in FST query, options propagation, drop linked vs force removal, detached root-only drop, drop-all preserving tape-only files and skipping tape fsid, source missing or target already exists in replication, duplicate fid tracker rejection, and drain job submission.
