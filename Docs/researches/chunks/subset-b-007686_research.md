# sources/distributed-fs/moosefs/mfsmaster/filesystem.c lines 9114-10780

## Scope And Purpose

This chunk covers the tail of MooseFS master's in-memory filesystem maintenance and the main metadata serialization/deserialization helpers for filesystem nodes, directory edges, free inode records, quotas, root creation, load-time consistency, runtime configuration reload, and module initialization.

The range starts inside `fs_test_files()`, after per-file chunk validation has already run. The visible part records automatic archive/trash flag changes, updates aggregate health counters, checks parent/child edge back-pointers, and wraps the incremental hash-table scan. It then defines the periodic trash and sustained-file purgers, edge renumeration, cleanup routines, binary metadata store/load routines, load-time orphan repair, quota/free-list persistence, new filesystem bootstrap, and `fs_strinit()` registration with the main event loop.

This is master-side metadata plumbing. It does not implement client-visible operations directly, but it is a core integration layer between runtime metadata objects (`fsnode`, `fsedge`, `freenode`, `quotanode`), the chunk subsystem, storage-class policies, open-file tracking, changelog/meta-restore replay, and the binary metadata image format.

## Important APIs, Types, And Functions

The main data types referenced by this chunk are:

- `fsnode`: in-memory inode object. The code handles directories, files, trash files, sustained files, symlinks, device nodes, FIFOs, sockets, and generic "other" nodes through `type` and the `data.*` union.
- `fsedge`: directory-name edge between a parent directory and child inode, also reused for trash/sustained pseudo-roots with `parent == NULL`.
- `statsrecord`: subtree accounting record recomputed while loading edges and propagated to parents.
- `freenode`: deleted inode record containing inode number and free timestamp.
- `quotanode`: per-directory quota definition with soft/hard inode, logical length, size, and real-size limits.
- `bio`: MooseFS buffered I/O abstraction used for metadata image reads and writes.

Key functions in this range:

- `fs_test_files()` tail: emits `AUTOARCH` changelog records when chunk-loop archival/trash flags changed, updates filesystem health counters, checks edge link consistency, and resets the incremental scan position at `noderehashpos`.
- `fs_univ_empty_trash_part()`, `fs_univ_emptytrash()`, `fs_emptytrash()`, `fs_mr_emptytrash()`: purge expired trash entries bucket-by-bucket, mark old trash entries with a trash flag when storage-class retention policy allows, and validate replay counts/checksums during meta-restore.
- `fs_univ_empty_sustained_part()`, `fs_univ_emptysustained()`, `fs_emptysustained()`, `fs_mr_emptysustained()`: purge sustained files once no open-file state references them, again with meta-restore count/checksum verification.
- `fs_renumerate_edges()`, `fs_mr_renumerate_edges()`, `fs_renumerate_edge_test()`: assign monotonically increasing edge IDs in directory traversal order when edge IDs are missing, exhausted, or detected out of order during load.
- `fs_cleanupedges()`, `fs_cleanupnodes()`, `fs_cleanupfreenodes()`, `fs_cleanup()`: tear down in-memory metadata allocations and reset global counters.
- `fs_storeedge()`, `fs_loadedge()`, `fs_storeedges()`, `fs_loadedges()`: persist and reconstruct directory/trash/sustained edge lists.
- `fs_storenode()`, `fs_loadnode()`, `fs_storenodes()`, `fs_loadnodes()`, `fs_importnodes()`: persist and reconstruct inodes, including type-specific payloads and older metadata format variants.
- `fs_storefree()`, `fs_loadfree()`: persist and reconstruct the deleted-inode reuse-delay list.
- `fs_storequota()`, `fs_loadquota()`: persist and reconstruct quota definitions.
- `fs_lostnode()`, `fs_checknodes()`, `fs_check_consistency()`: repair orphan nodes after ignored load errors by linking them into root with `lost_node_<inode>` names.
- `fs_new()`, `fs_set_root_times()`, `fs_afterload()`, `fs_reload()`, `fs_strinit()`: initialize a fresh filesystem, adjust root timestamps for replay/import, connect files to chunks after load, read config knobs, and register periodic maintenance callbacks.

## Control Flow

`fs_test_files()` is incremental. It scans a bounded slice of `nodehashtab` per call, avoids running during chunk counter work, and keeps static counters across calls. In the visible tail, file nodes that had archival/trash flags modified by `chunk_fileloop_task()` generate an `AUTOARCH` changelog entry. Files are classified into valid, under-goal, missing regular files, missing trash files, and missing sustained files; chunk totals are accumulated; real size is checked; and both parent lists and directory child lists are validated for reciprocal `child`, `parent`, `next*`, and `prev*` pointer consistency. When the scan reaches `noderehashpos`, it logs a loop completion and resets to bucket zero.

Trash cleanup is split into a small worker and a public/replay wrapper. `fs_univ_emptytrash()` chooses the next trash bucket in normal mode, or uses the replay-supplied bucket in `SESFLAG_METARESTORE` mode. A special `bid >= TRASH_BUCKETS` value scans all buckets. `fs_univ_empty_trash_part()` first purges files whose `atime`, `mtime`, and `ctime` are all older than `trashretention * 3600`, accumulating counts and an XOR inode checksum. It then performs a second pass over survivors and sets the trash flag when `mtime + 300 < ts` and the node retention is at least the storage class minimum. Normal mode writes `EMPTYTRASH` changelog records only when something changed; meta-restore mode compares replayed counts/checksum and increments the metadata version only after a match.

Sustained cleanup mirrors trash cleanup but uses open-file state as the gate. `fs_univ_empty_sustained_part()` purges nodes in a sustained bucket only when `of_isfileopen(inode) == 0`. `fs_univ_emptysustained()` advances `sustained_bid` in normal mode, supports all-bucket replay scans, writes `EMPTYSUSTAINED` changelogs in normal mode, and validates `freeinodes` plus optional checksum in meta-restore mode.

Edge renumeration is recursive. `fs_renumerate_edges()` reserves a contiguous range below `nextedgeid` for a directory's current children, assigns increasing IDs to that directory's edges, then recurses into child directories with keep-alive checks between visits. `fs_renumerate_edge_test()` runs this when `nextedgeid == EDGEID_MAX` or `edgesneedrenumeration` is set, then emits `RENUMERATEEDGES`. `fs_mr_renumerate_edges()` repeats the deterministic pass during meta-restore and rejects mismatched `expected_nextedgeid`.

Node storage is hash-table based. `fs_storenodes()` writes `maxnodeid` and `nodes`, then iterates every hash bucket up to `noderehashpos`, serializing each node and ending with a zero type marker. `fs_storenode()` writes a common header and then type-specific payload: directories/FIFOs/sockets have no extra payload, device nodes write `rdev`, symlinks write path length plus path bytes, and file/trash/sustained nodes write logical length plus the non-trailing-zero chunk table. Large chunk tables are written in 65,536-entry blocks.

Node loading reads a format-version-dependent header. `fs_loadnodes()` loads `maxnodeid` and, for metadata versions `>= 0x11`, `hashelements`; older imports use `hashelements = 1`. `fs_loadnode()` converts old type numbers for versions `<= 0x12`, allocates the right node shape, initializes xattr/ACL/keep flags to zero, increments the storage-class reference, normalizes old trash retention seconds into hours for versions `<= 0x13`, loads type-specific payload, and adds the inode to the node hash/free-bitmask accounting unless it is a duplicate. Older file formats can carry open session IDs; those call `of_mr_acquire(sessionid, inode)` while loading.

Edge storage preserves tree order. `fs_storeedges()` writes `nextedgeid`, recursively stores root directory edges pre-order, then writes trash and sustained bucket lists, and ends with a zero parent/child marker. `fs_loadedges()` reads `nextedgeid` for modern formats or forces renumeration for old formats, initializes static load cursors, and repeatedly calls `fs_loadedge()`.

`fs_loadedge()` reconstructs both directory edges and pseudo-root trash/sustained entries. It validates edge name length, child existence, parent existence, and parent type. With `ignoreflag` it can replace empty names, truncate long names, skip entries whose children are missing, or attach nodes with bad/missing parents to root. It enforces the expected serialized parent grouping by tracking `current_parent_id` and special-cases root because ignored errors can attach additional edges there. After linking an edge into child and parent lists, it updates nlink/elements counters, edge hash state, child parent list, parent subtree stats, trash/sustained space/node counters, and `edgesneedrenumeration` if edge IDs are non-increasing.

Free-list loading stores an ordered deleted-inode queue. `fs_loadfree()` reads a count, then batches up to 1024 records at a time. Timestamps must be nondecreasing; if not, normal load fails, while `ignoreflag` logs and skips the remaining free-node section. Each accepted free inode is appended to `freelist`, updates `freelastts`, and marks the inode used in the bitmask so it is not immediately reused.

Quota loading reads a count and version-dependent record size (`66` bytes for `mver == 0x10`, `70` bytes otherwise). It ignores inode zero records, requires the referenced inode to exist and be a directory, and creates quota records through `fsnodes_new_quotanode()`. Old quota records get `QUOTA_PERIOD_DEFAULT`; newer records include `graceperiod`.

Initialization and load-finalization are straightforward. `fs_new()` creates the root directory with default storage class, trash retention, mode `0777`, uid/gid zero, empty stats and children, then adds it to the inode hash. `fs_afterload()` connects loaded file chunk references back into the chunk subsystem via `fs_add_files_to_chunks()`. `fs_check_consistency()` verifies root exists, and only when `ignoreflag` is set does it scan for orphan nodes and attach them as lost nodes. `fs_strinit()` resets globals, initializes hash/memory subsystems, applies config, allocates `snapshot_inodehash`, and registers periodic callbacks.

## State And Persistence Behavior

The chunk owns several persistent metadata sections:

- Node section version `0x14`: common node header fields are type, inode, storage class, extended attributes, Windows attributes, mode, uid/gid, atime/mtime/ctime, and trash retention in hours. Type-specific data follows.
- Edge section version `0x11`: each edge stores parent inode, child inode, 64-bit edge ID, name length, and name bytes. A zero parent/child pair terminates the section.
- Free inode section version `0x10`: count followed by `(inode, free timestamp)` records in nondecreasing timestamp order.
- Quota section version `0x11`: count followed by directory inode, grace period, exceeded/flags state, timestamp, inode limits, logical length limits, size limits, and real-size limits.

Normal periodic mutations are changelogged rather than just applied in memory. Trash cleanup emits `EMPTYTRASH`, sustained cleanup emits `EMPTYSUSTAINED`, automatic archival/trash flag changes emit `AUTOARCH`, chunk-table cleanup in the unseen earlier part emits `SETFILECHUNK`, and edge renumeration emits `RENUMERATEEDGES`. The `fs_mr_*` entry points replay those operations with deterministic counts/checksums and call `meta_version_inc()` only after the local computation agrees with replay data.

Global counters and cursors maintained here include `trash_bid`, `sustained_bid`, `trashspace`, `sustainedspace`, `trashnodes`, `sustainednodes`, `nodes`, `dirnodes`, `filenodes`, `maxnodeid`, `hashelements`, `nextedgeid`, `edgesneedrenumeration`, `freelist`, `freetail`, `freelastts`, and the static `fs_test_files()` health counters. Many of these are derived from the metadata image during load, so load order matters: nodes must be loaded before edges, edges rebuild parent links and stats, free-list loading marks delayed-reuse inodes, and `fs_afterload()` later connects file chunk IDs to the chunk tables.

## Dependencies And Integration Points

This chunk depends heavily on local MooseFS master subsystems:

- Chunk subsystem: `chunk_fileloop_task()`, `chunk_count()`, `chunk_counters_in_progress()`, `missing_log_insert()`, `missing_log_swap()`, and `fs_add_files_to_chunks()` provide chunk health, archival/trash flag updates, and load-time chunk reverse links.
- Storage classes: `sclass_get_arch_mode()`, `sclass_get_arch_delay()`, `sclass_get_arch_min_size()`, `sclass_get_min_trashretention()`, and `sclass_incref()` define archival policy, trash minimum retention, and type-specific storage-class references.
- Node/edge allocators and indexes: `fsnode_*_malloc/free`, `fsedge_malloc/free`, `fsnodes_node_add/find`, `fsnodes_edge_add`, `fsnodes_used_inode`, `fsnodes_init_freebitmask`, edge/node hash cleanup/init, chunk table allocation, symlink allocation, and freenode/quotanode allocators.
- Open-file/session tracking: `of_isfileopen()` protects sustained files from deletion, and `of_mr_acquire()` restores old-format open session references.
- Changelog/meta-restore: `changelog()`, `SESFLAG_METARESTORE`, `meta_version_inc()`, and `MFS_ERROR_MISMATCH` make maintenance operations replayable and checked.
- Configuration/main loop: `cfg_get*()`, `main_reload_register()`, `main_msectime_register()`, and `main_time_register()` wire this module into master startup, reload, 100 ms structure checks, 1-second quota/trash/sustained maintenance, and 60-second free-inode recycling.

The binary persistence routines also depend on MooseFS endian helpers (`put*bit`, `get*bit`) and `bio_read()`, `bio_write()`, `bio_skip()`, and `bio_error()`. Because metadata images are versioned by the store/load function return values, changing serialized fields requires coordinated version handling rather than local struct edits.

## Risks And Edge Cases

The highest-risk code is `fs_loadedge()`, because it rebuilds both topology and accounting. It assumes normal metadata stores edges grouped by parent, and treats pre-existing children under a parent as a sequence error unless `ignoreflag` is active. Ignore-mode repair attaches some bad edges to root without generating unique names; the comment explicitly leaves uniqueness unresolved. That can interact with root special-case tail handling and should be tested with duplicate or conflicting orphan names.

Name truncation during edge load has a subtle size-risk pattern. When `nleng` exceeds the max, the code allocates a shorter edge, skips `nleng - max`, sets `e->nleng` to the max, and then reads `e->nleng` bytes. If the serialized layout is name bytes immediately after the fixed header, skipping before reading means the kept bytes are the tail of the overlong name rather than the prefix. Any compatibility or repair tooling that expects prefix truncation should verify this behavior against actual metadata images.

Meta-restore determinism depends on operation counts and XOR checksums matching exactly. Trash cleanup has a sentinel allowance for `trashflaginodes == 0xFFFFFFFF` and optional checksum allowance for zero, so older changelog formats may not validate every field. New code should preserve those compatibility paths unless the changelog format is intentionally bumped.

Time arithmetic is mostly widened for trash expiration, but not everywhere. The expiration checks cast timestamps plus retention to `uint64_t`; the later trash-flag check uses `p->mtime + 300 < ts` in 32-bit arithmetic. The archival calculation in the prefix guards overflow by checking `arch_chk_time >= reftime`. Maintenance behavior around wrapped 32-bit timestamps deserves regression coverage if timestamp handling changes.

Serialization buffers are manually sized and shared across branches. `fs_storenodes()` and `fs_loadnodes()` allocate buffers large enough for common headers, chunk blocks, old session IDs, and symlink/device payloads. Any field addition must update the store version, loader header-size logic, and buffer size expressions together. The file section also trims trailing zero chunk IDs during store; code that expects `fdata.chunks` to preserve allocated sparse tail length after reload should account for this compaction.

The cleanup functions reset global pointers and counters after freeing subsystem memory. They assume no concurrent users of the in-memory filesystem graph. Calling them outside shutdown/reload teardown would leave registered periodic callbacks pointing at reset state.

`fs_check_consistency()` only repairs orphaned nodes when `ignoreflag` is set. A normal metadata load with missing parent relationships should fail earlier in edge loading rather than silently repairing. Tests should distinguish strict load from recovery/import load.

There is a likely audit target in `fs_loadfree()`: the ignore-mode skip length for remaining free-node records is `(t-l)*1024`, while free-node records are 8 bytes each and `l` is the number of buffered records remaining, not bytes. If this path is reachable with malformed timestamp order, the skip amount may not align with the serialized section. This should be verified before relying on ignore-mode recovery of corrupted free lists.

## Test Signals

Useful test signals for this chunk include:

- Metadata round-trip tests that create directories, hard-linked files, symlinks, devices, FIFOs/sockets, trash entries, sustained files, sparse chunk tables, quotas, and free inode records, then run `fs_storenodes/fs_storeedges/fs_storefree/fs_storequota` followed by the matching load path.
- Version compatibility tests for node versions `0x10` through `0x14`, especially old flags/mode packing, old trash retention in seconds, old type conversion, and old file session ID restoration through `of_mr_acquire()`.
- Corruption/recovery tests for empty edge names, overlong names, missing child nodes, missing/bad parent nodes, parent sequence errors, duplicate node IDs, overlong symlink paths, bad free-list timestamp order, and quota records pointing at missing or non-directory inodes, each with and without `ignoreflag`.
- Meta-restore replay tests for `EMPTYTRASH`, `EMPTYSUSTAINED`, and `RENUMERATEEDGES` that check successful count/checksum matches, mismatch rejection, and metadata version increments only on accepted replay.
- Periodic maintenance tests that verify bucket cursor rotation for `trash_bid` and `sustained_bid`, all-bucket scan behavior, open-file protection for sustained files, retention-hour expiration using all three file timestamps, and trash-flag setting after the 300-second mtime delay.
- Edge ID tests that load non-increasing edge IDs, confirm `edgesneedrenumeration`, run `fs_renumerate_edge_test()`, and verify deterministic `nextedgeid` plus changelog output.
- Load-finalization tests that ensure `fs_afterload()` connects file chunks to chunk metadata and `fs_check_consistency(ignoreflag=1)` links orphan nodes under root as `lost_node_<inode>` without corrupting existing parent/child lists.
- Startup/reload tests that check `fs_strinit()` initializes all memory pools and hashes, applies config bounds for quota grace, atime mode, max hard links, and inode reuse delay, and registers `fs_test_files`, quota checking, trash cleanup, sustained cleanup, and free-inode cleanup with the expected intervals.

For operational diagnostics, important log/changelog signals are `structure error` warnings from `fs_test_files()`, `unknown chunks`, `EMPTYTRASH data mismatch`, `EMPTYSUSTAINED data mismatch`, `RENUMERATEEDGES data mismatch`, `edgeid mismatch detected - force edgeid renumeration`, `loading edge/node/free/quota` errors, and the load summary printed by `fs_printinfo()`.
