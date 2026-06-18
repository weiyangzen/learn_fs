# Group Research: group_214_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_journal_validate_c_s_d3547af388a7

Scope: `Docs/research_subset_a.md`, focused on bcachefs journal validation/write paths, option schema/parsing, superblock clean/counter/error/downgrade/io handling, and member metadata management.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.c

This file validates and renders journal sets and individual journal entries. It is the journal-side metadata integrity gate used both when reading/replaying journal entries and before writing journal data.

Key responsibilities:
- Builds contextual journal error messages with version, entry type, sequence, and offset.
- Validates journal bkeys for nonzero size, bounds, key format, compatibility conversion, and type-specific bkey validity.
- Repairs some corrupt entries under fsck policy by shrinking/removing invalid keys and zeroing trailing entry space.
- Validates all supported `BCH_JSET_ENTRY_*` payload types through a dispatch table.
- Renders journal entry contents for diagnostics.
- Validates whole `jset` headers: magic, compatible metadata version, checksum type, `last_seq <= seq`, and entry bounds.
- Provides early validation before full read when only bucket-bound size checks are possible.

Important invariants:
- Entry iteration must never advance past the enclosing `jset`/clean-section vstruct end.
- On write validation failures, errors are counted and may force filesystem inconsistency handling rather than silent writeout.
- `btree_root` entries intentionally keep the entry wrapper even if contents are nulled so later recovery can tell a root was expected.
- Unknown journal entry types are tolerated by returning success if the type is outside the known dispatch table.

Dependencies include bkey validation/compatibility, fsck error handling, replicas validation, journal format helpers, superblock magic/checksum helpers, and printbuf diagnostics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.h

This header exposes journal validation and text-rendering APIs.

Key elements:
- Declares `bch2_journal_entry_err_msg()`, entry validation/text helpers, full `jset` validation, and early `jset` validation.
- Defines `journal_entry_err()` and `journal_entry_err_on()` macros that integrate journal validation with fsck repair policy.
- Defines `JOURNAL_ENTRY_NONE` and `JOURNAL_ENTRY_BAD` sentinel return values used by journal scanning.

Important behavior:
- Read-time validation calls `mustfix_fsck_err()`.
- Write-time validation increments persistent fsck error counts and can make the filesystem inconsistent/read-only if corrupt metadata would be written.
- The macros rely on local variables such as `from` and `ret`, so callers must follow the expected validation-function structure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.c

This file implements allocation, preparation, checksum/encryption, submission, and completion of journal writes.

Key responsibilities:
- Allocates journal entry replicas on suitable devices, honoring metadata targets and desired replica durability.
- Advances journal devices to fresh buckets when current buckets lack enough free sectors.
- Resizes journal buffers and coordinates write-buffer sizing.
- Compacts journal entries, drops empty reservations, converts `write_buffer_keys`, adds missing B-tree roots, timestamps, common superblock-derived entries, and rewind-limit entries.
- Chooses flush versus noflush journal writes based on errors, explicit flush needs, journal delay, and skip-flush policy.
- Validates journal entries before or after encryption depending on checksum/encryption/version requirements.
- Submits journal bios with flush/FUA semantics and optional separate preflushes for multi-device filesystems.
- Completes writes in sequence order, updates `last_seq_ondisk`, `flushed_seq_ondisk`, `seq_ondisk`, reclaim state, and waiters.
- Handles degraded journal writes and fatal write failure by emergency read-only transition.

Important invariants:
- `journal_buf.write_done` means all post-completion bookkeeping is finished, not just that IO completed.
- Completion must not advance `flushed_seq_ondisk` past a sequence until replica refs for prior sequences are released.
- `j->in_flight.front` is kept equal to `seq_ondisk + 1` for `journal_seq_to_buf()` indexing.
- Clean filesystems defer marking journal replicas until after write completion so a clean superblock is not dirtied before journal data exists.
- `nochganges`/`nochanges` mode skips actual IO but still runs completion bookkeeping.

Dependencies include allocator device targeting, replicas accounting, B-tree root journaling, write-buffer flushing, checksum/encryption, journal reclaim, discard scheduling, superblock clean entries, and block-layer bio submission.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.h

This header declares the journal write closure callback and a helper for appending journal-set entries.

Key elements:
- `CLOSURE_CALLBACK(bch2_journal_write)` is the async journal write entry point.
- `jset_entry_init()` zeroes a new fixed-size entry, stores its `u64s` payload length, advances the caller’s end pointer, and returns the initialized entry.

Important invariant:
- `entry->u64s` counts from the start of the entry data area and excludes the shared header fields, so callers pass total structure size and the helper stores `DIV_ROUND_UP(size, 8) - 1`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/journal/write.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/opts.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/opts.c

This file implements bcachefs option tables, parsing, formatting, superblock/member serialization, runtime hooks, and inode-option extraction.

Key responsibilities:
- Materializes string tables for errors, degraded policy, fsck fixes, upgrade policy, features, btree IDs, checksum/compression/hash/data/member/reconcile/journal options, and d_types.
- Builds `bch2_opt_table[]` from the macro schema in `opts.h`, including sysfs attributes, type, flags, bounds, help text, and superblock/member/ext accessors.
- Parses booleans, unsigned integers, string choices, bitfields, and custom option functions.
- Validates bounds, sector alignment, power-of-two requirements, and custom validators.
- Formats single options, changed option sets, and inode IO options.
- Applies defined values from one `bch_opts` to another and gets/sets options by enum ID.
- Parses mount option lists, including `no<opt>` boolean negation and synonyms such as `quota=usrquota` and degraded bool aliases.
- Converts options to/from superblock, member, and extension fields with sector, ilog2, and one-bias transforms.
- Runs pre/post option hooks for feature enablement, compression availability, casefold constraints, device state changes, reconciliation scans, copygc/reconcile wakeups, discard persistence, durability updates, and incompatible version upgrade.
- Maintains an option-change cookie under a mutex for readers that need to detect changed IO policy.

Important invariants:
- Undefined options are represented by separate `<name>_defined` bits; default fallback is handled by `opt_get()`.
- `OPT_MOUNT_OLD` options are parsed but rejected for modern mount-time setting with a warning.
- Runtime IO-affecting option changes are bracketed by reconciliation scan setup before and after the change.
- Superblock updates are protected by `sb_lock` and persisted with `bch2_write_super()` only when the encoded value changes.
- Metadata inode options override user-data policy: metadata uses metadata target/replicas/checksum and disables compression/EC.

Dependencies include fs parser constants, disk-group target parsing, compression helpers, reconciliation work scheduling, copygc wakeups, device state changes, feature/version upgrade helpers, and superblock IO.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/opts.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/opts.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/opts.h

This header is the central option schema for bcachefs.

Key responsibilities:
- Declares option string tables and print helpers for enums used across diagnostics.
- Defines option flags for filesystem/device/inode scope, format/mount/runtime availability, human-readable parsing, superblock field transforms, hidden/legacy/doc behavior, and validation constraints.
- Defines option types: bool, uint, string, bitfield, and custom function.
- Defines the `BCH_OPTS()` macro list that creates every option’s enum ID, in-memory field, default, persistence accessor, flags, parser type, hint, and help text.
- Defines `struct bch_opts`, `struct bch_option`, masks, parse staging, and option get/set helpers.
- Declares parsing, formatting, pre/post hook, superblock serialization, and inode-option APIs.
- Defines `struct bch_inode_opts` and `bch2_io_opts_fixups()`.

Major option categories:
- Format and metadata geometry: block size, B-tree node size, extent size.
- Error/fsck/recovery policy: errors, fsck, fix_errors, recovery passes, journal rewind/scrub.
- Data placement and redundancy: metadata/data replicas, foreground/background/promote targets, durability, data_allowed.
- Integrity and encoding: metadata/data checksum, compression, background compression, string hash, EC, nocow.
- Runtime services: journal delays, copygc, reconcile, auto snapshot deletion, writeback, discard.
- Mount-only/debug behavior: degraded, noexcl, read_only, nochanges, norecovery, no_data_io.
- Device attributes: state, bucket size, rotational, readahead, discard.

Important invariants:
- `struct bch_opts` stores each option as a value plus a defined bit so partial option sets can be merged.
- `bch2_io_opts_fixups()` normalizes inherited policy: background target/compression default to foreground/compression, single replica disables EC, nocow disables checksum/compression/EC, and EC caps replicas to RAID6-style limits.
- Superblock field flags describe how values are encoded on disk; callers must use the conversion helpers instead of writing fields directly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/opts.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.c

This file implements the `BCH_SB_FIELD_clean` superblock section used after clean shutdown.

Key responsibilities:
- Validates clean-section journal-entry-shaped records, including late validation through journal entry validators.
- Reads and duplicates the clean section from the superblock when a filesystem is marked clean.
- Verifies that clean-section journal sequence and B-tree roots match the actual journal after clean shutdown.
- Adds common superblock/journal entries for key version and IO clocks.
- Renders clean-section flags, journal sequence, and contained journal entries.
- Marks filesystems dirty by clearing the clean bit and ensuring always-on features.
- Marks filesystems clean by resizing/populating the clean section with common entries and current B-tree roots, validating it, and recording journal member positions.

Important invariants:
- The clean section stores entries in the same format as journal entries.
- If the superblock says clean but no clean section exists, the clean bit is cleared and an invalid-clean error is returned.
- Clean-section entry bounds are validated both structurally and with the same bkey/journal validation machinery used by the journal.
- Clean shutdown captures all B-tree roots so the next mount can skip journal replay.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.h

This header exposes clean-superblock section APIs.

Public functions:
- Late validation of clean-section contents.
- Verification of clean-section roots against journal roots.
- Reading the clean section from an open filesystem.
- Adding common journal/superblock entries.
- Marking filesystem state dirty or clean.

It also exports `bch_sb_field_ops_clean` for the generic superblock field dispatcher.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.c

This file implements persistent filesystem counters stored in the superblock and mirrored in per-cpu runtime storage.

Key responsibilities:
- Builds maps from runtime counter enum IDs to stable on-disk IDs.
- Exports counter names, flags, and stable ID maps.
- Renders persisted counter values from the superblock.
- Loads superblock counter values into per-cpu counters and mount snapshots.
- Writes current per-cpu counters back into the superblock counter field, resizing as needed.
- Maintains a delayed-work ring of recent counter snapshots for delta display.
- Initializes and tears down counter storage.
- Resets individual counters.
- Implements the counter query ioctl when chardev support is enabled.

Important invariants:
- Stable on-disk counter IDs are not the same as enum order; mapping tables must be used.
- Counter types distinguish event counts from sector amounts and are enforced by macros in `counters.h`.
- `mount[]` stores the values observed at mount/load time for mount-relative queries.
- Recent counters sample every half second and display only counters that changed across the window.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.h

This header declares persistent counter APIs and event accounting macros.

Key elements:
- Superblock-to-CPU and CPU-to-superblock synchronization declarations.
- Counter init/exit/reset and recent-counter text rendering declarations.
- Counter ioctl declaration.
- Exports counter names, flags, stable map, and superblock field ops.
- Defines `event_inc`, `event_add`, `event_trace`, `event_add_trace`, and `event_inc_trace`.

Important invariant:
- `event_inc()` is only valid for `TYPE_COUNTER` counters and `event_add()` is only valid for `TYPE_SECTORS`; compile-time checks enforce the expected type.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_format.h

This header defines the persistent counter catalog and on-disk counter field format.

Key responsibilities:
- Defines counter flag types: event counters and sector amount counters.
- Lists all persistent counters with stable numeric IDs, type flags, and help text.
- Generates runtime enum `bch_persistent_counters`.
- Generates stable on-disk enum `bch_persistent_counters_stable`.
- Defines `struct bch_sb_field_counters` as a variable-length superblock field of little-endian counter values.
- Provides a compile-time uniqueness check pattern for stable counter IDs.

Counter categories include:
- Sync/fsync and data read/write/update/promotion behavior.
- Reconcile, copygc, stripe, bucket allocation/discard, and cached pointer operations.
- B-tree cache/node operations.
- Journal reservation/write/reclaim events.
- Transaction restarts and commits.
- Write buffer flushing and accounting paths.
- Error throws.

Important invariant:
- Stable IDs are explicit and sparse so new counters can be added without changing existing on-disk positions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_types.h

This header defines runtime counter storage.

Key type:
- `struct bch_fs_counters` stores mount-time snapshots, per-cpu current counter values, a 20-sample recent-history matrix, and delayed work for periodic sampling.

The structure is embedded in `struct bch_fs` and coordinated by `counters.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.c

This file manages superblock policy for metadata version upgrades and downgrades.

Key responsibilities:
- Defines upgrade and downgrade tables mapping metadata version crossings to required recovery passes and fsck errors that should be fixed silently.
- Handles all-fsck recovery pass expansion for broad upgrade requirements.
- Adds extra upgrade requirements for version-specific conditions such as existing stripes.
- Writes required recovery passes and silent-error bitmaps into the superblock extension field on upgrade.
- Builds the downgrade superblock field containing per-version recovery/error requirements for older tools/kernels.
- Validates and renders the downgrade field.
- Applies downgrade entries when lowering allowed/current minor versions by merging required passes and silent errors into in-memory and on-disk extension state.

Important invariants:
- Downgrade entries are packed and only 2-byte aligned; iteration carefully checks bounds before accessing flexible-array errors.
- Downgrade entries must match the major version of the current superblock.
- Entries below `version_incompat` are omitted because older compatible downgrade paths cannot safely apply past incompatible format use.
- The downgrade field is only updated once the B-tree subsystem is running, because some conditions depend on live filesystem state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.h

This header declares the downgrade/upgrade policy interface.

Public functions:
- Update the downgrade superblock field.
- Record compatible and incompatible upgrade requirements.
- Apply extra upgrade requirements.
- Apply downgrade requirements for a minor-version transition.

It exports `bch_sb_field_ops_downgrade` for generic superblock field validation/rendering.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade_format.h

This header defines the on-disk format of the downgrade superblock section.

Key types:
- `struct bch_sb_field_downgrade_entry`: packed entry containing target metadata version, two words of stable recovery-pass bits, error count, and flexible array of fsck error IDs.
- `struct bch_sb_field_downgrade`: superblock field wrapper containing a variable-length list of entries.

Important invariant:
- Entries are `__packed __aligned(2)`, so code must not assume natural 64-bit alignment for `recovery_passes`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.c

This file implements persistent filesystem/fsck error counting in the superblock.

Key responsibilities:
- Generates error-name strings from the stable error catalog.
- Renders error IDs and unknown error fallback text.
- Validates the superblock errors field for nonzero counts and strictly increasing error IDs.
- Renders persisted errors sorted by most recent error time.
- Renders in-memory error counts.
- Increments an in-memory error count with last-error timestamp, preserving sorted-by-ID order.
- Serializes in-memory error counts back to the superblock.
- Loads superblock error counts into memory.

Important invariants:
- Persistent entries are sorted by error ID for validation/storage.
- Human-readable output sorts by `last_error_time` descending.
- Counts are stored as 48-bit values packed with 16-bit error IDs in the on-disk entry word.
- Allocation failure while counting a new error silently drops that new count rather than destabilizing error handling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.h

This header exposes persistent error-counting APIs.

Key elements:
- Exports error string table and ID-to-text renderer.
- Declares filesystem error text rendering.
- Exports `bch_sb_field_ops_errors`.
- Declares increment, serialize, and load functions for superblock error counts.
- Includes `errors_types.h` for the in-memory darray type.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_format.h

This header defines fsck error flags, the stable fsck/superblock error catalog, and the on-disk errors field.

Key responsibilities:
- Defines fsck error behavior flags: can fix, can ignore, autofix, no log, and silent.
- Lists all stable `BCH_FSCK_ERR_*` IDs with numeric IDs and flags.
- Generates `enum bch_sb_error_id`.
- Defines packed on-disk error entries and the variable-length errors superblock field.
- Defines bitfield accessors for 16-bit error ID and 48-bit count.

Error categories include:
- Clean/dirty journal state and journal entry validation.
- B-tree node, bset, topology, and root errors.
- Filesystem/device usage accounting.
- Allocation, freespace, bucket generation, discard, and backpointer errors.
- Extent pointer, checksum/compression, stripe, reflink, and reservation errors.
- Snapshot/subvolume/inode/dirent/xattr/quota namespace errors.
- Accounting/reconcile/workqueue and VFS consistency errors.
- Device flush and journal bucket sequence errors.

Important invariant:
- Numeric IDs are stable and sparse; the final `MAX` entry establishes `BCH_FSCK_ERR_MAX`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_types.h

This header defines in-memory persistent-error count types.

Key types:
- `struct bch_sb_error_entry_cpu`: 16-bit error ID, 48-bit count, and last-error timestamp.
- `bch_sb_errors_cpu`: dynamic array of CPU-format error entries.

This type is protected by `c->errors.counts_lock` in `errors.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.c

This file implements bcachefs superblock layout documentation, validation, read fallback, write replication, version management, field dispatch, and text rendering.

Key responsibilities:
- Documents superblock layout, redundancy, threat model, fixed fields, variable fields, versioning, and recovery behavior.
- Converts metadata versions to text and computes latest compatible versions within a major version.
- Enforces incompatible feature/version enablement through `bch2_set_version_incompat()`.
- Gets, resizes, deletes, and reallocates variable-length superblock fields.
- Validates superblock layout sector, version compatibility, UUIDs, offset, member count/index, time precision, feature bits, field bounds, member sections, and all typed superblock fields.
- Copies shared superblock state between filesystem-wide and per-device handles.
- Updates in-memory `c->sb` CPU fields from the on-disk superblock, including ext recovery passes, silent errors, and lost-data btree bitmap.
- Reads the primary superblock, embedded/standalone layout, and all backup copies, selecting the highest valid sequence number.
- Falls back to buffered IO in userspace if direct IO is incompatible with device block size.
- Writes superblocks to all online member devices and all configured superblock slots.
- Reads back primary superblocks before write to detect silent dropped writes or external modification.
- Marks clean/dirty as needed, serializes counters/members/errors/downgrade/extent-type state, validates before write, and refuses unsafe writes.
- Determines whether enough devices were successfully written to keep the filesystem mountable.
- Handles feature setting, compatible/incompatible upgrade, version downgrade, and async recovery pass scheduling.
- Provides generic superblock field validation/text dispatch and full superblock text rendering.

Important invariants:
- The highest valid sequence-number superblock copy is authoritative.
- Backup copy selection scans every configured backup, not only on primary failure.
- Superblock field resizing must also ensure online member devices have enough buffer space.
- Members are validated before other fields because other fields may depend on member metadata.
- Writes are skipped before initialization and in `nochanges` mode.
- A superblock write is fatal if no device was written or the set of written devices is insufficient to mount with current degraded policy.
- `bch2_write_super()` updates in-memory visible options only after persistence succeeds or the write path exits.

Dependencies include checksum helpers, journal superblock state, journal sequence blacklist, quota, device open/write refs, replicas, disk groups, member metadata, counters, errors, downgrade policy, clean section handling, recovery pass mapping, and block-layer bio IO.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.h

This header exposes superblock IO, field, version, magic, and rendering APIs.

Key elements:
- Defines the superblock readback scratch buffer size.
- Provides version compatibility and incompatible-feature request helpers.
- Defines typed superblock field get/resize/minsize/delete helpers.
- Defines `struct bch_sb_field_ops` for field validation/rendering dispatch.
- Provides filesystem-specific journal and bset magic derivation from UUID.
- Declares superblock copy, allocation, validation, read, silent read, write, feature, upgrade/downgrade, and text-rendering functions.

Important invariant:
- `bch2_request_incompat_feature()` is a fast-path check against `c->sb.version_incompat`; only unsupported requests call the slower superblock-updating path.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/io_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/io_types.h

This header defines the CPU-format superblock summary stored in `struct bch_fs`.

Key fields:
- Internal and user UUIDs.
- Current, minimum, incompatible, allowed incompatible, and upgrade-complete versions.
- Device count, clean flag, multi-device flag, and encryption type.
- Extent type sizing/known metadata and backpointer shift.
- Time base/precision conversion fields.
- Feature and compat bitmaps.
- Required recovery passes, silent fsck errors, and btrees with lost data.

This structure is refreshed by `bch2_sb_update()` after reading or writing the on-disk superblock.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/io_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.c

This file implements superblock member-device metadata handling, validation, text output, error tracking, B-tree allocation bitmaps, member slot allocation, and member-field upgrades.

Key responsibilities:
- Reports pointers to missing/removed devices and schedules allocation-check recovery passes.
- Exports member IO error strings and IOPS measurement names.
- Reads members from v1 or v2 sections and returns mutable v2 member pointers.
- Initializes v2 members from v1 and grows `member_bytes` to the current `struct bch_member` size.
- Mirrors v2 members back to v1 while old metadata compatibility requires it.
- Validates member geometry: bucket count, bucket range, bucket size versus block/B-tree node size, B-tree bitmap shift, and freespace/feature consistency.
- Renders detailed and short member/device descriptions.
- Validates/renders both `members_v1` and `members_v2` superblock fields.
- Serializes runtime per-device error counters into the superblock and loads member info back into `bch_dev`.
- Renders and resets device IO error counters, including reset baseline and flush errors.
- Maintains per-member “range has B-tree nodes” bitmaps to speed recovery scans.
- Runs B-tree bitmap GC by scanning B-tree roots/interior levels and rewriting compacted member bitmaps.
- Schedules daily/rate-limited bitmap GC when marked B-tree bitmap coverage is much larger than current B-tree allocation.
- Counts existing member devices, allocates new member slots, cleans deleted member UUID markers, and upgrades missing member fields such as rotational state.

Important invariants:
- `members_v2` is canonical for modern metadata; `members_v1` is kept only for compatibility when required.
- `member_bytes` allows forward-compatible larger member records but must be nonzero and large enough for current access during validation/resizing.
- Deleted devices use `BCH_SB_MEMBER_DELETED_UUID`; zero UUID slots may be reused, preferring the least-recently-mounted slot when full.
- B-tree bitmap marking may resize bitmap granularity by folding existing bits; the shift must stay below `BCH_MI_BTREE_BITMAP_SHIFT_MAX`.
- Bitmap GC writes updated member bitmap state under `sb_lock` and persists it with `bch2_write_super()`.

Dependencies include allocation/bucket helpers, disk groups, replicas, B-tree iterators/cache, progress reporting, recovery pass scheduling, superblock IO, init/error handling, and per-device runtime state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.c -->