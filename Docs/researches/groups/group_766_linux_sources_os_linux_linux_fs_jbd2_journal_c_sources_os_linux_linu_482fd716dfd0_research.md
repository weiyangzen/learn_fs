# Group Research: group_766_linux_sources_os_linux_linux_fs_jbd2_journal_c_sources_os_linux_linu_482fd716dfd0

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/linux/linux`, and every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/journal.c -->
# File Research: sources/os/linux/linux/fs/jbd2/journal.c

## Role

`journal.c` is the central JBD2 journal lifecycle and log-management implementation. It manages journal objects, the `kjournald2` commit thread, journal superblock loading/updating, commit scheduling, fast-commit buffer allocation, log-space tail accounting, feature negotiation, journal flushing/wiping/destruction, abort/error state, proc statistics, shrinker registration, slab/cache setup, and `journal_head` attachment to buffer heads.

## Main Responsibilities

- Starts and stops the per-journal kernel thread through `jbd2_journal_start_thread()`, `kjournald2()`, and `journal_kill_thread()`.
- Schedules, waits for, and forces commits through `jbd2_log_start_commit()`, `jbd2_journal_start_commit()`, `jbd2_log_wait_commit()`, `jbd2_journal_force_commit()`, and `jbd2_complete_transaction()`.
- Allocates log blocks and descriptor buffers through `jbd2_journal_next_log_block()` and `jbd2_journal_get_descriptor_buffer()`.
- Maps logical journal blocks to physical blocks via `jbd2_journal_bmap()`, supporting external fixed journals and inode-backed journals.
- Writes journal metadata buffers with magic-number escaping and frozen-data handling in `jbd2_journal_write_metadata_buffer()`.
- Loads, validates, and updates the on-disk journal superblock.
- Initializes and destroys `journal_t` instances through `jbd2_journal_init_dev()`, `jbd2_journal_init_inode()`, `jbd2_journal_load()`, and `jbd2_journal_destroy()`.

## Commit Thread and Commit Control

`kjournald2()` loops until `JBD2_UNMOUNT`, waking for explicit commit requests, commit timer expiry, freezer events, or journal shutdown. It calls `jbd2_journal_commit_transaction()` when `j_commit_request` advances beyond `j_commit_sequence`.

The thread uses:
- `j_state_lock` for commit state.
- `j_wait_commit` for commit requests/timer wakeups.
- `j_wait_done_commit` to notify waiters when commit state changes or the thread exits.
- `j_commit_timer` to wake after the running transaction’s expiry time.

`jbd2_trans_will_send_data_barrier()` lets ordered-data callers determine whether a commit will issue the needed flush/barrier, avoiding duplicate barriers when possible.

## Fast Commit Support

The file implements the JBD2-side fast commit coordination:
- `jbd2_fc_begin_commit()` serializes fast commits against full commits and existing fast commits.
- `jbd2_fc_end_commit()` clears fast-commit state and wakes waiters.
- `jbd2_fc_end_commit_fallback()` converts a failed fast commit into a full commit request.
- `jbd2_fc_get_buf()`, `jbd2_fc_wait_bufs()`, and `jbd2_fc_release_bufs()` allocate and manage fast-commit write buffers in the fast-commit journal area.

Fast commits are disabled after recovery in `journal_reset()` until the filesystem explicitly enables them again.

## Superblock and Feature Handling

`journal_load_superblock()` reads the journal superblock, validates magic, block size, format, length, start block, feature flags, checksum compatibility, checksum type, and fast-commit sizing. It initializes tail/head fields and checksum seed.

Feature APIs include:
- `jbd2_journal_check_used_features()`
- `jbd2_journal_check_available_features()`
- `jbd2_journal_set_features()`
- `jbd2_journal_clear_features()`

`jbd2_journal_set_features()` upgrades checksum-v2 requests to checksum-v3, avoids enabling checksum-v1 together with v3, initializes fast-commit layout when requested, and refreshes transaction limits.

## Flush, Wipe, Erase, and Abort Paths

`jbd2_journal_flush()` forces the running/committing transaction to finish, checkpoints all checkpoint transactions, cleans the journal tail, marks the journal empty, and optionally discards or zeroes journal blocks via `__jbd2_journal_erase()`.

`jbd2_journal_wipe()` is a pre-load operation that either ignores or clears recoverable log contents.

`jbd2_journal_abort()` records a permanent in-memory abort state, stores an errno in the journal superblock, and starts the current transaction so journaled buffers can be released. `-ESHUTDOWN` has precedence over other abort errnos because it does not imply the same fsck requirement.

## Memory, Buffer, and Inode Integration

The file creates module-global caches for revoke records/tables, journal heads, handles, JBD2 inodes, transactions, and power-of-two data-copy slabs.

`jbd2_journal_add_journal_head()`, `jbd2_journal_grab_journal_head()`, and `jbd2_journal_put_journal_head()` attach, refcount, detach, and free `journal_head` objects associated with `buffer_head`s. A buffer with `BH_JBD` gets an elevated buffer refcount and remains protected from normal buffer release until the journal head reference count reaches zero.

`jbd2_journal_init_jbd_inode()` and `jbd2_journal_release_jbd_inode()` integrate VFS inodes with ordered-data tracking, waiting for commit writeout before removing inodes from transaction lists.

## Important Invariants

- Commit state updates are protected by `j_state_lock`; transaction buffer lists by `j_list_lock`; checkpoint tail updates by `j_checkpoint_mutex`.
- Journal superblock tail updates use FUA when journal space can be reused after the update.
- `jbd2_journal_load()` starts from an abort-marked journal and clears `JBD2_ABORT` only after successful recovery.
- A clean journal is represented on disk by `s_start == 0`.
- `journal_head` removal requires no active running, next, checkpoint transaction, or transaction list membership.
- Log transaction limits must be recomputed after journal size, checksum tag format, fast-commit area, or feature changes.

## Research Notes

This file is the glue between the JBD2 transaction engine, recovery/checkpoint logic, block-device write ordering, and filesystem users such as ext4. Most correctness risks are around ordering: log-tail durability before reuse, superblock writes with barriers, buffer copy-out during commit, and consistent journal abort propagation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/recovery.c -->
# File Research: sources/os/linux/linux/fs/jbd2/recovery.c

## Role

`recovery.c` implements JBD2 on-disk journal recovery. It scans journal records after an unclean shutdown, discovers the valid transaction range, records revoke entries, replays non-revoked metadata blocks to the filesystem device, and resets the journal head/tail state for normal operation.

## Recovery Flow

The main entry point is `jbd2_journal_recover()`.

Recovery uses three passes over the log:
- `PASS_SCAN`: finds the end of valid committed transactions, validates checksums, counts revoke records, tracks the recovery head block.
- `PASS_REVOKE`: builds the revoke table so replay can skip blocks invalidated by later revokes.
- `PASS_REPLAY`: copies non-revoked journaled data blocks back to their home filesystem blocks.

If the journal is already clean (`j_tail == 0`), recovery is skipped and transaction sequence/head fields are initialized from the superblock.

## Core Helpers

- `jread()`: maps a journal offset to a device block, reads the buffer, starts direct journal readahead, validates uptodate status, and returns a `buffer_head`.
- `do_readahead()`: issues sequential readahead over up to 128 KiB of journal blocks.
- `count_tags()`: counts descriptor tags, respecting checksum tails, UUID elision, and last-tag flags.
- `read_tag_block()`: reconstructs 32-bit or 64-bit target block numbers from descriptor tags.
- `calc_chksums()`: computes legacy transaction checksum coverage across descriptor and payload blocks.
- `jbd2_do_replay()`: processes descriptor tags, reads each journal payload block, checks revokes and tag checksums, restores escaped magic values, and dirties the target filesystem buffer.
- `scan_revoke_records()`: counts or installs revoke records from revoke blocks.

## Checksums and Corruption Handling

The file supports:
- Descriptor block checksum verification with `jbd2_descriptor_block_csum_verify()`.
- Commit block checksum verification with `jbd2_commit_block_csum_verify()`.
- Partial commit block checksum verification for incomplete commit blocks.
- Per-data-block tag checksum verification with `jbd2_block_tag_csum_verify()`.

`PASS_SCAN` is careful with checksum failures because stale journal blocks can appear after lazy initialization or wraparound. It uses commit timestamps to distinguish likely stale records from real corruption where possible. Failed valid transactions set `j_failed_commit` or return `-EFSBADCRC`.

## Fast Commit Replay

`fc_do_one_pass()` replays the fast-commit area between `j_fc_first` and `j_fc_last` by calling the filesystem-provided `j_fc_replay_callback()`. It is invoked for scan and replay-style passes when fast commits are enabled, but skipped for revoke pass.

The expected commit id for fast-commit replay is based on the end transaction found by the full journal scan.

## Revoke Semantics

During `PASS_REVOKE`, revoke records are inserted through `jbd2_journal_set_revoke()`. During replay, `jbd2_journal_test_revoke()` suppresses writing any block whose transaction id is older than or equal to the latest revoke for that block. Later journal entries after a revoke can still replay.

## Completion Behavior

After recovery:
- `j_transaction_sequence` is advanced past the last recovered transaction.
- `j_head` is set to the recovery head block.
- The revoke table is cleared and any temporary oversized replay revoke table is destroyed.
- The filesystem device is synced, writeback errors are checked, and an optional flush is issued when barriers are enabled.

## Important Invariants

- Journal log offsets wrap between `j_first` and `j_last`.
- Non-scan passes must end at the same transaction id discovered by `PASS_SCAN`.
- Replay writes to `j_fs_dev`, while journal reads come from `j_dev`.
- Revoke record count from `PASS_SCAN` can trigger a larger temporary revoke hash table for replay.
- Escaped data blocks have the JBD2 magic restored before being dirtied on the filesystem device.

## Research Notes

This file is conservative about recovering as much valid data as possible while reporting I/O or checksum failures. The most subtle logic is in scan-time checksum handling, where stale wrapped journal blocks and interrupted commits must not be misinterpreted as valid transactions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/revoke.c -->
# File Research: sources/os/linux/linux/fs/jbd2/revoke.c

## Role

`revoke.c` implements JBD2 revoke records. Revokes prevent old journal records for deleted or reallocated metadata blocks from being replayed after a crash and overwriting newer contents at the same filesystem block number.

## Data Structures

- `struct jbd2_revoke_record_s`: one revoked block and its transaction sequence, stored in a hash chain.
- `struct jbd2_revoke_table_s`: hash table of revoke records with power-of-two sizing.
- `journal->j_revoke_table[2]`: double-buffered tables for running and committing transactions.
- `journal->j_revoke`: points to the current running transaction’s revoke table.

## Runtime Revoke Path

`jbd2_journal_revoke()`:
- Ensures the journal supports the revoke incompatible feature.
- Finds the target buffer if not supplied.
- Checks revoke credits.
- Marks the buffer `Revoked` and `RevokeValid` when present.
- Calls `jbd2_journal_forget()` for supplied journaled buffers.
- Inserts a revoke record for the current transaction.

`jbd2_journal_cancel_revoke()` is called when a block is journaled again in the same transaction. It clears cached revoke state and removes the hash record if needed. It also clears revoked state on hashed aliases for non-blockdev mappings.

## Commit-Time Revoke Writing

`jbd2_journal_switch_revoke_table()` swaps the running and committing revoke tables and reinitializes the new running table.

`jbd2_journal_write_revoke_records()` walks the committing revoke table, writes records into revoke descriptor blocks, deletes in-memory records, and flushes the final descriptor.

`write_one_revoke_record()` writes 32-bit or 64-bit block numbers depending on journal features and allocates new revoke descriptor buffers as needed. `flush_descriptor()` fills `r_count`, sets descriptor checksums, marks the descriptor for journal write, and submits it.

## Recovery Revoke Path

During replay:
- `jbd2_journal_set_revoke()` inserts or updates the latest transaction sequence for a revoked block.
- `jbd2_journal_test_revoke()` returns true when a replay candidate is covered by a revoke record from the same or later transaction.
- `jbd2_journal_clear_revoke()` frees all replay revoke records.

## Cache and Table Lifecycle

The file owns slab caches for revoke records and revoke table headers:
- `jbd2_journal_init_revoke_record_cache()`
- `jbd2_journal_init_revoke_table_cache()`
- `jbd2_journal_destroy_revoke_record_cache()`
- `jbd2_journal_destroy_revoke_table_cache()`

Per-journal tables are created by `jbd2_journal_init_revoke()` and destroyed by `jbd2_journal_destroy_revoke()`.

## Locking Model

The comments define the central lock model:
- The committing table is accessed only by `kjournald2`, so it needs no hash-list lock.
- The running table is accessed by holders of transaction handles and protected by `j_revoke_lock` for hash-chain modifications.
- Replay runs before the filesystem is mounted and needs no concurrent access protection.

## Important Invariants

- A block revoked then journaled in the same transaction must cancel the revoke.
- A block journaled then revoked in the same transaction must have the revoke take precedence; revoke records are written later than normal journal data.
- Data writes do not cancel revokes because old metadata replay must still be prevented.
- Revoke credits are mandatory; running out is treated as serious corruption/error.
- Destroying a revoke table asserts all hash chains are empty.

## Research Notes

The file is small but central to crash consistency. Its correctness depends on preserving the ordering relationship between journal data records and revoke descriptors, plus maintaining accurate cached revoke bits on buffer heads and aliases.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/revoke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jbd2/transaction.c -->
# File Research: sources/os/linux/linux/fs/jbd2/transaction.c

## Role

`transaction.c` implements the JBD2 transaction and handle state machine. It creates running transactions, attaches filesystem update handles, accounts journal credits and revoke credits, manages write/create/undo access for metadata buffers, marks metadata dirty, forgets or invalidates buffers, handles transaction barriers, and tracks ordered-data inode ranges.

## Transaction and Handle Lifecycle

- `jbd2_get_transaction()` initializes a new `transaction_t`, assigns a TID, sets expiry, initializes counters, and installs the commit timer.
- `jbd2__journal_start()` / `jbd2_journal_start()` allocate handles, optional reserved handles, and attach them to a running transaction.
- `start_this_handle()` handles transaction creation, barrier waiting, reserved-handle conversion, journal-space waiting, credit accounting, and `memalloc_nofs_save()`.
- `jbd2_journal_stop()` drops the handle, optionally batches synchronous writers, requests commits for sync/expired transactions, waits for sync commits, releases credits, and frees reserved handles.
- `jbd2__journal_restart()` detaches a long-running operation from one transaction, requests commit, and reattaches to a new transaction with fresh credits.

## Credit and Space Accounting

The file enforces transaction size and log-space constraints with:
- `add_transaction_credits()`
- `jbd2_journal_extend()`
- `sub_reserved_credits()`
- `jbd2_max_user_trans_buffers()`

It limits user payload to the journal’s maximum transaction buffers minus descriptor/commit overhead, limits reserved credits to half a transaction, and waits for checkpoint space before dirtying buffers that could later deadlock commit.

Revoke descriptor credits are charged based on `j_revoke_records_per_block`.

## Barriers and Update Quiescing

`jbd2_journal_lock_updates()` blocks new normal updates, waits for reserved credits and active transaction updates to drain, and then serializes special journal-locked operations through `j_barrier`.

`jbd2_journal_unlock_updates()` drops the barrier and wakes blocked starters. Reserved handles are allowed through some barriers to avoid writeback deadlocks.

## Metadata Access Paths

`jbd2_journal_get_write_access()` gives a handle permission to modify an existing metadata buffer. It checks filesystem device writeback errors, attaches a journal head, handles dirty non-JBD buffers, performs copy-out if the buffer belongs to the committing transaction, and cancels any revoke.

`jbd2_journal_get_create_access()` handles newly created locked buffers, allowing only safe states: no transaction, current transaction, or committing transaction on `BJ_Forget`.

`jbd2_journal_get_undo_access()` preserves committed data for non-rewindable operations such as bitmap updates, storing `b_committed_data` after write access succeeds.

`jbd2_write_access_granted()` is a lockless fast path that verifies a buffer is already attached to the handle’s transaction, using RCU and barriers to avoid stale `journal_head` reuse.

## Dirtying and Forgetting Buffers

`jbd2_journal_dirty_metadata()` marks a previously accessed buffer as modified, consumes one metadata credit once per transaction, sets `buffer_jbddirty`, and files it on the transaction metadata list unless it is still owned by the committing transaction.

`jbd2_journal_forget()` removes a buffer from journaling interest, handling current-transaction buffers, committing-transaction buffers, checkpointed buffers, freed buffers, and dirty/writeback cases. It may refile buffers on `BJ_Forget` so checkpoint cleanup remains ordered with the transaction deleting the block.

## Buffer List Management

The file implements transaction buffer circular lists and list transitions:
- `__blist_add_buffer()`
- `__blist_del_buffer()`
- `__jbd2_journal_temp_unlink_buffer()`
- `__jbd2_journal_unfile_buffer()`
- `__jbd2_journal_file_buffer()`
- `jbd2_journal_file_buffer()`
- `__jbd2_journal_refile_buffer()`
- `jbd2_journal_refile_buffer()`

List types include metadata, forget, shadow, and reserved buffers. Dirty state is hidden from the VM as `buffer_jbddirty` while JBD2 controls writeout.

## Folio Invalidation and Buffer Freeing

`jbd2_journal_try_to_free_buffers()` removes clean checkpoint references from a locked folio and then delegates to `try_to_free_buffers()` if no JBD buffers remain.

`jbd2_journal_invalidate_folio()` and `journal_unmap_buffer()` handle truncation invalidation. They carefully distinguish buffers with no transaction, checkpointed buffers, committing transaction buffers, and running transaction buffers. Partial-page invalidation can return `-EBUSY` if a buffer is in the committing transaction and cannot be safely discarded yet.

## Ordered Data Inode Tracking

`jbd2_journal_inode_ranged_write()` and `jbd2_journal_inode_ranged_wait()` attach `jbd2_inode` objects to the transaction inode list and track dirty page ranges. `jbd2_journal_begin_ordered_truncate()` starts writeout of truncated data when that inode’s data belongs to the committing transaction.

## Important Invariants

- A handle must not cross journals; nested starts on the same journal only bump `h_ref`.
- `t_updates` pins a transaction against commit state changes while handles are active.
- Buffers belonging to the committing transaction require frozen copy-out before current transaction modification.
- Dirty metadata buffers should be tracked as `buffer_jbddirty`, not normal `buffer_dirty`, while journal-owned.
- `b_next_transaction` represents handoff from committing to running transaction.
- Truncate invalidation relies on filesystem ordering: on-disk inode size/orphan state must be updated before data buffers are discarded.

## Research Notes

This is the highest-risk JBD2 state-machine file in the group. It encodes subtle crash-consistency and deadlock-avoidance rules around credit reservation, committing transaction copy-out, checkpoint pinning, buffer reuse after free, and ordered-data truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jbd2/transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/Kconfig -->
# File Research: sources/os/linux/linux/fs/jffs2/Kconfig

## Role

This file declares Linux Kconfig options for building and configuring JFFS2, the Journalling Flash File System v2 for MTD flash devices.

## Main Configuration Symbols

- `JFFS2_FS`: main tristate filesystem option; depends on `MTD` and selects `CRC32`.
- `JFFS2_FS_DEBUG`: integer debug verbosity, default `0`.
- `JFFS2_FS_WRITEBUFFER`: write-buffer support, default enabled; required for NAND, NOR with transparent ECC, and DataFlash.
- `JFFS2_FS_WBUF_VERIFY`: optional readback verification of write-buffer writes.
- `JFFS2_SUMMARY`: optional summary-node support for faster mount.
- `JFFS2_FS_XATTR`: extended attribute support.
- `JFFS2_FS_POSIX_ACL`: POSIX ACL support; depends on xattrs, defaults enabled, selects `FS_POSIX_ACL`.
- `JFFS2_FS_SECURITY`: security-label xattr support; depends on xattrs, defaults enabled.
- Compression options for zlib, LZO, RTIME, and Rubin compressors.

## Compression Configuration

`JFFS2_COMPRESSION_OPTIONS` exposes advanced compressor selection. Without it, conservative defaults apply:
- Zlib default enabled.
- RTIME default enabled.
- LZO default disabled.
- Rubin default disabled.

The default compression mode choice includes:
- `JFFS2_CMODE_NONE`
- `JFFS2_CMODE_PRIORITY`
- `JFFS2_CMODE_SIZE`
- `JFFS2_CMODE_FAVOURLZO`

## Integration

The symbols declared here drive conditional compilation in `fs/jffs2/Makefile` and feature availability in the JFFS2 implementation. Xattr, ACL, security label, compressor, write-buffer, and summary code are all included based on these options.

## Important Invariants

- JFFS2 is restricted to MTD devices, not normal block devices.
- POSIX ACL support is layered on xattr support.
- Removing compressors may make existing filesystems unreadable.
- Enabling experimental/less common compressors can reduce compatibility with older kernels or bootloaders.

## Research Notes

This file is the feature gate for the JFFS2 source directory. Most runtime subsystems in this group (`acl.c`, background GC, build/mount code) depend on the base `JFFS2_FS`, while ACL code is only built with `JFFS2_FS_POSIX_ACL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/Makefile -->
# File Research: sources/os/linux/linux/fs/jffs2/Makefile

## Role

This Makefile defines how the JFFS2 filesystem object is built and which source files are included under each Kconfig feature.

## Build Composition

The main object is:

- `obj-$(CONFIG_JFFS2_FS) += jffs2.o`

The base `jffs2-y` object includes core compression selection, directory/file operations, ioctl, node lists, allocation, read/write, node management, inode reading, scanning, garbage collection, symlink, build, erase, background GC, filesystem glue, writev, superblock, and debug code.

## Conditional Objects

Feature-dependent additions include:
- `wbuf.o` for `CONFIG_JFFS2_FS_WRITEBUFFER`.
- `xattr.o`, `xattr_trusted.o`, and `xattr_user.o` for `CONFIG_JFFS2_FS_XATTR`.
- `security.o` for `CONFIG_JFFS2_FS_SECURITY`.
- `acl.o` for `CONFIG_JFFS2_FS_POSIX_ACL`.
- `compr_rubin.o`, `compr_rtime.o`, `compr_zlib.o`, and `compr_lzo.o` for compressor options.
- `summary.o` for `CONFIG_JFFS2_SUMMARY`.

## Integration

This file is the compile-time bridge from Kconfig options to source modules. The files researched here map directly into this build:
- `build.o` and `background.o` are always included with JFFS2.
- `acl.o` is included only when POSIX ACL support is enabled.

## Research Notes

The Makefile confirms that mount/build and GC thread code are core JFFS2 behavior, while ACL support is optional and depends on the xattr/ACL configuration path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/acl.c -->
# File Research: sources/os/linux/linux/fs/jffs2/acl.c

## Role

`acl.c` implements JFFS2 POSIX ACL support on top of JFFS2 extended attributes. It converts ACLs between Linux `struct posix_acl` and the compact JFFS2 on-flash ACL format, reads and writes ACL xattrs, updates inode mode bits for access ACLs, and initializes inherited ACLs during inode creation.

## On-Flash ACL Encoding

The file supports:
- `struct jffs2_acl_header` with `JFFS2_ACL_VERSION`.
- Short entries for `ACL_USER_OBJ`, `ACL_GROUP_OBJ`, `ACL_MASK`, and `ACL_OTHER`.
- Full entries with id fields for named `ACL_USER` and `ACL_GROUP`.

Helpers:
- `jffs2_acl_size()` computes serialized size.
- `jffs2_acl_count()` validates serialized size and computes entry count.
- `jffs2_acl_from_medium()` parses flash/xattr bytes into a `posix_acl`.
- `jffs2_acl_to_medium()` serializes a `posix_acl` into JFFS2 byte order.

## ACL Read Path

`jffs2_get_acl()`:
- Rejects RCU ACL lookup with `-ECHILD`.
- Maps `ACL_TYPE_ACCESS` to `JFFS2_XPREFIX_ACL_ACCESS`.
- Maps `ACL_TYPE_DEFAULT` to `JFFS2_XPREFIX_ACL_DEFAULT`.
- Uses `do_jffs2_getxattr()` first to determine size, then to read the value.
- Returns `NULL` for absent ACL xattrs (`-ENODATA` or `-ENOSYS`) and parsed ACLs otherwise.

## ACL Write Path

`__jffs2_set_acl()` serializes an ACL and writes it through `do_jffs2_setxattr()`. A NULL ACL removes the xattr and treats missing xattrs as success.

`jffs2_set_acl()` handles VFS ACL updates:
- For access ACLs, calls `posix_acl_update_mode()` and updates inode mode/ctime through `jffs2_do_setattr()` when required.
- For default ACLs, rejects non-directory targets with `-EACCES` when an ACL is being set.
- Updates the inode ACL cache with `set_cached_acl()` after a successful write.

## Inode Creation ACL Initialization

`jffs2_init_acl_pre()`:
- Initializes inode ACL cache state.
- Calls `posix_acl_create()` to compute inherited default/access ACLs and adjusted mode.
- Stores inherited ACLs temporarily in inode cache fields.

`jffs2_init_acl_post()`:
- Writes cached default and access ACLs to xattrs after the inode has been created on flash.

This two-stage pattern lets JFFS2 apply ACL-derived mode during inode creation while writing ACL xattrs only after the new inode exists.

## Important Invariants

- ACL version must match `JFFS2_ACL_VERSION`.
- Serialized sizes must exactly match the expected short/full entry layout.
- Named user/group ids are converted through `init_user_ns`.
- Default ACLs are valid only on directories.
- Access ACL mode changes must be persisted through JFFS2 setattr before writing the ACL xattr.

## Research Notes

The file is a thin but important adapter between Linux POSIX ACL APIs and JFFS2’s xattr subsystem. The main risk areas are serialized ACL validation, exact size accounting, id mapping, and keeping inode mode bits consistent with access ACLs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/acl.h -->
# File Research: sources/os/linux/linux/fs/jffs2/acl.h

## Role

`acl.h` declares the JFFS2 on-flash ACL structures and exposes ACL helper prototypes or no-op definitions depending on `CONFIG_JFFS2_FS_POSIX_ACL`.

## Structures

- `struct jffs2_acl_entry`: full ACL entry with tag, permissions, and id.
- `struct jffs2_acl_entry_short`: compact ACL entry with tag and permissions only.
- `struct jffs2_acl_header`: ACL version plus flexible array of full entries.

The implementation in `acl.c` stores the first four base ACL entry types as short entries and named user/group entries as full entries.

## Conditional API

When POSIX ACL support is enabled, the header declares:
- `jffs2_get_acl()`
- `jffs2_set_acl()`
- `jffs2_init_acl_pre()`
- `jffs2_init_acl_post()`

When disabled:
- `jffs2_get_acl` and `jffs2_set_acl` are defined as `NULL`.
- ACL initialization helpers become no-op macros returning success.

## Integration

The header is included by JFFS2 code that needs ACL hooks without requiring the ACL implementation to be present in all builds. It lets inode and VFS operation setup compile cleanly with or without POSIX ACL support.

## Important Invariants

- Structure field types use JFFS2 endian-aware integer aliases (`jint16_t`, `jint32_t`).
- Callers must tolerate ACL hooks being `NULL` when the feature is disabled.
- The serialized layout must stay compatible with `acl.c` parsing and writing.

## Research Notes

This file is primarily an ABI/layout definition for JFFS2 ACL xattrs plus a build-time compatibility shim.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/background.c -->
# File Research: sources/os/linux/linux/fs/jffs2/background.c

## Role

`background.c` implements the optional per-filesystem JFFS2 background garbage-collection kernel thread. The thread wakes when flash-space conditions require GC, performs GC passes, handles freezer and signal events, and exits cleanly on unmount or fatal GC-space failure.

## Public Entry Points

- `jffs2_garbage_collect_trigger()`: called with `erase_completion_lock` held; sends `SIGHUP` to the GC task if it exists and `jffs2_thread_should_wake()` says work is needed.
- `jffs2_start_garbage_collect_thread()`: initializes start/exit completions, starts `jffs2_garbage_collect_thread()` with an MTD-indexed thread name, waits until the thread records itself, and returns the PID or error.
- `jffs2_stop_garbage_collect_thread()`: sends `SIGKILL` to the GC task under `erase_completion_lock` and waits for the exit completion.

## Thread Loop

`jffs2_garbage_collect_thread()`:
- Allows `SIGKILL`, `SIGSTOP`, and `SIGHUP`.
- Stores `current` in `c->gc_task` and completes startup.
- Lowers priority with `set_user_nice(current, 10)`.
- Marks itself freezable.
- Sleeps when `jffs2_thread_should_wake()` is false.
- Adds a 50 ms interruptible delay each cycle to avoid starving userspace during mount-time or heavy GC work.
- Handles freezer events and pending signals.
- Blocks `SIGHUP` while running a GC pass so wakeup signals do not interrupt the pass.
- Calls `jffs2_garbage_collect_pass(c)` until killed or until `-ENOSPC` aborts the thread.

## Signal Semantics

- `SIGHUP`: wake/request another GC check.
- `SIGSTOP`: enter kernel signal stop.
- `SIGKILL`: exit thread, used by unmount.
- Freezer: calls `try_to_freeze()` and restarts wake checks after thaw.

## Important Invariants

- `c->gc_task` is protected by `erase_completion_lock`.
- `jffs2_start_garbage_collect_thread()` must only run when no GC thread exists.
- Thread startup and shutdown are synchronized with completions.
- `jffs2_garbage_collect_trigger()` assumes the caller already holds `erase_completion_lock`.

## Research Notes

This file is operational glue around JFFS2 garbage collection rather than the GC algorithm itself. Its main concerns are avoiding mount-time/user-visible starvation, cooperating with suspend/freezer, and making unmount shutdown deterministic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/background.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jffs2/build.c -->
# File Research: sources/os/linux/linux/fs/jffs2/build.c

## Role

`build.c` builds JFFS2 in-memory filesystem structures at mount time after scanning flash. It initializes eraseblock state, scans raw nodes, reconstructs inode and directory link relationships, removes unlinked inode trees, initializes xattr state, computes GC reservation thresholds, and performs final list rotation for wear leveling.

## Mount Entry Point

`jffs2_do_mount_fs()`:
- Initializes free size and block count from flash/sector size.
- Allocates the eraseblock array with `vzalloc()` or `kzalloc()`.
- Initializes each eraseblock offset and free size.
- Initializes all eraseblock state lists.
- Sets `highest_ino`, initializes summary support with `jffs2_sum_init()`.
- Calls `jffs2_build_filesystem()`.
- Computes trigger levels with `jffs2_calc_trigger_levels()`.

On build failure it frees inode caches, raw node refs, summary state, and eraseblock storage.

## Filesystem Build Passes

`jffs2_build_filesystem()` runs the mount reconstruction sequence:
- Sets `JFFS2_SB_FLAG_SCANNING` and calls `jffs2_scan_medium()` to build inode caches and physical node references.
- Sets `JFFS2_SB_FLAG_BUILDING`.
- Pass 1: for every inode with scanned dirents, `jffs2_build_inode_pass1()` increments child inode link counts and detects possible directory hardlinks.
- Pass 2: removes inodes with zero link count using `jffs2_build_remove_unlinked_inode()`.
- Pass 2a: recursively processes children that became unlinked through dead directory removal.
- Final pass: frees temporary dirent lists and, for directories, records parent inode number in `pino_nlink`.
- Builds the xattr subsystem through `jffs2_build_xattr_subsystem()`.
- Clears build flags, rotates lists for wear leveling, and returns success.

## Directory and Link Reconstruction

`jffs2_build_inode_pass1()` walks temporary scanned dirents:
- Ignores deletion dirents with `ino == 0`.
- Resolves child inode caches.
- Marks raw dirent nodes obsolete if the referenced child inode does not exist.
- Reuses the dirent `raw/ic` union to store child inode cache pointers after validation.
- Increments `pino_nlink`.
- Marks directories and detects possible hard-linked directories.

The final cleanup pass converts directory child `pino_nlink` from temporary link count into parent inode number, warning if directory hardlinks remain.

## Unlinked Inode Removal

`jffs2_build_remove_unlinked_inode()`:
- Marks every raw node for an unlinked inode obsolete.
- If the inode was a directory, walks its child dirents and decrements each child’s temporary link count.
- Adds children that become unlinked to a `dead_fds` work list for later cleanup.
- Leaves inode cache deletion to erase code after physical nodes are fully gone.

This avoids recursion while cleaning dead directory subtrees discovered during mount.

## GC Trigger Levels

`jffs2_calc_trigger_levels()` computes reservation thresholds:
- Blocks needed to permit deletion.
- Blocks needed to permit writes.
- Background GC wake threshold.
- GC merge threshold.
- Bad-block GC threshold.
- Dirty-space threshold below which GC is not worth attempting.
- Very-dirty-block trigger threshold, larger when obsolete nodes can be marked on flash.

These fields drive space reservation and background GC wake behavior elsewhere in JFFS2.

## Important Invariants

- During build, `pino_nlink` is first used as a link count and later as parent inode number for directories.
- Temporary `scan_dents` must be freed on both success and failure.
- Missing child inode references are treated as obsolete dirent nodes.
- Directory hardlinks are detected and reported because normal directory topology should be single-parent.
- Xattr subsystem build happens only after core inode/dirent reconstruction.
- Eraseblock arrays mirror the physical MTD eraseblock layout exactly.

## Research Notes

This file is mount-time reconstruction logic for a log-structured flash filesystem. Its correctness depends on carefully interpreting scanned historical nodes, deletion dirents, obsolete nodes, and link counts so the in-memory inode tree reflects the latest valid flash state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jffs2/build.c -->