# sources/distributed-fs/moosefs/mfsmaster/filesystem.c lines 1-9113

## Purpose

This chunk implements most of the MooseFS master in-memory filesystem namespace and file metadata engine. It defines the core inode (`fsnode`) and directory-entry (`fsedge`) model, custom bucket allocators, inode reuse tracking, hash indexes, quota accounting, POSIX permission/ACL/xattr integration, trash/sustained-file handling, namespace operations, snapshot/append/truncate/write chunk operations, and metadata consistency scanning through the first part of `fs_test_files`.

The code is the authoritative bridge between client-visible filesystem calls and lower master subsystems: chunks, storage classes, sessions/open-files, xattrs, ACLs, changelog persistence, quota state, data-cache invalidation, pattern rules, and missing-chunk reporting.

## Important Types And Global State

- `fsnode` is the inode object. Common fields include inode id, ctime/mtime/atime, uid/gid, mode/type, flags for xattr/ACL/default ACL, storage class id, extended attributes, Windows attributes, trash retention, parent edge list, and type-specific union data.
- `fsedge` is a named parent-child link. It carries child/parent pointers, intrusive links through the parent children list and child parents list, a hash-chain pointer, an edge id used for directory continuation, and inline name storage.
- `statsrecord` caches subtree counts and space metrics: inodes, dirs, files, chunks, logical length, chunk storage size, and real size adjusted by storage class replication/eights.
- `quotanode` attaches quota limits and soft-limit timing to a directory and is also kept in the global `quotahead` list.
- `freenode` records delayed-reuse inodes with free timestamp.

Major global structures are:

- `root`, `nodes`, `dirnodes`, `filenodes`, `maxnodeid`, and `hashelements`.
- `nodehashtab` and `edgehashtab`, both split into high/low arrays with incremental rehash state.
- `freebitmask`, `freelist`, `freetail`, and `freelastts` for inode allocation and delayed reuse.
- `trash[]` and `sustained[]` bucket arrays plus `trashspace`, `trashnodes`, `sustainedspace`, and `sustainednodes`.
- `edgeid_id_hashtab` / `edgeid_ptr_hashtab` for short-lived directory continuation lookup.
- operation counters consumed by `fs_stats`.
- `fsinfo_*` counters and message buffer used by periodic file/chunk consistency scans.

## Allocation And Indexing

The file uses custom bucket allocators instead of one `malloc` per object:

- `fsnode_*_malloc/free` allocate fixed-size node variants by type-specific union size.
- `fsedge_malloc/free` bucket edges by rounded name length.
- `symlink_malloc/free` bucket symlink target buffers.
- `chunktab_malloc/free/realloc` bucket chunk-id arrays by chunk count ranges.
- `freenode` and `quotanode` use `CREATE_BUCKET_ALLOCATOR`.

`fs_get_memusage` reports allocated/used memory for hash tables and all major allocators.

Name lookup is based on `fsnodes_hash(parent_inode, nleng, name)`, with `fsnodes_edge_add/find/delete` maintaining a lazily expanding hash table. Inode lookup uses `hash32(inode)` via `fsnodes_node_add/find/delete`. Both tables use incremental rehashing (`*_hash_move`) to amortize resize cost. Directory read continuation uses edge ids, descending from `nextedgeid`, and a small modulo hash cache; callers can recover by walking children when the cache misses.

## Inode Lifecycle

`fsnodes_get_next_id` scans `freebitmask` to allocate a new inode and expands the mask as needed. `fsnodes_free_id` appends to a timestamped freelist, and `fs_univ_freeinodes` eventually clears bitmask entries after `InodeReuseDelay`, unless the inode is still open through `of_isfileopen`; replay mode validates free/sustained counts and an inode xor checksum. `fsnodes_init_freebitmask` and `fsnodes_used_inode` support load-time reconstruction of used inode state.

`fsnodes_create_node` creates an inode under a parent, inheriting storage class/trash retention/eattrs/default ACLs from the parent as appropriate, applying umask and setgid directory behavior, incrementing storage-class references, adding the inode hash entry, and finally linking it into the parent with `fsnodes_link`.

`fsnodes_remove_node` is the final destruction path. It removes from inode hash, decrements global node counters, releases quota/xattr/ACL records, deletes chunk references through `chunk_delete_file`, releases symlink/chunktab buffers, decrements storage-class refs, invalidates data cache with `dcm_modify`, queues inode reuse, and returns the node to the right bucket allocator.

## Namespace Links, Stats, And Trash/Sustained State

`fsnodes_link` and `fsnodes_remove_edge` are the central edge mutators. They update intrusive child/parent lists, directory element counts, nlink semantics, edge hash membership, parent timestamps/eattrs, storage stats up the ancestor tree, and ctime/archive checks on children.

`fsnodes_unlink` removes a namespace entry. Last-linked regular files either:

- move to trash when retention policy applies,
- move to sustained when still open,
- or are fully removed.

Trash/sustained entries are represented as parentless `fsedge` records stored in bucket arrays, with the original path in the edge name. `fsnodes_purge` removes trash/sustained files or moves open trash files to sustained. `fsnodes_undel`, `fs_univ_trash_recover`, `fs_univ_setpath`, `fs_univ_undel`, and `fs_univ_purge` implement recovery, path editing, undelete, and deletion from these detached areas.

Subtree stats are maintained incrementally through `fsnodes_get_stats`, `fsnodes_add_stats`, `fsnodes_sub_stats`, and `fsnodes_add_sub_stats`. Real-size accounting depends on storage-class keep/archive replication factors. `fsnodes_check_realsize` repairs cached file ratios when storage class policy changes.

## Permissions, Attributes, ACLs, And Xattrs

`fsnodes_accessmode` combines uid/gid checks, `SESFLAG_IGNOREGID`, `SESFLAG_MAPALL`, `EATTR_NOOWNER`, POSIX ACL mode calculation, and read-only Windows attribute restrictions. `fsnodes_sticky_access` enforces sticky-directory deletion/rename semantics.

`fsnodes_fill_attr` serializes a fixed `ATTR_RECORD_SIZE` record for clients, including remapped display type, cache-control flags, no-xattr marker, undeletable marker, owner/group mapping, times, nlink, size/length, device ids, symlink lengths, and optional winattr. Directory size is encoded as a compact pseudo-floating 32-bit value for Linux compatibility.

Public attribute APIs include:

- `fs_getattr`, `fs_setattr`, `fs_mr_attr`, `fs_mr_length`.
- `fs_set_additional_attributes` / `fs_mr_additionalattr` for bulk winattr/eattr/xattr/FACL import-like updates.
- `fs_listxattr_leng`, `fs_listxattr_data`, `fs_setxattr`, `fs_getxattr`, `fs_mr_setxattr`.
- `fs_setfacl`, `fs_getfacl_size`, `fs_getfacl_data`, `fs_mr_setacl`.

The xattr/ACL integration relies on `xattr_*` and `posix_acl_*` helpers, while `fs_set_xattrflag`, `fs_del_xattrflag`, `fs_set_aclflag`, and `fs_del_aclflag` let those subsystems mark inode-local flags.

## Quotas And Space Reporting

Quotas are directory-attached and globally listed. `fsnodes_check_quotanode` updates soft-quota timestamps and exceeded state and logs `QUOTA` records when that state changes. `fsnodes_test_quota` checks hard limits and expired soft limits recursively through parent paths; `fsnodes_test_quota_for_uncommon_nodes` handles move/exchange cases where only uncommon destination ancestors should be charged.

`fsnodes_quota_fixspace` clamps statfs total/available/free values by applicable quota limits. `fs_quotacontrol` gets, sets, or deletes quota flags/limits with admin and read-only checks, returns current directory stats, and logs quota changes. `fs_mr_quota` replays quota state directly. `fs_getquotainfo` serializes all quota records with path, grace-period, exceeded state, limits, and current usage.

## Client-Facing Filesystem Operations

The chunk exposes the master-side operations used by matoclserv/metatools:

- Lookup/path/stat: `fs_getrootinode`, `fs_path_lookup`, `fs_statfs`, `fs_access`, `fs_lookup`, `fs_get_parents_*`, `fs_get_paths_*`, `fs_getdirpath_*`, `fs_get_dir_stats`, `fs_node_info`.
- Creation: `fs_univ_create`, `fs_mknod`, `fs_mkdir`, `fs_univ_symlink`, `fs_symlink`.
- Deletion and movement: `fs_univ_unlink`, `fs_unlink`, `fs_rmdir`, `fs_univ_move`, `fs_rename`, `fs_univ_link`, `fs_link`.
- Directory reads: `fs_readdirfull`, `fs_readdir_size`, `fs_readdir_data`.
- File chunk introspection: `fs_filechunk`, `fs_checkfile`.
- Open/read/write/truncate/repair: `fs_opencheck`, `fs_readchunk`, `fs_writechunk`, `fs_writeend`, `fs_try_setlength`, `fs_do_setlength`, `fs_end_setlength`, `fs_rollback`, `fs_repair`.
- Policy operations: `fs_getsclass`, `fs_setsclass`, `fs_gettrashretention_prepare/store`, `fs_settrashretention`, `fs_geteattr`, `fs_seteattr`, `fs_archget`, `fs_archchg`.
- Trash/sustained listing and recovery: `fs_readsustained_*`, `fs_readtrash_*`, `fs_listtrash`, `fs_listsustained`, `fs_trash_recover`, `fs_trash_remove`, `fs_settrashpath`, `fs_undel`, `fs_purge`.

Most mutating operations follow the same structure: validate session/read-only flags, resolve root-scoped inode visibility via `fsnodes_node_find_ext`, check type/name/permission/eattr/sticky/quota constraints, perform the in-memory mutation, update stats/times/archive flags, write a `changelog(...)` entry for live mode, or increment metadata version in metarestore mode.

## Snapshot, Append, And Chunk Control Flow

Snapshots are implemented by `fs_univ_snapshot` and recursive helpers. `fsnodes_snapshot_test` validates overwrite/type rules and immutable/append-only constraints. `fsnodes_snapshot_recursive_test_quota` computes additional quota usage net of objects already present at the destination. `fsnodes_snapshot` either updates matching destination objects, unlinks/recreates differing files, copies symlink/device metadata, recursively creates directories, shares chunk ids via `chunk_add_file`, optionally copies xattrs/ACLs, and preserves hardlinks through `snapshot_inodehash`.

`fs_univ_append_slice` appends a chunk slice from one file to another. Live mode converts negative half-open slice notation to absolute inclusive chunk indexes, computes quota impacts for length and storage size, then delegates to `fsnodes_append_slice_of_chunks`, which resizes the destination chunk table, copies chunk references with `chunk_add_file`, drops obsolete destination chunk refs, updates length/stats/times, and logs `APPEND`.

Chunk write/truncate paths coordinate with the chunk subsystem:

- `fs_try_setlength` performs permission and quota checks and may allocate a delayed multi-truncate chunk via `chunk_multi_truncate`, logging `TRUNC`.
- `fs_do_setlength` commits logical length changes, append reservations, and `LENGTH` changelog records.
- `fs_writechunk` reserves/modifies a chunk through `chunk_multi_modify`, updates chunk tables, extends file length to the chunk boundary when needed, updates parent stats and times, and logs `WRITE`.
- `fs_writeend` finalizes actual write length, logs `LENGTH` when file length grew, records append result length, and unlocks the chunk.
- `fs_rollback` restores a previous chunk id and unlocks on write failure.
- Replay equivalents (`fs_mr_trunc`, `fs_mr_write`, `fs_mr_rollback`, `fs_mr_repair`, `fs_mr_set_file_chunk`, `fs_mr_autoarch`) call chunk `mr` APIs or validate expected counts.

## State And Persistence Behavior

Within this line range, persistence is primarily changelog-driven. Live mutators emit textual changelog records such as `CREATE`, `UNLINK`, `MOVE`, `LINK`, `SNAPSHOT`, `APPEND`, `WRITE`, `LENGTH`, `TRUNC`, `ROLLBACK`, `SETXATTR`, `SETACL`, `QUOTA`, `ARCHCHG`, `FREEINODES`, `AUTOARCH`, and `SETFILECHUNK`. Master-replay entry points are named `fs_mr_*`; they use `SESFLAG_METARESTORE`, bypass normal client permission checks where appropriate, reconstruct the same state, compare expected inode/count/checksum values for nondeterministic operations, and call `meta_version_inc()`.

Binary metadata load/store routines begin later in `filesystem.c` after this chunk, so this chunk should be reconciled with later research for exact on-disk node/edge/free/quota serialization. Still, the in-memory invariants maintained here are the state those later routines must persist: node hash, edge relationships, detached trash/sustained edges, inode freelist/bitmask, quota list, storage-class references, chunk file references, xattr/ACL flags, and stats caches.

## Dependencies And Integration Points

Key dependencies are:

- `chunks.h`: chunk reference counting, read/write/truncate/repair, storage status, arch/trash flags, auto-arch, missing/undergoal status.
- `storageclass.h`: default/inherited storage class refs, replication/eights, archive policy and delay/min-size.
- `sessions.h`, `openfiles.h`, `appendres.h`: session flags, open-file checks for sustained files, append reservation lengths.
- `xattr.h`, `posixacl.h`: extended attributes and POSIX ACL storage plus mode/permission integration.
- `matocsserv.h`: cluster space and reserve-space availability.
- `changelog.h`, `metadata.h`: durable mutation logging and replay versioning.
- `patterns.h`: create/rename policy forcing storage class, trash retention, and eattrs.
- `globengine.h`: trash/sustained listing filters.
- `datapack.h`: wire serialization helpers.
- `datacachemgr.h`: cache invalidation when nodes are removed.
- `missinglog.h`: recording missing chunks during consistency scans.
- `main.h`, `clocks.h`: current time and keep-alive during long recursive operations.

## Risks And Edge Cases

- The code relies heavily on manual intrusive lists; edge parent/child `prev*` pointers are easy to corrupt if a new mutator bypasses `fsnodes_link` or `fsnodes_remove_edge`.
- Many stats and quota checks are precomputed manually. Bugs in size/realsize deltas can create quota bypasses or stale directory stats.
- `fsnodes_test_quota` recursively walks all parents; hardlinked files can cause quota behavior to differ from simple tree accounting.
- `fsnodes_node_find_ext` enforces root-subtree visibility; callers passing `skipancestor=1` must be reviewed carefully because it weakens subtree isolation.
- Replay wrappers depend on deterministic inode allocation and operation counts. Paths with generated unique names, snapshot counters, or freed inode checksums intentionally compare expected values and can reject metadata replay with `MFS_ERROR_MISMATCH`.
- Trash/sustained files have parentless edges whose names are paths, not basename entries. Code that assumes `edge->parent` is non-null must handle detached edges explicitly.
- Archive state is partly time-dependent and updated opportunistically on ctime/mtime/atime/length changes and in `fs_test_files`; clock regressions or overflow are guarded but still important.
- The custom allocators and hash tables assume single-threaded master mutation or external serialization; there is no local locking in this chunk.
- Several operations mutate chunk references before/after file length changes; rollback and replay paths must stay aligned with chunk subsystem semantics.

## Test Signals

Useful validation signals for this chunk include:

- Namespace tests for create, mkdir, symlink, unlink/rmdir, rename replace/exchange, hardlink limits, sticky directories, immutable/append-only/undeletable eattrs, and root-subtree scoping.
- Trash/sustained tests covering unlink of open files, empty-file trash policy, path recovery with conflicts/unique names, purge, and list filtering.
- Quota tests for create, write, truncate expansion, append slice, snapshot, hardlink, move across quota boundaries, soft-grace expiration, and statfs clamping.
- ACL/xattr tests for permission decisions, mode synchronization, default ACL inheritance, access ACL removal, trusted/security/system namespace restrictions, and replay of `SETACL`/`SETXATTR`.
- Chunk operation tests for read recovery checks, write/rollback/unlock, delayed truncate, file repair, append slice bounds including negative notation, and snapshot chunk sharing/reference counts.
- Replay tests that apply changelog records and assert expected inode ids, free-inode checksums, snapshot counters, archive-change counts, and final stats.
- Long-running consistency signals from `fs_test_files`: `fsinfo_*` counters, missing log entries, unknown chunk messages, auto-archive changelog entries, edge parent/child consistency warnings, and real-size repairs.
