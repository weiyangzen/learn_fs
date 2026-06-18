# Group Research: group_229_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_fs_inode_h_source_fecaf565a81d

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/bcachefs-tools` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/inode.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/inode.h

## Purpose
Public inode helper header for bcachefs. It declares inode bkey validation/text/trigger operations, the normalized in-memory inode representation, inode lookup/write/create/remove helpers, inode option helpers, link-count helpers, and snapshot/subvolume identity utilities.

## Main Contents
- Bkey operation descriptors for `KEY_TYPE_inode`, `KEY_TYPE_inode_v2`, `KEY_TYPE_inode_v3`, inode generation keys, and inode allocation cursor keys.
- `struct bch_inode_unpacked`, the canonical unpacked inode view with inode number, snapshot, journal sequence, hash seed, size, sectors, version, flags, mode, and all v3 variable fields.
- `struct bkey_inode_buf`, a padded buffer large enough to pack an unpacked inode into a v3 key.
- Pack/unpack and format conversion declarations: `bch2_inode_pack()`, `bch2_inode_unpack()`, and `bch2_inode_to_v3()`.
- Lookup helpers that distinguish snapshot-specific lookup, subvolume-aware lookup, and nowarn variants.
- Inode write, fsck write, initialization, creation, removal, snapshot removal, and dead-inode cleanup declarations.
- Inline helpers for inode options, `d_type` derivation, format-specific flags/mode extraction, casefold inheritance, backpointer presence, biased nlink encoding, and root subvolume inum constants.

## Integration Notes
This header is a central dependency for namespace, xattr, quota, fsck, snapshot, and reconcile code. `namei.c` mutates `bch_inode_unpacked` values for create/link/unlink/rename; `str_hash.c` uses inode hash seed/type/casefold state; `quota.h` derives quota ids from uid/gid/project fields; `xattr.c` exposes inode options through synthetic xattrs. The link-count helpers encode bcachefs' on-disk convention where stored `bi_nlink` is biased by file type and `BCH_INODE_unlinked` represents zero visible links.

## Risks and Edge Cases
- Inode options use a +1 bias: zero means "inherit/default". Callers must use the provided helpers or can accidentally confuse unset with explicit value zero.
- `bch2_inode_nlink_set()` and `bch2_inode_nlink_get()` rely on mode-derived bias; changing mode and nlink ordering incorrectly can corrupt visible link counts.
- Snapshot-aware inode lookup is subtle: some helpers use subvolume snapshots while others accept explicit snapshot ids.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/inode_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/inode_format.h

## Purpose
Defines the on-disk inode-related bkey value formats and field/flag layouts. This file is the storage-format contract for inode keys, inode generations, inode allocation cursors, inode option ids, and inode flags.

## Main Contents
- Constants `BLOCKDEV_INODE_MAX` and `BCACHEFS_ROOT_INO`, both set to 4096.
- Packed on-disk inode formats:
  - `struct bch_inode` with hash seed, 32-bit flags, mode, and flexible fields.
  - `struct bch_inode_v2` adding journal sequence and 64-bit flags.
  - `struct bch_inode_v3` moving sectors, size, and version into fixed fields and storing mode/field start in packed flag bits.
- `struct bch_inode_generation` for inode generation tracking.
- `BCH_INODE_FIELDS_v2()` and `BCH_INODE_FIELDS_v3()` macro lists, covering timestamps, ids, nlink, generation, device, checksum/compression/replica/target options, project id, backpointer, subvolume fields, nocow, depth, 31-bit dirent offsets, casefold, and an unused EC field.
- `BCH_INODE_OPTS()` and `enum inode_opt_id`, the subset of fields exposed as inheritable inode options.
- `BCH_INODE_FLAGS()` plus bitmask accessors for string hash type, field count, v3 field start, and v3 mode.
- `struct bch_inode_alloc_cursor`, used under logged ops inode cursor namespace.

## Integration Notes
`inode.h` expands the field macros into `struct bch_inode_unpacked` and option accessors. `xattr.c` maps option ids to `bcachefs.*` xattrs. `str_hash.c` reads the packed string hash bits through the unpacked `INODE_STR_HASH` helper. Namespace code depends on the subvolume and backpointer fields defined here.

## Risks and Edge Cases
- Bits 20 and above in inode flags are shared with packed fields; new flags must not collide with hash/type/count/mode encodings.
- v1/v2/v3 formats have different fixed fields and bit widths, so validation and conversion code must keep minimum value sizes and field starts synchronized with this header.
- `bi_subvol` and `bi_parent_subvol` are documented as valid only for subvolume roots.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/inode_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.c

## Purpose
Implements persistent logged operation replay and cleanup. Logged operations are stored in the `BTREE_ID_logged_ops` btree so long-running or multi-step operations can resume after recovery and then delete their log record.

## Main Contents
- `struct bch_logged_op_fn`, mapping logged op key types to resume callbacks.
- `logged_op_fns[]`, generated from `BCH_LOGGED_OPS()` and bound to `bch2_resume_logged_op_truncate`, `bch2_resume_logged_op_finsert`, and `bch2_resume_logged_op_stripe_update`.
- `logged_op_fn()`, a linear type-to-callback lookup.
- `resume_logged_op()`, which reassembles the bkey into a mutable buffer, reports an fsck error if a supposedly clean filesystem still has logged ops, invokes the matching resume callback, and then finishes the logged op.
- `bch2_resume_logged_ops()`, which iterates the logged-ops inode range in the logged ops btree and resumes each key.
- `__bch2_logged_op_start()` and `bch2_logged_op_start()`, which allocate an empty slot and insert a logged op under no-ENOSPC commit rules.
- `bch2_logged_op_finish()`, which deletes the logged op with `no_check_rw` and `no_enospc`, escalating deletion failures to fatal filesystem error because a stale operation would remain replayable.

## Integration Notes
This file depends on individual operation resume implementations from truncate, finsert, and stripe update subsystems. Recovery invokes `bch2_resume_logged_ops()` after mount-time journal/btree setup. Callers that create logged ops are expected to hold an appropriate write reference; finish deliberately bypasses normal read/write checking so cleanup can succeed during shutdown paths.

## Risks and Edge Cases
- If `fn->resume()` returns an error it is currently ignored; the function still proceeds to `bch2_logged_op_finish()`. This may be intentional for idempotent resume callbacks, but it is a notable behavior to audit.
- Failure to delete a logged op is fatal by design.
- Logged ops on a filesystem marked clean are treated as fsck inconsistencies.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.h

## Purpose
Small public header for the logged operation subsystem.

## Main Contents
- `BCH_LOGGED_OPS()` macro listing supported logged operation families: `truncate`, `finsert`, and `stripe_update`.
- Inline `bch2_logged_op_update()`, which inserts/updates a logged op in `BTREE_ID_logged_ops` using cached iteration.
- Declarations for resuming, starting, and finishing logged operations.

## Integration Notes
`logged_ops.c` expands `BCH_LOGGED_OPS()` to build the resume dispatch table. Other subsystems use `bch2_logged_op_start()`, `bch2_logged_op_update()`, and `bch2_logged_op_finish()` around operations that must survive recovery.

## Risks and Edge Cases
- Any new logged op must be added to `BCH_LOGGED_OPS()` and must provide a matching `bch2_resume_logged_op_<name>()` symbol.
- Updates go directly to the logged ops btree; callers are responsible for transaction/commit context and write-reference requirements.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops_format.h

## Purpose
Defines the on-disk value formats and logical inode namespaces used by logged operation keys.

## Main Contents
- `enum logged_ops_inums` with logical inodes for logged ops and inode cursors.
- `struct bch_logged_op_truncate`, storing subvolume, inode number, and new file size.
- `enum logged_op_finsert_state`, tracking finsert progress through start, extent shifting, and finish states.
- `struct bch_logged_op_finsert`, storing state, subvolume, inode, destination/source offsets, and current position.
- `struct bch_logged_op_stripe_update`, storing old/new stripe indexes plus a compact old block map.

## Integration Notes
These structures are bkey values under `BTREE_ID_logged_ops`. `logged_ops.c` reassembles them generically and dispatches to operation-specific resume functions. The inum enum partitions logged op keys from inode allocation cursor keys.

## Risks and Edge Cases
- These are packed persistent recovery records; field ordering and endian annotations are part of disk compatibility.
- `old_block_map` is fixed at 16 entries for stripe update logging, so code building these keys must respect that capacity.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/namei.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/namei.c

## Purpose
Implements bcachefs transactional namespace operations and related fsck/path helpers: create, link, unlink, rename, path reconstruction from inode backpointers, dirent target repair, inherited option propagation, and casefold ancestry tracking.

## Main Contents
- Helper functions `parent_inum()` and `is_subdir_for_nlink()` for subvolume-aware parent lookup and directory link accounting.
- `bch2_create_trans()`, which creates regular inodes, tmpfiles, subvolumes, and snapshots. It validates subvolume writability, initializes/allocates new inodes or snapshots an existing subvolume root, creates child subvolumes when requested, applies ACLs, creates dirents, updates parent nlink/ctime/mtime, records inode backpointers, sets directory depth, propagates casefold flags, and writes the final inode in the child snapshot.
- `bch2_link_trans()`, which hard-links within a subvolume, increments nlink, validates inherited attrs, creates the new dirent, updates backpointer fields, and writes both directory and target inode.
- `bch2_unlink_trans()`, which resolves the dirent under the right snapshot, verifies VFS-provided target identity, checks directory emptiness, handles subvolume unlinking, decrements nlink for ordinary files, clears matching backpointers, removes the dirent with hash whiteout semantics, and updates times/nlink.
- `bch2_reinherit_attrs()`, which copies inheritable inode options from a source directory to a destination inode unless explicitly set on the destination.
- `bch2_rename_trans()`, which performs dirent rename/exchange/overwrite, handles subvolume parent updates, cross-subvolume restrictions, backpointer rewrites, inherited-option changes, directory nlink/depth changes, destination unlink semantics, ctime/mtime updates, and casefold propagation after cross-directory movement.
- `bch2_inum_to_path*()` helpers, which reconstruct paths by walking inode backpointers and printing components in reverse before flipping the print buffer.
- Fsck helpers for dirent-to-inode consistency: `bch2_check_dirent_inode_dirent()` and `__bch2_check_dirent_target()`.
- Casefold ancestry helpers: `bch2_maybe_propagate_has_case_insensitive()` and `bch2_check_inode_has_case_insensitive()`.

## Integration Notes
This file sits on top of `inode.h`, `dirent.h`, `str_hash.h`, `xattr.h`, ACL handling, and subvolume/snapshot APIs. It performs all metadata changes inside `btree_trans` transactions. Dirent creation/lookup/delete uses hash info derived from the parent inode, so namespace correctness depends on stable inode hash seed/type/casefold state across snapshots. Subvolume roots are represented as directory-looking inodes with special `DT_SUBVOL` dirents and `bi_subvol`/`bi_parent_subvol` fields.

## Risks and Edge Cases
- Cross-subvolume rename is allowed only for subvolume roots; ordinary inodes cannot move across subvolumes.
- Reinheritance failures for directories return `-EXDEV` because moving a directory into a parent with different inherited options would require recursively updating descendants.
- Path reconstruction depends on inode backpointers and gracefully emits disconnected markers unless `INUM_TO_PATH_FAIL_ON_ERR` is set.
- Fsck repair can update inode backpointers, remove duplicate directory links, or rewrite wrong dirent `d_type`; callers must be prepared for transaction restarts.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/namei.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/namei.h

## Purpose
Public declarations and small inline consistency helpers for bcachefs namespace operations.

## Main Contents
- Create flags for tmpfile, subvolume, snapshot, and read-only snapshot creation.
- Transactional operation declarations: `bch2_create_trans()`, `bch2_link_trans()`, `bch2_unlink_trans()`, and `bch2_rename_trans()`.
- Inherited attribute helper declaration `bch2_reinherit_attrs()`.
- Inode-to-path conversion declarations, including subvolume-bounded and snapshot-specific variants.
- Dirent target consistency helpers:
  - `dirent_points_to_inode_nowarn()` checks whether a dirent target matches an unpacked inode, including subvolume dirents.
  - `inode_points_to_dirent()` checks inode backpointer fields against a dirent position.
  - `bch2_check_dirent_target()` fast-paths matching type/backpointer and calls the full repair/check implementation otherwise.
- Casefold ancestry declarations.

## Integration Notes
VFS operation code, recovery, and fsck code call these transaction-level helpers rather than manipulating dirents/inodes directly. The inline dirent checks encode the expected relationship between `DT_SUBVOL`, child subvolume ids, ordinary inode numbers, inode `d_type`, and inode backpointer fields.

## Risks and Edge Cases
- `dirent_points_to_inode_nowarn()` returns a bcachefs typed ENOENT if a dirent and inode disagree; callers that use it during fsck should decide whether mismatch is repairable.
- The inline fast path in `bch2_check_dirent_target()` assumes both backpointer and `d_type` match; all other cases go through the heavier implementation in `namei.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota.c

## Purpose
Implements bcachefs quota format validation, superblock quota settings, in-memory quota accounting, quota limit enforcement, mount-time quota reconstruction, and Linux `quotactl_ops` integration.

## Main Contents
- Text labels for user/group/project quota types and space/inode counters.
- Superblock quota field operations:
  - `bch2_sb_quota_validate()` checks field size.
  - `bch2_sb_quota_to_text()` prints flags, timelimits, and warnlimits.
- Quota bkey operations:
  - `bch2_quota_validate()` rejects quota keys whose inode position is outside `QTYP_NR`.
  - `bch2_quota_to_text()` prints hard/soft limits for space and inode counters.
- Under `CONFIG_BCACHEFS_QUOTA`, debugging text helpers for `qc_info` and `qc_dqblk`.
- `for_each_set_qtype()` iteration over enabled quota types from mount options.
- Limit checking and notification:
  - `bch2_quota_check_limit()` handles hardlimit, softlimit, timer, warning issue/clear, and `KEY_TYPE_QUOTA_NOCHECK`.
  - `flush_warnings()` sends kernel quota netlink warnings.
- Accounting APIs:
  - `bch2_quota_acct()` charges or uncharges a single counter across all enabled qtypes.
  - `bch2_quota_transfer()` moves space and one inode between qids for selected qtypes.
- `__bch2_quota_set()` loads persistent limits from quota bkeys into in-memory radix tables and optionally updates timer/warn fields.
- Filesystem lifecycle: `bch2_fs_quota_init()`, `bch2_fs_quota_exit()`, `bch2_fs_quota_read()`.
- Mount-time reconstruction: reads superblock limits, quota btree keys, then scans all inode snapshots and charges live master-subvolume inodes.
- Quota control operations for enable, disable, remove, get state, set info, get quota, get next quota, and set quota.

## Integration Notes
Quota ids come from `bch_qid()` in `quota.h`, derived from inode uid/gid/project. Persistent hard/soft limits live in `BTREE_ID_quotas`, while global grace/warn limits live in the superblock quota field. Runtime usage is maintained in `c->quotas[type].table` radix tables protected by per-type mutexes. `bch2_quotactl_operations` exposes this implementation to the VFS.

## Risks and Edge Cases
- Space values in VFS quota structs are bytes while internal accounting uses sectors; conversions shift by 9.
- `bch2_quota_transfer()` passes `dst_q[i]->c[...] .v + delta` as the delta argument to `bch2_quota_check_limit()`, even though `bch2_quota_check_limit()` itself adds `qc->v + v`. This deserves audit because it appears to double-count existing destination usage during limit checks.
- Accounting is enabled only when corresponding mount options are active; enabling enforcement without accounting is rejected.
- Quota scan skips inodes deleted in a given snapshot by treating ENOENT as an advance condition.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota.h

## Purpose
Public quota header for bcachefs quota bkey operations, id derivation, enabled-type calculation, accounting APIs, and quotactl integration.

## Main Contents
- Declaration of `bch_sb_field_ops_quota`.
- Bkey validation/text declarations and `bch2_bkey_ops_quota` descriptor with minimum value size 32 bytes.
- `bch_qid()`, which derives user/group/project quota ids from an unpacked inode. Project id uses the inode option +1 bias, so stored zero maps to project id zero and nonzero maps to `bi_project - 1`.
- `enabled_qtypes()`, which produces a bitmask from filesystem options `usrquota`, `grpquota`, and `prjquota`.
- Under `CONFIG_BCACHEFS_QUOTA`, declarations for accounting, transfer, lifecycle, mount-time read, and `bch2_quotactl_operations`.
- Stub no-op implementations when quota support is disabled.

## Integration Notes
Callers can unconditionally call `bch2_quota_acct()` and `bch2_quota_transfer()` because the header provides no-op stubs for builds without quota support. Inode and namespace code use `bch_qid()` to charge ownership changes consistently with project-id encoding.

## Risks and Edge Cases
- The project-id bias must remain consistent with inode option handling in `inode.h` and synthetic xattr handling in `xattr.c`.
- Disabled quota builds silently skip accounting and quota initialization.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota_format.h

## Purpose
Defines persistent quota bkey and superblock quota field formats.

## Main Contents
- `enum quota_types`: user, group, project, and count.
- `enum quota_counters`: space, inode, and counter count.
- `struct bch_quota_counter`, storing hardlimit and softlimit.
- `struct bch_quota`, the quota bkey value containing counters for space and inodes.
- Superblock quota field structures:
  - `struct bch_sb_quota_counter` with timelimit and warnlimit.
  - `struct bch_sb_quota_type` with flags and counter limits.
  - `struct bch_sb_field_quota` containing settings for all quota types.

## Integration Notes
`quota.c` validates, prints, loads, and updates these structures. Quota btree keys use key position inode as quota type and offset as qid. Superblock quota fields store grace/warning policy, while btree quota values store per-qid hard/soft limits.

## Risks and Edge Cases
- Endian annotations are part of the disk format and must be preserved.
- `struct bch_sb_field_quota` validation expects the full structure size.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/quota_types.h

## Purpose
Defines in-memory quota ids, accounting modes, counters, radix tables, per-type locks, and superblock-derived runtime limits.

## Main Contents
- `struct bch_qid`, an array of qids indexed by quota type.
- `enum quota_acct_mode` with modes for prealloc, warn, and nocheck accounting.
- `struct memquota_counter`, containing current usage, hard/soft limits, grace timer, warning count, and warning-issued bitset.
- `struct bch_memquota`, grouping space/inode counters.
- `bch_memquota_table`, a generic radix tree mapping qid to in-memory quota counters.
- `struct quota_limit`, carrying timelimit and warnlimit.
- `struct bch_memquota_type`, grouping limits, radix table, and mutex for one quota type.

## Integration Notes
`struct bch_fs` owns an array of `bch_memquota_type` instances. `quota.c` allocates radix entries on demand and locks quota types in stable nested order when charging or transferring usage.

## Risks and Edge Cases
- `memquota_counter.v` is unsigned but accounting deltas are signed; limit paths must prevent underflow.
- Warning-issued state is in-memory and distinct from persistent warning counters/timers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/quota_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.c

## Purpose
Implements hash-info initialization and fsck repair for bcachefs string-key hash tables. This shared layer supports hashed dirents and xattrs, including casefold state, snapshot hash consistency, duplicate handling, wrong-offset repair, and whiteout-safe movement.

## Main Contents
- `__bch2_hash_info_init()` builds `struct bch_hash_info` from an inode: snapshot, hash type, 31-bit offset flag, casefold encoding pointer, and hash seed. Old siphash derives the full key by SHA-256 hashing the stored seed.
- `bch2_hash_info_init()` rejects casefolded directories when the filesystem lacks casefold encoding.
- `bch2_dirent_has_target()` checks whether a dirent target still exists, handling subvolume and ordinary inode targets differently.
- `bch2_fsck_rename_dirent()` renames a duplicate dirent to a `.fsck_renamed-N` name and updates backpointers.
- `hash_pick_winner()` decides which duplicate hash key survives, preferring identical values, snapshot ordering, and dirents with valid targets.
- `bch2_repair_inode_hash_info()` repairs per-snapshot inode hash seed/type mismatches by copying root hash info into the bad inode and writing it through fsck.
- `check_inode_hash_info_matches_root()` verifies hash info consistency across snapshot versions before repairing a key.
- `str_hash_dup_entries()`, `bch2_str_hash_repair_key()`, and `str_hash_bad_hash()` handle duplicate or misplaced hash keys by moving keys to their proper hash position, inserting snapshot whiteouts, deleting stale entries, and committing lazy fsck updates.
- `str_hash_check_dirent()` repairs dirent casefold mismatch by rebuilding the dirent under the current hash info.
- `__bch2_str_hash_check_key()` is the main fsck validation path for a single hash-table key.

## Integration Notes
`str_hash.h` provides inline lookup/set/delete primitives; this file provides the slower repair side. `dirent` and `xattr` subsystems provide `bch_hash_desc` instances with hash/cmp functions. Snapshot handling is central: all versions of a directory inode must use identical hash type and seed, or lookup across snapshots can break.

## Risks and Edge Cases
- Repair can move keys to lower positions; callers track `updated_before_k_pos` to know whether iteration must revisit earlier keys.
- Duplicate dirent repair may rename one valid target rather than delete it when both point to valid inodes.
- Hash mismatches may actually be inode hash-info mismatches, so repairs first validate snapshot root hash state before moving keys.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.h

## Purpose
Generic inline framework for bcachefs string-key hash tables. It abstracts hash type selection, hash computation state, btree lookup, collision probing, insert/replace semantics, whiteout-aware delete, and fsck check dispatch.

## Main Contents
- `bch2_str_hash_opt_to_type()`, mapping mount/inode hash options to concrete hash type, including old/new siphash feature selection.
- `struct bch_hash_info`, carrying inode snapshot, hash type, 31-bit truncation flag, casefold encoding, and keyed hash seed.
- Hash context helpers:
  - `bch2_str_hash_init()`
  - `bch2_str_hash_update()`
  - `__bch2_str_hash_end()`
  - `bch2_str_hash_end()`
- `struct bch_hash_desc`, the per-table descriptor containing btree id, key type, hash functions, comparison functions, and optional visibility predicate.
- `is_visible_key()`, which filters keys by type and snapshot/subvolume visibility.
- Lookup helpers:
  - `bch2_hash_lookup_in_snapshot()`
  - `bch2_hash_lookup()`
  - `bch2_hash_hole()`
- Collision/whiteout helpers:
  - `bch2_hash_needs_whiteout()` scans forward to decide whether deleting a slot needs a whiteout.
  - `bch2_hash_set_or_get_in_snapshot()` probes from the hash offset, detects duplicates/collisions, records first reusable slot, supports must-create and must-replace flags, and either updates or returns the existing key.
  - `bch2_hash_set_in_snapshot()` and `bch2_hash_set()` wrap insertion.
  - `bch2_hash_delete_at()` and `bch2_hash_delete()` delete by position or key, emitting whiteouts when needed.
- Fsck repair declarations and fast-path `str_hash_key_needs_check()` / `bch2_str_hash_check_key()`.

## Integration Notes
Dirents and xattrs use this file by supplying `bch_hash_desc` instances. The btree key position offset is the computed hash, but collisions are resolved by linear probing through slots in the same inode range. Snapshot-aware visibility and whiteouts are required so deletions do not expose hidden older entries.

## Risks and Edge Cases
- `cmp_key` and `cmp_bkey` return true for inequality; this convention is easy to misread.
- `STR_HASH_must_create` returns the found existing key to signal EEXIST in wrappers; callers must handle the returned bkey correctly.
- 31-bit hashing applies only when the caller allows it and the inode has the 31-bit dirent offset flag.
- Whiteout decisions depend on forward scanning; incorrect hash functions or comparison callbacks can corrupt lookup semantics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/xattr.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/xattr.c

## Purpose
Implements bcachefs extended attribute storage, lookup, validation, VFS xattr handlers, xattr listing, POSIX ACL value printing, and synthetic `bcachefs.*` / `bcachefs_effective.*` xattrs for inode options.

## Main Contents
- Xattr hash descriptor implementation:
  - Hash includes xattr type byte plus name.
  - Key and bkey comparison check type, name length, and name bytes.
  - `bch2_xattr_hash_desc` targets `BTREE_ID_xattrs` with `KEY_TYPE_xattr`.
- `bch2_xattr_validate()`, checking value size bounds, known type, and absence of NUL bytes in names.
- `bch2_xattr_to_text()`, which prints namespace prefix, name, value, and ACL text for POSIX ACL xattrs.
- `bch2_xattr_get_trans()`, a transaction-level lookup using inode hash info and `bch2_hash_lookup()`.
- `bch2_xattr_set()`, the exported transaction-level setter/delete path. It checks subvolume writability, peeks and updates inode ctime, writes the inode to ensure snapshot presence, then inserts/replaces/deletes the xattr through the generic string hash layer.
- Listing helpers:
  - `__bch2_xattr_emit()` emits prefix+name NUL-terminated list entries.
  - `bch2_xattr_emit()` respects handler list permissions.
  - `bch2_xattr_list_bcachefs()` lists defined and effective inode options.
  - `bch2_xattr_list()` walks the xattr btree for an inode and appends synthetic bcachefs option names.
- VFS handlers for user, trusted, security, bcachefs, and bcachefs_effective namespaces.
- `bcachefs.*` option get/set code maps option names to inode option ids, parses option values, runs option hooks, updates project id/casefold/31-bit dirent flags, writes the inode under update lock, and notifies directory casefold changes.
- Type-to-handler map includes POSIX ACL access/default nop handlers for stored ACL xattrs.

## Integration Notes
Stored xattrs are hashed by inode hash info and live in `BTREE_ID_xattrs`. Synthetic bcachefs option xattrs operate directly on inode fields rather than xattr btree keys. ACL code stores ACLs through this same xattr format. The xattr setter deliberately writes the inode ctime in the same transaction so snapshot-visible xattrs have a matching inode key.

## Risks and Edge Cases
- Validation allows a value size up to `xattr_val_u64s(name_len, val_len + 4)` with an in-code "XXX why +4 ?" note.
- `Inode_opt_inodes_32bit` can only be changed after confirming the directory is empty, because existing dirents would otherwise require rehashing.
- `bcachefs_effective.*` set is a no-op because effective values are inherited.
- Trusted xattrs list only for callers with `CAP_SYS_ADMIN`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/xattr.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/xattr.h

## Purpose
Public xattr header defining bcachefs xattr bkey operations, xattr value layout helpers, search keys, exported transaction setter, list function, and VFS handler array.

## Main Contents
- Declaration of `bch2_xattr_hash_desc`.
- Bkey validation/text declarations and `bch2_bkey_ops_xattr` with minimum value size 8 bytes.
- `xattr_val_u64s()`, computing the number of u64s needed for name+value payload.
- `xattr_val()` macro, returning a pointer to the value bytes after the name.
- `struct xattr_search_key` and `X_SEARCH()` initializer for hash lookups.
- Forward declarations for VFS and bcachefs inode/hash types.
- `bch2_xattr_set()`, exported for both filesystem code and migration tooling.
- `bch2_xattr_list()` and `bch2_xattr_handlers[]`.

## Integration Notes
`xattr.c` implements the hash descriptor and handlers declared here. `acl.c` and migration/tooling paths can call `bch2_xattr_set()` without going through VFS xattr handlers. The value helpers encode the packed `struct bch_xattr` flexible-array layout from `xattr_format.h`.

## Risks and Edge Cases
- `xattr_val()` relies on `x_name_len`; callers must validate bounds before dereferencing arbitrary on-disk values.
- `xattr_val_u64s()` must stay synchronized with `struct bch_xattr` layout.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/xattr_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/fs/xattr_format.h

## Purpose
Defines persistent xattr namespace indexes and the packed on-disk xattr value format.

## Main Contents
- Xattr type indexes:
  - user
  - POSIX ACL access
  - POSIX ACL default
  - trusted
  - security
- `struct bch_xattr`, containing value header, xattr type, name length, little-endian value length, and a flexible byte array containing name followed by value.
- Comment documenting that adding `__counted_by(x_name_len)` previously caused a false positive out-of-bounds write detection, so the flexible array remains unannotated.

## Integration Notes
`xattr.h` provides helpers for computing value sizes and locating the value portion. `xattr.c` validates type/name/value lengths and maps type indexes to VFS xattr handlers.

## Risks and Edge Cases
- Name and value share one flexible byte array; all size validation must account for both.
- The type index namespace is persistent and must remain stable for disk compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/fs/xattr_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/chardev.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/chardev.c

## Purpose
Implements the bcachefs character-device ioctl interface. It dispatches global and per-filesystem ioctls, handles device management commands, exposes usage/accounting/superblock queries, runs asynchronous data jobs via file descriptors, and registers `/dev/bcachefs-ctl` plus per-filesystem control devices.

## Main Contents
- Device lookup helpers:
  - `bch2_device_lookup()` resolves by member index or user path and returns a normal device ref.
  - `bch2_device_lookup_outer()` converts to `ref_outer` for operations that acquire `state_lock`, avoiding removal deadlocks.
- `bch2_global_ioctl()` currently handles offline fsck.
- `bch2_ioctl_query_uuid()` returns filesystem user UUID.
- `bch2_copy_ioctl_err_msg()` copies a printbuf error message to v2 ioctl error buffers and appends the error string when needed.
- Device management ioctl handlers for add, remove, online, offline, set-state, resize, and resize-journal, with v1/v2 variants, privilege checks, flag validation, device lookup, and error propagation.
- Asynchronous data job support:
  - `struct bch_data_ctx`
  - `bch2_data_thread()`
  - release/read file operations
  - `bch2_ioctl_data()`, which starts a `thread_with_file` and reports progress events.
- Query handlers:
  - `bch2_ioctl_fs_usage()`
  - `bch2_ioctl_query_accounting()`
  - legacy and v2 device usage
  - `bch2_ioctl_read_super()`
  - `bch2_ioctl_disk_get_idx()`
- `bch2_fs_ioctl()` main command switch. A small set of read/query ioctls can run before `BCH_FS_started`; mutation and deeper query commands require started state.
- Character-device registration:
  - global IDR mapping minors to `struct bch_fs`
  - file ops for unlocked ioctl/open
  - per-filesystem device create/destroy
  - module-level init/exit.

## Integration Notes
This is the userspace control surface for `dev.c`, journal resize, data movement/scrub, fsck, accounting, counters, and superblock reads. It relies heavily on typed bcachefs errors but returns Linux errnos through `bch2_err_class()`. The `ref_outer` lookup variants match the lifetime rules documented in `dev.c`: callers that may block on `state_lock` cannot hold a normal `ca->ref` because removal drains that ref under the same lock.

## Risks and Edge Cases
- Most device mutation ioctls require `CAP_SYS_ADMIN`; query functions still validate started state and buffer sizes.
- V2 ioctls copy detailed error strings back to userspace; v1 ioctls mostly log errors.
- `bch2_ioctl_disk_resize_v2()` uses normal device refs while the older resize path uses outer refs, even though resize takes `state_lock`; this is worth checking against the deadlock comment near `bch2_device_lookup_outer()`.
- Async data jobs hold a write ref and must release it in the worker/error cleanup path.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/chardev.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/chardev.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/chardev.h

## Purpose
Public header for bcachefs character-device ioctl integration, with no-op stubs when filesystem support is disabled.

## Main Contents
- Under normal builds:
  - `bch2_copy_ioctl_err_msg()`
  - `bch2_fs_ioctl()`
  - per-filesystem chardev init/exit
  - module/global chardev init/exit
- Under `NO_BCACHEFS_FS`:
  - `bch2_fs_ioctl()` returns `-ENOTTY`
  - init/exit functions are empty success/no-op stubs.

## Integration Notes
Filesystem initialization calls the init/exit functions to publish or remove control devices. VFS ioctl paths and global character-device file ops call `bch2_fs_ioctl()` for command dispatch.

## Risks and Edge Cases
- Callers must tolerate `-ENOTTY` in `NO_BCACHEFS_FS` builds.
- The header intentionally hides all implementation details; lifetime and permission checks live in `chardev.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/chardev.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/dev.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/dev.c

## Purpose
Implements bcachefs multi-device management: membership validation, splitbrain checks, device allocation/free, sysfs linkage, block-device attach/detach, device state transitions, add/remove/online/offline, resize, mount-time resize allocation, lookup by name, and block-layer holder callbacks for dead/sync events.

## Main Contents
- Long embedded documentation for multi-device behavior, per-device metadata, state meanings, durability/caching, add/remove/online/offline workflows, hot-remove handling, data restrictions, degraded mode, resize, errors, and self-healing.
- Read/write reference name arrays generated from `BCH_DEV_READ_REFS()` and `BCH_DEV_WRITE_REFS()`.
- `bch2_devs_list_to_text()` prints device names for a compact device list.
- Membership helpers:
  - `bch2_dev_may_add()` checks block size and bucket size compatibility.
  - `bch2_dev_to_fs()` finds a mounted filesystem by `dev_t`.
  - `bch2_dev_in_fs()` verifies UUID membership, removed-device state, block size, member sequence, superblock sequence/write-time, and splitbrain conditions.
- Startup/shutdown helpers:
  - `bch2_dev_io_ref_stop()`
  - `__bch2_dev_read_only()`
  - `__bch2_dev_read_write()`
  - `bch2_dev_unlink()`
  - `bch2_dev_free()`
  - `__bch2_dev_offline()`
  - `bch2_dev_sysfs_online()`
- Allocation/attach helpers:
  - `__bch2_dev_alloc()` allocates and initializes refs, kobject, IO latency stats, journal/discard/bucket state, error counters, and per-cpu IO counters from a superblock member.
  - `bch2_dev_attach()` installs a device in `c->devs`.
  - `bch2_dev_alloc()` allocates an existing member at mount/recovery.
  - sysfs identity readers fill device name/model/serial.
  - `__bch2_dev_attach_bdev()` and `bch2_dev_attach_bdev()` attach an open block device, initialize journal state, set read refs, mark it online, and wake reconcile.
- State management:
  - `bch2_dev_state_allowed()` verifies leaving RW does not violate write requirements unless forced.
  - `__bch2_dev_set_state()` handles read-only transition, superblock state update, allocator re-add for RW, and reconcile scans for pending/device/stripes.
  - `bch2_dev_set_state()` wraps it under `state_lock` and removal checks.
- Device removal:
  - `__bch2_dev_remove()` marks the device removing, moves it to evacuating, drops data by backpointers or legacy scanning, verifies usage is empty, flushes journal pins, offlines the device, removes allocation metadata, flushes again, GC-checks replicas, removes it from `c->devs`, and drains refs.
  - `bch2_dev_remove()` frees the device outside `state_lock` and marks the superblock member deleted or UUID-zeroed.
- Device add/online:
  - `bch2_dev_add_initialize()` advances partially initialized new devices through usage init, superblock marking, freespace init, and journal allocation.
  - `bch2_dev_add()` reads a new device superblock, allocates a member slot, attaches it, writes updated superblocks, initializes runtime metadata, invalidates device cache, emits UUID uevent, and wakes reconcile.
  - `bch2_dev_online()` reattaches an existing member, validates membership/splitbrain, marks device superblock, restores RW allocator state, initializes freespace/journal if needed, updates last mount, and schedules pending reconcile.
- Offline/resize:
  - `bch2_dev_may_offline()` checks whether remaining devices can read/write the filesystem.
  - `bch2_dev_offline()` validates state and calls `__bch2_dev_offline()`.
  - `bch2_dev_resize()` grows a device, updates bucket arrays, marks device superblock, writes new bucket count, initializes new freespace, recalculates capacity, and wakes reconcile.
  - `__bch2_dev_resize_alloc()` performs mount-time allocation accounting and freespace initialization for newly added buckets.
- `bch2_dev_lookup()` finds devices by name or `/dev/`-stripped path.
- Block holder ops:
  - `bch2_fs_bdev_mark_dead()` handles block-layer dead-device events by syncing/evicting when possible, emergency read-only fallback, and offlining the bcachefs device.
  - `bch2_fs_bdev_sync()` syncs filesystem on holder sync request.

## Integration Notes
This file is the implementation behind chardev device ioctls and mount/recovery device setup. It coordinates allocator state, journal state, discard, EC stripe flushing, reconcile scans, replicas accounting, superblock writes, sysfs, block holder callbacks, and global filesystem list membership. The code has careful lifetime separation between normal `ca->ref`, `ref_outer`, read/write IO refs, and `state_lock` to avoid deadlocks during removal and error work.

## Risks and Edge Cases
- `bch2_dev_may_offline()` builds `new_rw_devs` but clears `ca->dev_idx` from `new_devs` twice, not from `new_rw_devs`. This appears inconsistent with `bch2_dev_state_allowed()` and could make write-availability checks for offline overly permissive.
- Device removal intentionally consumes the caller's `ref_outer`; callers must not use `ca` afterward unless documented.
- Splitbrain checks can be bypassed by `no_splitbrain_check`, but the code logs the detected mismatch.
- Removal has several durability barriers: stripe flush, btree interior updates flush, journal pin flushes, journal flushes, allocation metadata removal, and replica GC. Skipping one could leave stale pointers or superblock replica entries.
- Shrinking is explicitly unsupported.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/dev.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/dev.h

## Purpose
Public device-management API for bcachefs initialization, online/offline state, add/remove/resize operations, identity reading, and block holder integration.

## Main Contents
- `bch2_devs_list_to_text()` for printing device lists.
- Lookup/membership helpers: `bch2_dev_to_fs()` and `bch2_dev_in_fs()`.
- Low-level lifecycle helpers: IO ref stop, unlink, free, offline, sysfs online, identity read, allocation, and block-device attach.
- State transition helpers: `bch2_dev_state_allowed()`, `__bch2_dev_set_state()`, and `bch2_dev_set_state()`.
- User-visible management operations: add initialize, remove, add, online, offline, resize.
- Mount-time resize allocation helper `__bch2_dev_resize_alloc()`.
- Name lookup `bch2_dev_lookup()`.
- `bch2_sb_handle_bdev_ops`, the block-layer holder callbacks.

## Integration Notes
`chardev.c` calls the user-visible management functions. Mount/recovery code uses allocation and attach functions. Error handling uses `__bch2_dev_set_state()` to demote devices after sustained write errors.

## Risks and Edge Cases
- Functions that take `state_lock` must be paired with the correct device reference type; the implementation distinguishes normal refs from `ref_outer`.
- `__bch2_dev_set_state()` assumes caller already holds `state_lock`, while `bch2_dev_set_state()` acquires it.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/dev.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/dev_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/dev_types.h

## Purpose
Defines lightweight device-init data structures shared across bcachefs initialization and device management code.

## Main Contents
- `struct bch_sb_handle_holder`, linking an opened block-device holder back to a `struct bch_fs`.
- `struct bch_sb_handle`, the opened superblock/device handle. It stores the loaded superblock, block device file and pointer, display name, scratch bio, holder, buffer size, block open mode, layout/bio/fs-superblock flags, and sequence.
- `struct bch_devs_mask`, a bitmask over possible superblock member slots.
- `struct bch_devs_list`, a compact list of device indexes capped by bkey pointer count.

## Integration Notes
`bch_sb_handle` is passed among superblock IO, device add/online, attach, and mount discovery code. The holder pointer is used by block holder callbacks in `dev.c` to recover the owning filesystem during block-layer events. Device masks represent online/RW/allowed member sets.

## Risks and Edge Cases
- `bch_sb_handle` ownership is transfer-like in attach paths: `__bch2_dev_attach_bdev()` copies the handle into `ca->disk_sb` and clears the source handle.
- The bitmask size depends on `BCH_SB_MEMBERS_MAX`; list storage depends on `BCH_BKEY_PTRS_MAX`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/dev_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/error.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/error.c

## Purpose
Implements bcachefs error policy, fsck error reporting/decision logic, fatal/inconsistent/topology handling, IO error accounting work, interactive fsck prompts, repeated-error memoization/rate limiting, bkey validation error conversion, contextual inode/offset error text, and filesystem error state initialization.

## Main Contents
- `__bch2_log_msg_start()` initializes a printbuf with bcachefs log prefix/indentation.
- Inconsistent error handling:
  - `__bch2_inconsistent_error()` sets `BCH_FS_error` and applies `errors=` policy: continue, fix_safe/read-only, or panic.
  - `bch2_fs_inconsistent()` and `bch2_trans_inconsistent()` format messages and include transaction update details when available.
- Topology/fatal errors:
  - `__bch2_topology_error()` sets topology-error flag and either emergency-ROs or schedules explicit topology recovery.
  - `bch2_fatal_error()` emits a fatal message and triggers emergency read-only.
- IO error handling:
  - `bch2_io_error()` increments per-device persistent error counters, starts write-error timing, queues long work with `ref_outer`.
  - `bch2_io_error_work()` demotes a device to read-only after sustained write errors when possible, otherwise makes the filesystem emergency read-only.
- Interactive fsck prompt support for kernel stdio redirect and userspace tools builds.
- `fsck_err_get()`, `count_fsck_err_locked()`, and `__bch2_count_fsck_err()` track per-error id count, last message, repeated transaction-restart duplicates, and ratelimiting.
- `bch2_fsck_err_opt()` converts fsck flags plus filesystem options into typed repair/ignore/ask/exit decisions.
- `__bch2_fsck_err()` is the central fsck error engine. It formats messages, honors silent-error bits, handles autofix policy, runtime self-healing policy, fsck ask/yes/no/exit modes, transaction relock around prompts, repair action text, logging, state flags for fixed/not-fixed errors, and transaction log strings.
- `__bch2_bkey_fsck_err()` wraps invalid bkey validation failures and usually converts them to "delete key" fsck decisions outside write/commit validation.
- Flush/free functions release tracked fsck error messages.
- `bch2_inum_offset_err_msg_trans_norestart()` and wrapper add path/inode/offset context to errors.
- `bch2_fs_errors_init_early()`, `bch2_fs_errors_init()`, and `bch2_fs_errors_exit()` initialize and clean error list/count structures.

## Integration Notes
`error.h` macros used throughout the filesystem eventually route here. `namei.c`, `str_hash.c`, `quota.c`, `xattr.c`, and logged-op replay all use fsck/inconsistent helpers. Device error demotion calls `__bch2_dev_set_state()` from `dev.c`, with `ref_outer` lifetime rules matching device removal. Bkey validators use `__bch2_bkey_fsck_err()` to report corrupt on-disk keys with validation context.

## Risks and Edge Cases
- `__bch2_fsck_err()` must sometimes unlock a transaction for user input and relock afterward; callers must handle transaction restart returns.
- Silent errors set `BCH_FS_errors_fixed_silent` and return fix/ignore without printing.
- Runtime self-healing is restricted by `errors=` policy; some autofixable errors still force shutdown under `errors=ro`.
- IO error work is intentionally never cancelled; device free drains `ref_outer` instead.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/error.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/error.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/error.h

## Purpose
Public error-handling header for bcachefs. It declares inconsistent/topology/fsck/fatal/IO error APIs and defines the macros used throughout the codebase to report, fix, ignore, or propagate filesystem consistency errors.

## Main Contents
- Inconsistent error API:
  - `__bch2_inconsistent_error()`
  - `bch2_inconsistent_error()`
  - `bch2_fs_inconsistent()`
  - `bch2_trans_inconsistent()`
  - condition macros for fs/trans inconsistent checks.
- Topology error declarations.
- `struct fsck_err_state`, storing per-error id, count, ratelimit flag, cached return decision, all-yes/all-no fix mode, and last message.
- Fsck counting and option decision declarations.
- `__bch2_fsck_err()` and `bch2_fsck_err()` generic macro that accepts either `struct bch_fs *` or `struct btree_trans *`.
- Macro families:
  - `fsck_err`, `mustfix_fsck_err`, `log_fsck_err`
  - `_on` condition variants
  - `ret_fsck_err`, `ret_log_fsck_err` return-on-error variants
  - wrappers that convert typed fsck fix/ignore errors into boolean "should fix" decisions.
- Bkey validation fsck error wrapper macros that delete invalid bkeys after a fix/ignore decision.
- Fatal error API and condition macro.
- IO error declarations, latency accounting hook/stub, and inline IO success/failure completion accounting.
- Contextual inum/offset error message declarations.
- Error subsystem lifecycle declarations.

## Integration Notes
This header is used broadly by validators, fsck passes, btree code, namespace code, xattr/quota validation, logged op replay, and IO paths. It gives call sites compact macros while keeping policy centralized in `error.c`. The type-dispatch macro for `bch2_fsck_err()` lets code pass either a filesystem or transaction object.

## Risks and Edge Cases
- `fsck_err_on()` warns if passed a filesystem pointer while a btree transaction is active in the current task, because interactive prompts need transaction unlock/relock support.
- Bkey fsck macros currently handle repair by deleting the entire key; the comment notes this may change.
- Macro control flow uses `goto fsck_err` and `return` variants; call sites must provide the expected labels/variables.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/error.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/error_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/error_types.h

## Purpose
Defines the `struct bch_fs_errors` state embedded in the filesystem object.

## Main Contents
- Includes superblock error counter types.
- `struct bch_fs_errors` fields:
  - `msgs`, a list of tracked fsck error message states.
  - `msgs_lock`, protecting the message list.
  - `msgs_alloc_err`, recording allocation failure while tracking messages.
  - `counts`, CPU-side superblock error counters.
  - `counts_lock`, protecting counter updates.

## Integration Notes
`error.c` initializes, updates, flushes, and frees this state. The message list backs repeated-error memoization and ratelimiting, while `counts` mirrors persistent superblock error counts.

## Risks and Edge Cases
- If message-state allocation fails, fsck error ratelimiting/memoization may degrade but the filesystem continues reporting.
- The list and count locks protect different parts of the error state and should not be conflated.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/error_types.h -->