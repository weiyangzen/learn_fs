# Group Research: group_212_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_fs_logged_ops_c_sour_8aeca7221d48

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.c

This file implements recovery and lifecycle handling for the `BTREE_ID_logged_ops` btree, which stores resumable filesystem operations that must survive crashes.

Key elements:
- `logged_op_fns[]` maps logged operation key types to their resume functions via `BCH_LOGGED_OPS()`.
- `bch2_resume_logged_ops()` scans `BTREE_ID_logged_ops` for `LOGGED_OPS_INUM_logged_ops` and calls `resume_logged_op()` for each entry.
- `resume_logged_op()` reassembles the bkey into a mutable `bkey_buf`, checks for the inconsistency “clean filesystem has logged op”, dispatches the resume callback if recognized, then deletes the logged operation with `bch2_logged_op_finish()`.
- `__bch2_logged_op_start()` allocates an empty slot in the logged-ops btree, assigns the operation position, and updates the btree transaction.
- `bch2_logged_op_start()` wraps start in `commit_do()` with `BCH_TRANS_COMMIT_no_enospc`.
- `bch2_logged_op_finish()` deletes the operation with `BCH_TRANS_COMMIT_no_check_rw | BCH_TRANS_COMMIT_no_enospc`, and treats deletion failure as fatal because a completed operation would remain logged.

Important behavior:
- The finish path is designed to succeed even during shutdown, avoiding spurious `EROFS` on cleanup.
- Recovery detects logged operations on filesystems marked clean via `fsck_err_on(... logged_op_but_clean ...)`.
- Unknown logged operation types are still deleted because `fn` may be `NULL` but `bch2_logged_op_finish()` still runs.

Dependencies:
- Uses btree transaction/update APIs, bkey buffers, EC/data operation resume hooks, and fatal/fsck error handling.
- The operation type list comes from `logged_ops.h`, while on-disk layouts come from `logged_ops_format.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.h

This header declares the logged-operation API and the canonical list of logged operation kinds.

Key elements:
- `BCH_LOGGED_OPS()` currently lists:
  - `truncate`
  - `finsert`
  - `stripe_update`
- `bch2_logged_op_update()` is an inline helper inserting/updating a logged op in `BTREE_ID_logged_ops` using cached iteration.
- Declares start, finish, and recovery entry points:
  - `bch2_resume_logged_ops()`
  - `__bch2_logged_op_start()`
  - `bch2_logged_op_start()`
  - `bch2_logged_op_finish()`

Role:
- Shared by operation producers and recovery dispatch.
- The macro list drives the `logged_op_fns[]` table in `logged_ops.c`, so adding a new logged-op type requires matching resume function naming and on-disk format support.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops_format.h

This header defines the on-disk value formats for logged operations.

Key elements:
- `enum logged_ops_inums` partitions logged-op btree inode namespaces:
  - `LOGGED_OPS_INUM_logged_ops`
  - `LOGGED_OPS_INUM_inode_cursors`
- `struct bch_logged_op_truncate` stores subvolume, inode number, and target size.
- `enum logged_op_finsert_state` tracks insert-range progress:
  - `start`
  - `shift_extents`
  - `finish`
- `struct bch_logged_op_finsert` stores operation state, subvolume, inode, destination/source offsets, and current position.
- `struct bch_logged_op_stripe_update` stores old/new stripe indices plus old block mapping metadata.

Role:
- These structures are persistent recovery records. Field sizes and endianness are fixed with `__le*` types, so compatibility depends on stable layout.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.c

This file implements core namespace mutation transactions and several namespace fsck/path helpers.

Main transaction operations:
- `bch2_create_trans()` creates regular inodes, tmpfiles, subvolumes, and snapshots. It initializes inode metadata, creates subvolume records when requested, applies ACLs, creates dirents, updates parent link counts/timestamps, propagates casefold state, and writes the new inode in the proper snapshot.
- `bch2_link_trans()` creates a hardlink within the same subvolume, increments nlink, checks inherited attribute compatibility, creates the new dirent, updates backpointer fields, and writes both directory and target inode.
- `bch2_unlink_trans()` validates the VFS-provided target against the dirent, checks empty directories, handles subvolume unlink/removal semantics, decrements nlink when appropriate, clears matching inode backpointers, deletes the hash entry, and updates both inodes.
- `bch2_rename_trans()` performs rename, exchange, and overwrite. It updates dirent hashes, inode backpointers, subvolume parents, inherited attributes, directory depths, nlink accounting, timestamps, and overwritten target nlink.

Subvolume and inheritance behavior:
- `parent_inum()` resolves the logical parent, using `bi_parent_subvol` when crossing subvolume roots.
- `is_subdir_for_nlink()` excludes subvolume roots from normal directory nlink increments.
- `bch2_reinherit_attrs()` copies inherited inode options from a new parent unless explicitly set; directory casefold changes can reject cross-directory moves with `-EXDEV`.

Path reconstruction:
- Reverse-print helpers build paths from inode backpointers.
- `bch2_inum_to_path_reversed()` walks inode `bi_dir`/`bi_dir_offset` backpointers, follows parent subvolume snapshots, detects loops, and emits disconnected markers unless `INUM_TO_PATH_FAIL_ON_ERR` is set.
- Public wrappers include `bch2_inum_to_path()`, `bch2_inum_to_path_in_subvol()`, and `bch2_inum_snapshot_to_path()`.

Fsck helpers:
- `bch2_check_dirent_inode_dirent()` verifies target inode backpointers, repairs missing/wrong backpointers, handles unlinked inodes with dirents, and flags multiple links to directories/subvolumes.
- `__bch2_check_dirent_target()` repairs dirent `d_type` and target encoding when inconsistent with the inode.
- Casefold propagation helpers maintain `BCH_INODE_has_case_insensitive` on casefolded directories and ancestors.

Important invariants:
- Directory entries, inode backpointers, nlink counts, timestamps, and subvolume parent metadata are updated together inside btree transactions.
- Cross-subvolume moves are rejected except for subvolume-root cases explicitly handled.
- Directory casefold state is propagated up the tree for overlayfs expectations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.h

This header exposes namespace transaction helpers and inline consistency checks.

Key elements:
- Creation flags:
  - `BCH_CREATE_TMPFILE`
  - `BCH_CREATE_SUBVOL`
  - `BCH_CREATE_SNAPSHOT`
  - `BCH_CREATE_SNAPSHOT_RO`
- Declares transaction entry points for create, link, unlink, rename, inherited attribute repair, path reconstruction, dirent-target checks, and casefold propagation.
- `dirent_points_to_inode_nowarn()` verifies that a dirent target matches an inode, handling both subvolume dirents and normal inode dirents.
- `inode_points_to_dirent()` checks inode backpointer fields against a dirent key position.
- `bch2_check_dirent_target()` fast-paths valid dirents and calls `__bch2_check_dirent_target()` only when backpointer or `d_type` mismatches are detected.

Role:
- Used by VFS operations, fsck, dirent checking, and error reporting code that needs inode-to-path translation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.c

This file implements bcachefs quota metadata validation, superblock quota defaults, in-memory accounting, and Linux quotactl operations when `CONFIG_BCACHEFS_QUOTA` is enabled.

Always-built metadata operations:
- `bch2_sb_quota_validate()` validates the superblock quota field size.
- `bch2_sb_quota_to_text()` prints per-type flags and per-counter timer/warn settings.
- `bch_sb_field_ops_quota` registers the superblock field handlers.
- `bch2_quota_validate()` ensures quota bkey type index is below `QTYP_NR`.
- `bch2_quota_to_text()` prints hard/soft limits for space and inode counters.

Quota accounting:
- Uses per-quota-type `genradix` tables protected by per-type mutexes.
- `bch2_quota_acct()` checks enabled user/group/project quota types, applies hard/soft limit logic, updates in-memory counters, and sends quota netlink warnings.
- `bch2_quota_transfer()` moves space and inode usage between qids, used when ownership/project changes.
- `bch2_quota_check_limit()` enforces hard limits unless privileged, starts soft-limit timers, detects grace expiry, and clears warning state when usage drops.

Quota initialization:
- `bch2_fs_quota_init()` initializes locks.
- `bch2_fs_quota_exit()` frees genradix tables.
- `bch2_sb_get_or_create_quota()` creates the quota superblock field and defaults timer limits to seven days.
- `bch2_fs_quota_read()` reads on-disk quota limits and scans all inode snapshots to populate current usage without limit checks.

Quotactl support:
- `bch2_quota_enable()` enables enforcement flags but requires accounting to have been enabled at mount.
- `bch2_quota_disable()` clears enforcement flags.
- `bch2_quota_remove()` deletes quota btree ranges only when the corresponding quota accounting is disabled.
- `bch2_quota_get_state()` reports enabled accounting and timer/warn limits.
- `bch2_quota_set_info()` updates timer/warn limits in the superblock.
- `bch2_get_quota()` and `bch2_get_next_quota()` read in-memory quota state.
- `bch2_set_quota()` updates the quota btree and then mirrors new limits into memory.
- `bch2_quotactl_operations` wires these into the VFS quota interface.

Important details:
- Space limits are stored internally in sectors and converted to/from byte units for VFS quota structures.
- Quota reads account only live inodes discoverable via snapshot tree/master-subvolume lookup.
- Error paths return bcachefs error classes for VFS-facing calls.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.h

This header defines quota API glue and conditional no-op fallbacks.

Key elements:
- Registers quota bkey operations with validation, text formatting, and `min_val_size = 32`.
- `bch_qid()` maps an unpacked inode to user/group/project quota ids; project id is stored with a `+1` bias in inode options, so quota id uses `project - 1` or zero.
- `enabled_qtypes()` builds a bitmask from mount options `usrquota`, `grpquota`, and `prjquota`.
- Under `CONFIG_BCACHEFS_QUOTA`, declares accounting, transfer, init/exit/read, and `bch2_quotactl_operations`.
- Without quota support, all accounting and initialization functions become no-ops.

Role:
- Keeps callers quota-aware without forcing conditional compilation throughout inode/write paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_format.h

This header defines persistent quota formats.

Key elements:
- Quota types:
  - user
  - group
  - project
- Quota counters:
  - space
  - inode count
- `struct bch_quota_counter` stores hard and soft limits.
- `struct bch_quota` is the on-disk bkey value containing counters for space and inodes.
- Superblock quota field structs store per-type flags plus timer and warning limits per counter.

Role:
- Separates durable quota limits and global quota policy from in-memory usage counters.
- Uses little-endian fields and packed/aligned layout for on-disk compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_types.h

This header defines in-memory quota types.

Key elements:
- `struct bch_qid` stores user/group/project ids in a fixed array.
- `enum quota_acct_mode` distinguishes preallocation, warning/enforced, and no-check accounting.
- `struct memquota_counter` tracks current usage, hard/soft limits, timer, warning count, and warning-issued bits.
- `struct bch_memquota` groups counters for one quota id.
- `bch_memquota_table` is a generic radix tree of memory quota records.
- `struct quota_limit` stores global timer/warn limits.
- `struct bch_memquota_type` contains per-counter limits, the radix table, and the mutex for one quota type.

Role:
- Provides the runtime accounting backing used by `quota.c`; persistent bkeys store limits, while this layer tracks current usage and warning state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/quota_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.c

This file implements fsck and repair support for bcachefs string-hash btrees, used by dirents and xattrs.

Hash info:
- `__bch2_hash_info_init()` derives hash type, snapshot, 31-bit offset mode, casefold encoding, and siphash key from an inode.
- Old siphash compatibility hashes the inode seed through SHA-256 before building the key.
- `bch2_hash_info_init()` rejects casefolded directories when Unicode/casefold support is unavailable.

Duplicate and bad-key repair:
- `bch2_dirent_has_target()` checks whether a dirent points to an existing subvolume or inode.
- `hash_pick_winner()` chooses which duplicate key survives; for dirents it prefers entries with valid targets and flags ambiguous valid-vs-valid duplicates.
- `bch2_fsck_rename_dirent()` creates a unique `.fsck_renamed-N` name when both duplicate dirents point to valid objects.
- `str_hash_dup_entries()` reports duplicate hash table keys, optionally renames, deletes the loser, and commits lazily.
- `bch2_str_hash_repair_key()` reinserts a key into its proper hash slot, inserts snapshot whiteouts when needed, updates backpointers, or handles duplicates.
- `str_hash_bad_hash()` checks inode hash metadata against the root snapshot and repairs keys at the wrong offset.

Snapshot hash invariants:
- `bch2_repair_inode_hash_info()` repairs an inode snapshot whose hash type/seed diverges from the oldest/root snapshot.
- `check_inode_hash_info_matches_root()` verifies all snapshot versions of the same inode use compatible hash metadata, because snapshot string lookups depend on consistent hash placement.

Dirent-specific checks:
- `str_hash_check_dirent()` verifies `d_casefold` matches directory hash info and rebuilds/repositions the dirent if needed.
- `__bch2_str_hash_check_key()` checks wrong offsets, duplicates, hash whiteout boundaries, and dirent casefold mismatches.

Role:
- This is primarily consistency-repair logic for hashed metadata btrees.
- It is generic through `bch_hash_desc` but currently has extra behavior for dirents.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.h

This header defines the generic string-hash engine used by dirents and xattrs.

Hash support:
- `bch2_str_hash_opt_to_type()` maps filesystem options to crc32c, crc64, new siphash, or old siphash based on feature bits.
- `struct bch_hash_info` stores snapshot, hash type, 31-bit offset mode, casefold encoding, and key material.
- `bch2_str_hash_init/update/end()` abstract crc32c, crc64, and siphash. crc64/siphash return shifted values to avoid signed offset issues, and `bch2_str_hash_end()` can mask to 31 bits for old directory-offset mode.

Generic hash descriptor:
- `struct bch_hash_desc` supplies btree id, key type, hash/cmp callbacks, and optional visibility predicate.
- `is_visible_key()` filters by key type and snapshot/subvolume visibility.

Lookup/create/delete helpers:
- `bch2_hash_lookup_in_snapshot()` scans from the computed hash offset until it finds a matching visible key or reaches a hole.
- `bch2_hash_lookup()` resolves the subvolume snapshot then calls the snapshot-specific lookup.
- `bch2_hash_hole()` finds an insertion hole for a key.
- `bch2_hash_needs_whiteout()` determines whether deletion must leave a hash whiteout to preserve collision-chain lookup semantics.
- `bch2_hash_set_or_get_in_snapshot()` implements insert/replace/create semantics while handling collisions and whiteout reuse.
- `bch2_hash_set_in_snapshot()` and `bch2_hash_set()` are wrappers for insertion.
- `bch2_hash_delete_at()` writes either `KEY_TYPE_hash_whiteout` or `KEY_TYPE_deleted`.
- `bch2_hash_delete()` looks up then deletes by search key.

Fsck integration:
- Declares inode hash-info repair and slow-path key checking.
- `str_hash_key_needs_check()` fast-filters keys with wrong offsets or dirent casefold mismatch.
- `bch2_str_hash_check_key()` calls the heavy checker only when needed.

Role:
- This header carries most of the generic string-hash algorithm inline for performance and reuse by dirents/xattrs.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.c

This file implements bcachefs extended attributes, using `str_hash` for xattr btree keys and Linux xattr handlers for the VFS interface.

Hash and bkey operations:
- `bch2_xattr_hash()` hashes xattr type plus name.
- `xattr_hash_key()`, `xattr_hash_bkey()`, `xattr_cmp_key()`, and `xattr_cmp_bkey()` adapt xattrs to `bch_hash_desc`.
- `bch2_xattr_hash_desc` targets `BTREE_ID_xattrs` and `KEY_TYPE_xattr`.
- `bch2_xattr_validate()` checks value size bounds, xattr type validity, and NUL characters in names.
- `bch2_xattr_to_text()` prints namespace prefix, name/value text, and ACL details for POSIX ACL xattrs.

Core xattr operations:
- `bch2_xattr_get_trans()` looks up an xattr by type/name and copies its value to the caller.
- `bch2_xattr_set()` checks subvolume read-only state, peeks/writes inode ctime to ensure snapshot inode presence, then inserts/replaces/deletes the xattr hash entry.
- Delete of a missing key maps to success unless `XATTR_REPLACE` was requested.

Listing:
- `bch2_xattr_emit()` emits normal xattr names through namespace handlers.
- `bch2_xattr_list_bcachefs()` lists synthetic `bcachefs.*` and `bcachefs_effective.*` inode option xattrs.
- `bch2_xattr_list()` scans the xattr btree in the inode subvolume and appends synthetic inode-option attributes.

VFS handlers:
- Provides user, trusted, and security handlers.
- Trusted listing requires `CAP_SYS_ADMIN`.
- POSIX ACL types map to nop ACL handlers for type recognition.

Bcachefs synthetic xattrs:
- `bcachefs.*` gets/sets explicitly defined inode options.
- `bcachefs_effective.*` exposes inherited/effective option values and ignores sets.
- Setting options parses option text, runs option hooks, handles casefold changes, validates 31-bit directory offset mode on empty dirs, updates project id accounting, and writes the inode.

Important behavior:
- Xattr updates always touch the inode ctime and write the inode before xattr btree mutation so snapshot metadata remains coherent.
- Xattr key size is bounded by `u8 k.u64s`; oversized values return `-ERANGE`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.h

This header declares xattr hash descriptors, bkey ops, search helpers, and VFS list/set entry points.

Key elements:
- Exposes `bch2_xattr_hash_desc`.
- Registers xattr bkey operations with validate/to-text handlers and `min_val_size = 8`.
- `xattr_val_u64s()` computes required value u64s from name and value lengths.
- `xattr_val()` returns the value pointer after the name bytes.
- `struct xattr_search_key` and `X_SEARCH()` package type/name lookup keys.
- Declares `bch2_xattr_set()` for use by migration/tools paths, `bch2_xattr_list()`, and the global handler table.

Role:
- Used by VFS xattr code, ACL code, metadata validation, and migration tooling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr_format.h

This header defines persistent xattr key/value layout and namespace ids.

Key elements:
- Namespace indexes:
  - user
  - POSIX ACL access
  - POSIX ACL default
  - trusted
  - security
- `struct bch_xattr` stores:
  - common `bch_val`
  - `x_type`
  - `x_name_len`
  - little-endian `x_val_len`
  - flexible `x_name_and_value[]` bytes

Important detail:
- Name and value are stored contiguously; helper macros in `xattr.h` compute the value pointer.
- The comment notes that `__counted_by(x_name_len)` previously caused a false out-of-bounds detection, so the flexible array is left without that annotation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.c

This file implements the bcachefs character device control interface and ioctl dispatch.

Device lookup and global ioctl:
- `bch2_device_lookup()` resolves devices either by member index (`BCH_BY_INDEX`) or userspace path, returning a referenced `bch_dev`.
- `bch2_global_ioctl()` currently handles offline fsck.
- `bch2_ioctl_query_uuid()` copies the filesystem user UUID to userspace.
- `bch2_copy_ioctl_err_msg()` copies structured error text into v2 ioctl error buffers.

Device management ioctls:
- Add, remove, online, offline, set-state, resize, and journal-resize handlers validate capability (`CAP_SYS_ADMIN`), flags, padding, and bounds before calling `dev.c` operations.
- v2 variants use `bch2_copy_ioctl_err_msg()` to return detailed error strings.
- Force flags are restricted to operations where degraded/data-loss override makes sense.

Data job ioctl:
- `bch2_ioctl_data()` starts a long-running data job through `thread_with_file`.
- `bch2_data_thread()` runs `bch2_data_job()` and records completion/device-offline status.
- The returned file supports `read()` through `bch2_data_job_read()`, which reports progress, sector counts, and totals for scrub or filesystem usage.
- A write reference `BCH_WRITE_REF_ioctl_data` prevents running data jobs after writes are disabled.

Usage/accounting ioctls:
- `bch2_ioctl_fs_usage()` reports capacity, used sectors, online reservations, persistent reservations, and replica usage entries.
- `bch2_ioctl_query_accounting()` returns accounting data selected by mask.
- `bch2_ioctl_dev_usage()` and v2 report per-device usage by data type.

Superblock and index ioctls:
- `bch2_ioctl_read_super()` copies either the filesystem superblock or a specific device superblock.
- `bch2_ioctl_disk_get_idx()` maps a block device dev_t to the bcachefs member index.

Dispatch and char-device lifecycle:
- `bch2_fs_ioctl()` dispatches filesystem ioctls, allowing a small query set before `BCH_FS_started` and requiring started state for mutating operations.
- `bch2_chardev_ioctl()` maps minors below `U8_MAX` to filesystem-specific devices; minor `U8_MAX` is the global control node.
- `bch2_fs_chardev_init()/exit()` allocate/remove per-filesystem minors and devices.
- `bch2_chardev_init()/exit()` register the global char device major, class, and control node.

Role:
- This is the kernel/userspace administrative control surface for mounted bcachefs filesystems.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.h

This header declares the chardev ioctl interface and provides no-op fallbacks when filesystem support is disabled.

Key elements:
- Declares:
  - `bch2_copy_ioctl_err_msg()`
  - `bch2_fs_ioctl()`
  - per-filesystem chardev init/exit
  - global chardev init/exit
- Under `NO_BCACHEFS_FS`, `bch2_fs_ioctl()` returns `-ENOTTY` and init/exit helpers are no-ops.

Role:
- Used by filesystem lifecycle code to register control devices and by VFS paths that route ioctl requests.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/chardev.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.c

This file implements bcachefs device membership, online/offline transitions, add/remove/resize operations, sysfs integration, splitbrain checks, and block-layer hot-remove handling. It also contains a long design comment documenting multi-device behavior.

Documentation block:
- Explains per-device metadata, member states, durability, caching, add/remove workflows, hot-remove behavior, data-type restrictions, degraded modes, resize, error tracking, and consistency/self-healing.

Device identity and validation:
- `bch2_devs_list_to_text()` prints device lists by name.
- `bch2_dev_may_add()` validates block size and bucket size compatibility.
- `bch2_dev_to_fs()` finds an open filesystem by block dev_t.
- `bch2_dev_in_fs()` validates UUID membership, removed slots, block size, and member sequence/write-time splitbrain conditions.

IO reference and state transitions:
- `bch2_dev_io_ref_stop()` stops read/write refs and clears online read mask for reads.
- `__bch2_dev_read_only()` removes allocator access, recalculates capacity, drains write refs, stops per-device journal use, schedules discards, and flushes EC operations.
- `__bch2_dev_read_write()` re-adds allocator access, restarts write refs, recalculates capacity, and schedules discards.
- `bch2_dev_state_allowed()` checks whether changing a RW device to non-RW leaves the filesystem writable under the given force flags.
- `__bch2_dev_set_state()` persists member state changes, triggers reconcile scans, and queues stripe scans when RW membership changes.
- `bch2_dev_set_state()` wraps state changes under `state_lock`.

Device allocation and attachment:
- `__bch2_dev_alloc()` allocates `bch_dev`, initializes kobject, refs, latency stats, buckets, discard state, journal early state, and IO counters.
- `bch2_dev_attach()` assigns index/name, links into `c->devs`, and creates sysfs objects.
- `bch2_dev_alloc()` allocates a member from the filesystem superblock.
- `__bch2_dev_attach_bdev()` attaches an opened superblock/block device to an offline member, checks capacity, initializes journal, records device/model/serial strings, installs holder backpointer, and starts read refs.
- `bch2_dev_attach_bdev()` handles attach under state lock, updates online mask, sysfs, and reconcile wakeup.

Device removal:
- `bch2_dev_remove()` transitions the member to evacuating, drops data via backpointers or legacy scans, verifies usage is empty, flushes btree/journal pins, offlines the device before removing alloc info, runs replicas GC/accounting checks, removes the `c->devs` pointer, waits for refs, frees the device, and marks the member UUID deleted/zeroed.
- It restores RW allocator state on some failure paths when possible.

Device add/online/offline:
- `bch2_dev_add()` reads a new device superblock, validates compatibility, allocates a new member slot, attaches the device, writes updated superblocks, initializes usage/freespace/journal for started filesystems, creates labels, sends UUID change uevent, and schedules reconcile.
- `bch2_dev_online()` reads an existing member superblock, validates membership/splitbrain, attaches it, marks device superblock, initializes freespace/journal if needed, updates `last_mount`, and schedules pending reconcile.
- `bch2_dev_may_offline()` verifies remaining online/RW devices can satisfy read/write requirements.
- `bch2_dev_offline()` checks permission and calls `__bch2_dev_offline()`.

Resize:
- `bch2_dev_resize()` supports grow-only resize, validates maximum bucket count and underlying block capacity, resizes bucket arrays, marks device superblock, persists new bucket count, initializes new freespace, recalculates capacity, and schedules reconcile for new space.
- `__bch2_dev_resize_alloc()` adjusts disk accounting and initializes freespace for new buckets.

Lookup and hot-remove:
- `bch2_dev_lookup()` finds a member by name or `/dev/`-stripped name.
- Block holder ops use `bdev_get_fs()` and `bdev_to_bch_dev()` to find the owning filesystem/device.
- `bch2_fs_bdev_mark_dead()` responds to block-layer death by attempting forced-degraded offline; if not safe, it syncs/shrinks/evicts and puts the whole filesystem emergency read-only.
- `bch2_fs_bdev_sync()` syncs the VFS superblock for a held block device.

Important invariants:
- Device state changes are serialized by `state_lock`.
- Superblock mutations use `sb_lock` and `PF_MEMALLOC_NOFS`.
- Device removal is conservative about journal flush ordering to avoid stale pointers and writes after IO refs are stopped.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.h

This header declares the device-management API.

Key elements:
- Device-list formatting and open-filesystem lookup.
- Membership validation with `bch2_dev_in_fs()`.
- IO ref, sysfs, allocation, attach, offline, free, and unlink helpers.
- State transition helpers:
  - `bch2_dev_state_allowed()`
  - `__bch2_dev_set_state()`
  - `bch2_dev_set_state()`
- Administrative operations:
  - remove
  - add
  - online
  - offline
  - resize
- Mount-time resize allocation helper.
- Name lookup and block holder ops export.

Role:
- Shared by chardev ioctls, error handling, filesystem lifecycle, and block-device holder callbacks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/dev_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/dev_types.h

This header defines lightweight device/init types.

Key elements:
- `struct bch_sb_handle_holder` stores a backpointer to `struct bch_fs` for block holder callbacks.
- `struct bch_sb_handle` owns a read/open superblock context: superblock pointer, backing file/block device, name, bio, holder, buffer size, open mode, layout/bio/fs-superblock flags, and sequence.
- `struct bch_devs_mask` is a bitmap over possible superblock members.
- `struct bch_devs_list` is a compact list of device indexes sized to max bkey pointers.

Role:
- These types connect superblock IO, device membership, and allocator/read-write device masks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/dev_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/error.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/error.c

This file implements bcachefs runtime inconsistency policy, fsck error handling, bkey validation errors, IO error accounting, and error-state lifecycle.

Runtime inconsistency handling:
- `__bch2_log_msg_start()` adds the bcachefs log prefix/indent.
- `__bch2_inconsistent_error()` sets `BCH_FS_error` and follows the configured `errors=` policy: continue, emergency read-only, or panic.
- `bch2_fs_inconsistent()` and `bch2_trans_inconsistent()` format and print filesystem or transaction inconsistency messages, including pending transaction updates.
- `__bch2_topology_error()` marks topology error state and either requests explicit topology repair during recovery or forces a topology-repair error.
- `bch2_fatal_error()` formats fatal errors and forces emergency read-only.

IO error handling:
- `bch2_io_error()` increments persistent per-device error counters, starts write-error timing, and schedules `io_error_work`.
- `bch2_io_error_work()` sets a device read-only after sustained write errors if safe; otherwise it puts the filesystem emergency read-only.

Fsck prompting and policy:
- `parse_yn_response()` accepts `y/n/Y/N`, where uppercase applies to all errors of that type.
- Kernel fsck prompting uses `stdio_redirect`, temporarily unlocking btree transactions and doing long unlock if user input waits.
- Userspace prompting uses `getline()`.
- `fsck_err_get()` tracks per-error state for deduplication, repeated answers, and rate limiting.
- `bch2_fsck_err_opt()` converts current fsck/mount options and error flags into fix/ignore/ask/exit outcomes.
- `__bch2_fsck_err()` is the central fsck decision engine: formats the message, detects custom action text, counts/rate-limits, asks or auto-decides, logs transaction strings for fixes, and sets global error/fixed flags.
- `__bch2_count_fsck_err()` increments counts and decides whether to print.

Bkey validation errors:
- `__bch2_bkey_fsck_err()` formats invalid bkey context, journal position if relevant, btree/level, key text, and reason; outside write/commit validation it marks the error autofix/delete.

Error formatting helpers:
- `bch2_inum_offset_err_msg_trans_norestart()` and `bch2_inum_offset_err_msg_trans()` format an inode/path plus byte offset, using namei path reconstruction when possible.

Lifecycle:
- `bch2_fs_errors_init_early()` initializes lists, locks, and count arrays.
- `bch2_fs_errors_init()` loads superblock error counts to CPU state.
- `bch2_flush_fsck_errs()` and `bch2_free_fsck_errs()` release per-error message state.
- `bch2_fs_errors_exit()` frees count arrays.

Important behavior:
- Repeated identical fsck messages reuse previous decisions to avoid repeated prompts across transaction restarts.
- Silent errors can still mark “errors fixed silently”.
- Runtime self-healing is allowed only when error flags and mount policy permit it.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/error.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/error.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/error.h

This header declares error handling APIs and many fsck/error macros.

Key elements:
- Declares inconsistency, topology, fatal, IO-error, latency/accounting, inode-offset formatting, and error lifecycle functions.
- Defines `struct fsck_err_state`, which records per-error id, count, cached return decision, fix policy, rate-limit state, and last message.
- `bch2_fs_inconsistent_on()` and `bch2_trans_inconsistent_on()` wrap conditional inconsistency reporting.
- Fsck macro families:
  - `mustfix_fsck_err*`
  - `fsck_err*`
  - `log_fsck_err*`
  - `ret_fsck_err*`
  - `ret_log_fsck_err*`
- `bkey_fsck_err*` macros convert invalid bkeys into delete-key fsck outcomes.
- `bch2_fs_fatal_error()` and `bch2_fs_fatal_err_on()` add function-name context to fatal errors.
- `bch2_account_io_success_fail()` clears write-error timers on success or records IO errors on failure.
- `bch2_account_io_completion()` adds latency accounting and success/failure accounting.

Role:
- Provides the common error/reporting vocabulary used across metadata validation, fsck, btree code, device code, and IO paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/error.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/error_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/error_types.h

This header defines `struct bch_fs_errors`, the filesystem-wide error tracking container.

Fields:
- `msgs`: list of active fsck error message states.
- `msgs_lock`: protects the message list.
- `msgs_alloc_err`: records allocation failure while tracking fsck messages.
- `counts`: CPU-side superblock error counters.
- `counts_lock`: protects counter state.

Role:
- Embedded in `struct bch_fs` and initialized by `error.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/error_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.c

This file implements module initialization, filesystem object allocation/free, superblock/device open, mount startup/recovery, read-write/read-only transitions, sysfs registration, and global print/log helpers.

Logging and globals:
- Defines module metadata.
- Exposes string tables for filesystem flags and write refs.
- `bch2_print_str_loglevel()`, `bch2_print_str()`, `bch2_print_opts()`, and `__bch2_print()` implement loglevel filtering and optional stdio redirection.
- Defines sysfs kobject types via `KTYPE()`.
- Maintains global `bch2_fs_list` and `bch2_fs_list_lock`.
- `bch2_uuid_to_fs()` and `__bch2_uuid_to_fs()` find open filesystems by UUID.

Read-only transition:
- `__bch2_fs_read_only()` stops background writers, drains open buckets/copygc/write buffer/EC, repeatedly flushes discards, write buffers, key cache, interior updates, journal pins, and btree writes until stable, handles journal-error dirty-node cancellation, marks clean shutdown when safe, stops journal, and stops per-device write refs/allocators.
- `bch2_fs_read_only()` sets `BCH_FS_going_ro`, stops reconcile before disabling write refs, waits for outstanding writes unless emergency read-only interrupts the wait, calls the low-level transition, clears RW flags, verifies clean invariants when possible, or persists error counters when unclean.
- `bch2_fs_emergency_read_only()` and locked variant halt the journal, queue async read-only work, wake allocators/waiters, and annotate the error message once.

Read-write transition:
- `__bch2_fs_read_write()` rejects RW when required feature/allocation/version/error conditions are not satisfied, initializes RW subsystems, starts device allocators/write refs, marks the journal running, starts global write refs, starts journal reclaim/write-buffer/copygc/reconcile, and kicks pending discard/invalidate/stripe/scrub/bitmap-GC work.
- `bch2_fs_read_write()` enforces no-recovery/nochanges/no-alloc-info restrictions.
- `bch2_fs_read_write_early()` performs the same under `state_lock`.

Filesystem shutdown/free:
- `__bch2_fs_free()` tears down all subsystems in reverse-style order, destroys workqueues, frees the superblock, and drops the module reference.
- `bch2_fs_stop()` serializes shutdown, goes read-only, stops read refs, unlinks devices/sysfs/chardev/debugfs, waits for read-only refs, flushes reads and work, and returns error codes if shutdown followed emergency RO or unresolved/fixed errors.
- `bch2_fs_free()` removes the fs from the global list, waits for closure completion, frees devices, and releases the fs kobject.
- `bch2_fs_exit()` combines stop and free.

Online/sysfs and RW init:
- `bch2_fs_online()` checks duplicate UUIDs, creates chardev/debug/sysfs objects, creates device sysfs nodes, and adds the fs to the global list.
- `bch2_fs_init_rw()` allocates workqueues and initializes RW btree, write IO, journal, VFS, journal reclaim, write buffer, copygc, and reconcile.

Version/mount option handling:
- `check_version_upgrade()` determines compatible or incompatible metadata upgrade target, records required recovery passes, and updates superblock upgrade state.
- `bch2_fs_opt_version_init()` handles `norecovery`, `nochanges`, `journal_rewind`, upgrade/downgrade eligibility, mount log output, recovery-pass requirements, lost-btree metadata, error-action compatibility, extent backpointer shift repair requirements, clean/fsck/recovery flags, Unicode/casefold messages, unsupported old features, and member field upgrades.

Filesystem object initialization:
- `bch2_fs_init()` initializes kobjects, locks, refs, time stats, early subsystem state, superblock fields, compatibility defaults, options, block size, names, write refs, blacklist table, btree/compress/counters/data/discard/EC/errors/encryption/read/VFS/IO clocks, Unicode casefold encoding, member devices, journal reservations, attaches opened block devices, performs version option init, and brings the fs online.
- `bch2_fs_alloc()` allocates `struct bch_fs`, runs init, and cleans up on failure.

Start/recovery:
- `bch2_missing_devs_to_text()` prints missing data-bearing devices.
- `bch2_fs_may_start()` enforces degraded/missing device policy and read/write capability.
- `__bch2_fs_start()` adds RW devices to allocator, checks start eligibility, initializes reconcile/counters, requests feature upgrades, optionally initializes RW early, runs option hooks, performs recovery or fresh initialization, marks started, then either remains read-only or goes read-write.
- `bch2_fs_start()` wraps start with formatted logging and clears `recovery_task`.

Resize-on-mount:
- `bch2_dev_will_resize_on_mount()` detects member resize requests when the block device is larger.
- `bch2_fs_will_resize_on_mount()` checks all online devices.
- `bch2_fs_resize_on_mount()` grows bucket arrays, updates member `nbuckets`, clears small-image/resize flags, writes superblock, and initializes new freespace if needed.

Open path:
- `__bch2_fs_open()` reads all supplied device superblocks, chooses the best by sequence/write_time, filters removed/splitbrain devices, allocates the filesystem from the best superblock, logs version messages, and starts unless `nostart`.
- `bch2_fs_open()` wraps open with user-facing error printing.

Module lifecycle:
- `bcachefs_init()` runs bkey pack tests, creates the global sysfs kobject, and initializes lock graph, key cache, chardev, VFS, and debug subsystems.
- `bcachefs_exit()` tears down global subsystems.
- Static-key module parameters are generated for debug parameters.
- Exposes a read-only metadata version module parameter.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.h

This header declares filesystem lifecycle, global fs lookup, read-only/read-write, resize, and open APIs.

Key elements:
- `KTYPE(type)` macro builds kobject type boilerplate from per-type attributes, release function, and sysfs ops.
- Exports string tables for filesystem flags, filesystem write refs, and device read/write refs.
- Exports global `bch2_fs_list` and `bch2_fs_list_lock`.
- Declares UUID lookup:
  - `__bch2_uuid_to_fs()`
  - `bch2_uuid_to_fs()`
- Declares emergency/read-only/read-write APIs.
- Declares RW init and mount-time resize.
- Declares missing-device formatting and start/stop/exit/open functions.

Role:
- Shared by init, chardev, error, logged-ops, recovery, and VFS-facing code that needs filesystem lifecycle control.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/init/fs.h -->