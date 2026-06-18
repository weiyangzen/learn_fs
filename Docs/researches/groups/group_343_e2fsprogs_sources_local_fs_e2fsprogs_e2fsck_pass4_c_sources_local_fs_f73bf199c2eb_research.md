# Group Research: group_343_e2fsprogs_sources_local_fs_e2fsprogs_e2fsck_pass4_c_sources_local_fs_f73bf199c2eb

Scope: `Docs/research_subset_a.md`; source tree `sources/local-fs/e2fsprogs` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass4.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/pass4.c

This file implements e2fsck pass 4, which validates inode reference counts after earlier passes have discovered allocated inodes, directory references, bad-block inodes, imagic inodes, and extended-attribute inode references.

Main entry point:
- `e2fsck_pass4(e2fsck_t ctx)` iterates every inode from 1 through `s_inodes_count`, skipping reserved/special inodes and inodes excluded by pass-1 maps.
- It compares `ctx->inode_link_info`, the inode’s stored `i_links_count`, and `ctx->inode_count`, the count discovered from directory traversal.
- It frees pass-4-owned structures at completion: `inode_link_info`, `inode_count`, `inode_bb_map`, `inode_imagic_map`, and `ea_inode_refs`.

Important helpers:
- `disconnect_inode()` handles allocated inodes not connected to the directory tree. It can clear zero-length regular files or directories with no blocks and no EA block, or reconnect other unattached inodes to `lost+found`.
- `check_ea_inode()` handles ext4 EA-inode reference accounting. It clears spurious `EXT4_EA_INODE_FL` on normal files when appropriate, treats real EA-inode references as one logical link for pass-4 purposes, and can repair stored EA inode refcounts.

Control flow and repairs:
- Starts readahead of block/inode bitmaps for pass 5 when possible.
- Shows `PR_4_PASS_HEADER` outside preen mode.
- For each live inode, fetches expected link count and observed directory count.
- If EA inode refs exist, consolidates EA-inode status before ordinary link-count checks.
- If observed links are zero, calls `e2fsck_process_bad_inode()` and then `disconnect_inode()`.
- If a directory’s observed link count exceeds `EXT2_LINK_MAX`, enables `dir_nlink` if needed and treats the link count as overflow.
- For mismatched link counts, reports inconsistent cached counts and either fixes `i_links_count` or marks filesystem invalid if the user declines.

Integration points:
- Uses `problem.h` codes `PR_4_*` and central `fix_problem()` prompting.
- Uses ext2fs inode bitmaps and icount APIs.
- Updates quota accounting when deleting zero-length disconnected inodes.
- Coordinates with `lost+found` reconnection and pass-5 bitmap loading.

Risk notes:
- The loop is protected against inode-number wraparound.
- `last_ino` avoids repeated inode reads but is reset after reconnection.
- EA-inode logic distinguishes old Lustre-style EA inodes by `i_ctime == i_atime`.
- Repair decisions depend heavily on user/preen policy from `problem.c`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass5.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/pass5.c

This file implements e2fsck pass 5, which reconciles computed block/inode usage maps with on-disk bitmaps and group/superblock summary counters.

Main entry point:
- `e2fsck_pass5(e2fsck_t ctx)` reads bitmaps, checks block bitmaps, inode bitmaps, bitmap tail padding, metadata checksums, then frees pass-5 maps: `inode_used_map`, `inode_dir_map`, `block_found_map`, and `block_metadata_map`.

Block bitmap checking:
- `check_block_bitmaps()` compares `ctx->block_found_map` against `fs->block_map`.
- It validates bitmap endpoints before scanning.
- It groups adjacent mismatches into compact single/range problem reports via `print_bitmap_problem()`.
- It has a fast path that compares entire group bitmap buffers with `memcmp` when not discarding and not on the last group.
- It handles bigalloc cluster conversions via `B2C`, `C2B`, and cluster comparison macros.
- If repairs are accepted through `PR_LATCH_BBITMAP`, it replaces `fs->block_map` with `block_found_map`, sets padding, marks the block bitmap dirty, and rescans counts.
- It updates per-group and superblock free-block counters.

Inode bitmap checking:
- `check_inode_bitmaps()` compares `ctx->inode_used_map` against `fs->inode_map`.
- It validates bitmap endpoints, handles groups marked `EXT2_BG_INODE_UNINIT`, counts free inodes and directory inodes, and repairs mismatches through `PR_LATCH_IBITMAP`.
- It updates per-group free-inode counts, used-directory counts, and the superblock free-inode count.
- It also supports discard of unused inode-table ranges when safe.

Discard support:
- `e2fsck_discard_blocks()` disables discard if the filesystem has already changed or if discard fails.
- `e2fsck_discard_inodes()` maps unused inode ranges to full inode-table blocks and discards only when discard zeroes data.

Checksum and padding checks:
- `check_inode_bitmap_checksum()` and `check_block_bitmap_checksum()` verify metadata checksums when `metadata_csum` is enabled and the bitmap has not already been dirtied.
- `check_inode_end()` and `check_block_end()` temporarily extend bitmap ends to verify padding bits past real inode/block ranges and mark bitmaps dirty when tail padding must be fixed.

Integration points:
- Relies on pass 1/2 maps as truth: `block_found_map`, `inode_used_map`, `inode_dir_map`.
- Uses `problem.c` latches for batch bitmap fixes and summary-counter repairs.
- Uses ext2fs bitmap copy, range extraction, padding, checksum, group descriptor, and dirty-marking APIs.
- Emits progress over two group-count spans: block pass then inode pass.

Risk notes:
- If bitmap replacement allocation/copy fails, pass 5 raises fatal copy errors.
- Any bitmap mismatch disables discard to avoid discarding blocks on a corrupt filesystem.
- Uninitialized group flags are cleared only after a prompted fix when live usage is found.
- Counter rescans after bitmap replacement are necessary because the first scan observed the old on-disk bitmap.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass5.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/problem.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/problem.c

This file is e2fsck’s central problem registry and repair-decision engine. It maps numeric `PR_*` codes to localized descriptions, prompts, default/preen behavior, latches, fatality, logging, and follow-up actions.

Core data:
- `prompt[]` maps internal prompt IDs to user prompts such as Fix, Clear, Relocate, Connect to `/lost+found`, Clone, Delete, Optimize, and Clear flag.
- `preen_msg[]` maps prompt IDs to automatic-action text in preen mode.
- `problem_table[]` is the large ordered registry of all e2fsck problem codes from pre-pass 1 through post-pass 5.
- `pr_latch_info[]` defines grouped problem latches, including illegal blocks, bad-block inode blocks, inode/block bitmap differences, relocation hints, duplicate blocks, orphan-list refugees, oversized inodes, directory optimization, group checksum fixes, and extent optimization.

Main behavior:
- `fix_problem(ctx, code, pctx)` looks up the problem, applies one-time profile configuration overrides, prints/logs the message, asks or auto-selects an answer, updates filesystem validity and fixed-problem flags, handles fatal/preen behavior, emits problem-log XML-like entries, and executes chained `PR_AFTER_CODE` prompts.
- `end_problem_latch()` emits latch end messages and clears variable latch state.
- `set_latch_flags()` and `get_latch_flags()` manipulate latch state.
- `clear_problem_context()` zeroes a context and initializes sentinel values for `blkcount` and `group`.
- Under `UNITTEST`, `verify_problem_table()` checks ordering/duplicates.

Problem table coverage:
- Pre-pass 1: superblock, group descriptors, journal, orphan list, quota, MMP, feature compatibility, orphan-file issues.
- Pass 1: inode modes, sizes, block/extent validity, EA blocks, quota/orphan inodes, casefold/encryption, inline data, bigalloc, EA inodes.
- Pass 1B/1C/1D/1E: duplicate block rescans, directory scans for duplicate-block inodes, duplicate reconciliation, extent tree optimization.
- Pass 2: directory structure, dirents, filetypes, htree validation, checksums, encryption/casefold directory constraints, EA inode directory links.
- Pass 3/3A: directory connectivity, root and lost+found creation, parent repair, directory rehash/optimization.
- Pass 4: unattached inodes, bad refcounts, EA-inode refs, dir_nlink, spurious EA inode flags.
- Pass 5: bitmap differences, bitmap padding, summary counters, uninitialized group flags, bitmap checksums.
- Post-pass 5: journal recreation, quotas, flushing, orphan-file maintenance.

Configuration and prompting:
- Per-problem profile keys can override description, preen/no defaults, message suppression, force-no behavior, max count, and “not a fix” semantics.
- `PR_PREEN_OK` controls automatic preen repair; missing it with a prompt triggers `preenhalt()`.
- `PR_NO_OK` allows a negative answer without invalidating the filesystem.
- `PR_NOT_A_FIX` prevents accepted optimization prompts from counting as fixed corruption.
- `PR_FATAL` calls `fatal_error()` after printing.
- `PR_AFTER_CODE` chains to a second problem code.

Logging:
- Normal output goes through `print_e2fsck_message()`.
- `ctx->logf` receives human-readable problem messages and chosen answers.
- `ctx->problem_logf` receives structured `<problem .../>`, `<header .../>`, and `<suppressed .../>` records with fields copied from `problem_context`.

Risk notes:
- The problem table must remain sorted for `UNITTEST` verification even though runtime lookup is linear.
- Static problem entries are mutated after profile overrides by setting `PR_CONFIG`; this is intentional but means behavior is process-global after first use.
- Latches centralize user choice across many individual findings, so callers must end latches to clear transient state and emit closing prompts.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/problem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/problem.h -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/problem.h

This header defines the public problem-code namespace and context structure used by e2fsck passes when reporting and repairing filesystem inconsistencies.

Core types:
- `problem_t` is a 32-bit problem code.
- `struct problem_context` carries optional fields used by message formatting and structured logs: error code, inode numbers, directory inode, inode pointer, dirent pointer, block numbers, logical block count, group, checksums, generic numeric fields, and string data.

Latch definitions:
- `PR_LATCH_MASK` extracts latch bits from problem flags.
- Latches group repeated repair decisions: illegal inode blocks, bad-block inode blocks, inode/block bitmaps, relocation hints, duplicate blocks, low dtime/orphan refugees, oversized inodes, directory optimization, group checksums, and extent optimization.
- `PRL_*` flags record yes/no, latched, and suppress state.

Problem-code layout:
- Pre-pass 1 codes start at `0x000001`.
- Pass 1 starts at `0x010000`.
- Pass 1B/1C/1D/1E occupy `0x011000` through `0x014000`.
- Pass 2 starts at `0x020000`.
- Pass 3 starts at `0x030000`, pass 3A at `0x031000`.
- Pass 4 starts at `0x040000`.
- Pass 5 starts at `0x050000`.
- Post-pass 5 starts at `0x060001`.

Notable groups:
- Pre-pass 1 covers superblock, journal, group descriptor, quota, MMP, metadata checksum, resize inode, orphan list, and orphan-file validation.
- Pass 1 covers inode/block/extent/EA/inline-data/casefold/encryption/quota/orphan-file validation.
- Pass 2 covers directory entries, filetypes, htree structure, checksums, encrypted/casefolded directory consistency, and EA-inode directory links.
- Pass 3 and 3A cover directory connectivity and rehash/optimization.
- Pass 4 covers link counts and EA inode refcounts.
- Pass 5 covers bitmap differences, padding, group summary counters, uninitialized group flags, and bitmap checksums.
- Post-pass 5 covers journal recreation, quota updates, block-group checksums, flush errors, and orphan-file cleanup.

Declared API:
- `fix_problem()`
- `end_problem_latch()`
- `set_latch_flags()`
- `get_latch_flags()`
- `clear_problem_context()`
- `print_e2fsck_message()`

Integration points:
- All pass files include this header to report problems by stable numeric code.
- `problem.c` supplies the table mapping these codes to text and behavior.
- Message formatting uses `problem_context` fields to expand symbolic placeholders.

Risk notes:
- Codes are externally meaningful to logs, tests, translation strings, and configuration profiles, so renumbering is risky.
- Comments serve as a compact semantic registry; adding a code requires synchronized updates in `problem.c`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/problem.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/problemP.h -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/problemP.h

This private header defines the internal structures and flags used by `problem.c`.

Core structures:
- `struct e2fsck_problem` stores one problem-table entry: code, localized description, prompt ID, behavior flags, optional chained problem code, runtime count, and max-count suppression threshold.
- `struct latch_descr` stores a latch group: latch code, question problem, end-message problem, and latch state flags.

Problem flags:
- `PR_PREEN_OK`: preen can answer automatically without halting.
- `PR_NO_OK`: a no answer does not mark the filesystem invalid.
- `PR_NO_DEFAULT`: default answer is no.
- `PR_MSG_ONLY`: print-only problem.
- `PR_FATAL`: fatal after reporting.
- `PR_AFTER_CODE`: ask/report another code after this one.
- `PR_PREEN_NOMSG`, `PR_NO_NOMSG`, `PR_PREEN_NOHDR`: suppress variants.
- `PR_NOCOLLATE`: avoid default answer collation.
- `PR_PREEN_NO`, `PR_FORCE_NO`: force no in certain modes.
- `PR_CONFIG`: profile overrides have already been applied.
- `PR_NOT_A_FIX`: yes answer is not counted as repaired corruption.
- `PR_HEADER`: structured pass header marker.

Integration points:
- Included by `problem.c` only.
- Complements the public problem-code declarations in `problem.h`.

Risk notes:
- Latch flag bit positions overlap intentionally with `PR_LATCH_MASK`; new flags must avoid the reserved latch bit range.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/problemP.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/quota.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/quota.c

This file handles ext4 quota inode validation and hiding during e2fsck setup.

Main functions:
- `e2fsck_hide_quota(ctx)` moves visible quota files into the hidden quota inode numbers recorded by ext4 when the filesystem has the quota feature and is not read-only.
- `e2fsck_validate_quota_inodes(ctx)` validates quota inode numbers in the superblock and clears invalid references.
- `move_quota_inode(fs, from_ino, to_ino, qtype)` performs the actual inode move.

Move behavior:
- Ensures bitmaps are loaded.
- Reads the visible quota inode.
- Rewrites it as a regular `0600` immutable file at the hidden quota inode number, preserving extents flag when supported.
- Unlinks the old named quota file from root.
- Updates inode allocation stats and clears the original inode on disk.

Validation:
- Rejects quota inode numbers that point to reserved special inodes or exceed `s_inodes_count`.
- Reports `PR_0_INVALID_QUOTA_INO` and clears the superblock field if accepted.

Integration points:
- Uses quota helpers `quota_type2inum()`, `quota_sb_inump()`, and `quota_get_qf_name()`.
- Uses problem codes `PR_0_HIDE_QUOTA` and `PR_0_INVALID_QUOTA_INO`.
- Marks the superblock dirty after modifying quota inode fields.

Risk notes:
- `pctx.dir = 2` in `e2fsck_hide_quota()` is explicitly a best guess for root.
- If move steps fail, the caller continues to the next quota type without updating the superblock field.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/readahead.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/readahead.c

This file implements metadata prefetch helpers used to reduce e2fsck runtime.

Directory block readahead:
- `e2fsck_readahead_dblist(fs, flags, dblist, start, count)` iterates a directory block list and coalesces contiguous physical runs.
- `readahead_dir_block()` accumulates runs and issues `io_channel_cache_readahead()` when a run breaks.
- `E2FSCK_RA_DBLIST_IGNORE_BLOCKCNT` treats each dir block entry as one block regardless of `blockcnt`.

Bitmap-driven readahead:
- `e2fsck_readahead(fs, flags, start, ngroups)` builds a temporary block bitmap of metadata blocks to prefetch, then sends contiguous set-bit ranges to the io channel.
- It can mark superblocks, group descriptor tables, block bitmaps, inode bitmaps, and inode table ranges.
- It skips uninitialized or fully unused bitmap/table groups where appropriate.
- Helper functions `mark_bmap()` and `mark_bmap_range()` avoid range-error noise by bounds-checking before marking.

Capability and sizing:
- `e2fsck_can_readahead(fs)` probes support by attempting a one-block readahead.
- `e2fsck_guess_readahead(fs)` estimates a useful readahead window as two inode-table groups, but disables it if that would exceed 1/50 of memory.

Integration points:
- Called by pass 4 to prefetch bitmaps before pass 5.
- Uses ext2fs group-location and bitmap APIs plus io-channel cache readahead support.

Risk notes:
- Readahead failures propagate as errcodes but do not themselves repair metadata.
- The temporary bitmap bounds checks intentionally trade completeness for quiet failure on unexpected geometry.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/readahead.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/recovery.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/recovery.c

This file is JBD2 journal recovery code adapted for e2fsprogs userland and kernel builds. It scans, revokes, and replays journal transactions after an unclean shutdown.

Core recovery model:
- `jbd2_journal_recover(journal)` performs three passes: `PASS_SCAN`, `PASS_REVOKE`, and `PASS_REPLAY`.
- `jbd2_journal_skip_recovery(journal)` scans only enough to advance transaction state while discarding pending journal contents.
- `struct recovery_info` records start/end transaction IDs and replay/revoke statistics.

Journal reading:
- `jread()` maps a journal offset to a device block, reads it through buffer heads, does readahead where available, and validates bounds.
- Kernel builds include `do_readahead()` to issue sequential journal reads in chunks.
- `wrap()` wraps log offsets across the journal ring, respecting fast-commit bounds when enabled.

Checksums and tags:
- `jbd2_descriptor_block_csum_verify()` verifies descriptor/revoke block tail checksums.
- `jbd2_commit_block_csum_verify()` verifies commit block checksums.
- `jbd2_block_tag_csum_verify()` verifies individual replayed data block checksums.
- `count_tags()` and `read_tag_block()` parse descriptor tags, including 64-bit block numbers and UUID elision.
- `calc_chksums()` computes transaction checksums for older checksum formats during scan.

Main pass engine:
- `do_one_pass()` walks transactions in sequence, reading descriptor, commit, and revoke blocks.
- `PASS_SCAN` finds the valid end of the log and handles checksum failures, async commit, stale lazy-init journal blocks, and commit-time ordering.
- `PASS_REVOKE` scans revoke records into the revoke table.
- `PASS_REPLAY` copies unrecalled journaled blocks back to the filesystem device, honoring revoke records and escaped magic values.
- Fast commits are delegated to `fc_do_one_pass()` through `j_fc_replay_callback`.

Revoke scanning:
- `scan_revoke_records()` validates record count, chooses 32-bit or 64-bit block record size, and calls `jbd2_journal_set_revoke()` for each revoked block.

Integration points:
- Uses revoke helpers from `revoke.c`.
- Uses JBD2 journal superblock fields, feature flags, buffer-head IO, and checksum helpers.
- After recovery, clears revoke state, syncs the block device, and flushes if barriers are enabled.

Risk notes:
- Recovery can continue after some replay IO errors but reports failure at the end.
- Checksum mismatch handling distinguishes likely stale journal blocks from corruption using commit-time monotonicity.
- Replayed buffers are marked dirty and released; final persistence depends on later sync/flush.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/region.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/region.c

This file provides a small region-allocation tracker used to detect overlapping allocations within an address range.

Core data:
- `struct region_struct` stores minimum/maximum bounds, a sorted linked list of allocated extents, and a cached `last` pointer.
- `struct region_el` stores half-open `[start, end)` allocated intervals.

API:
- `region_create(min, max)` allocates and initializes an empty region.
- `region_free(region)` frees all interval nodes and the region object.
- `region_allocate(region, start, n)` attempts to reserve `[start, start+n)`.

Allocation semantics:
- Returns `0` for successful allocation.
- Returns `1` for conflict or zero-length allocation.
- Returns `-1` for out-of-range or allocation failure.
- Maintains the interval list sorted and merged.
- Fast path extends or appends after `region->last` when allocations are monotonic.
- Detects overlaps covering start, end, or entire existing intervals.
- Merges adjacent intervals on either side.

Test program:
- Under `TEST_PROGRAM`, includes a bytecode-like scripted test harness with create, allocate, print, and free operations.

Integration points:
- Included via e2fsck internals as a utility for collision detection, especially metadata/EA/extent allocation validation.

Risk notes:
- The API treats `n == 0` as a non-error conflict-like return of `1`.
- `end = start+n` assumes caller-provided values do not overflow `region_addr_t`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/region.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/rehash.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/rehash.c

This file rebuilds and optionally compresses ext4 indexed directories during pass 3A.

Scheduling API:
- `e2fsck_rehash_dir_later(ctx, ino)` adds a directory inode to `ctx->dirs_to_hash`.
- `e2fsck_dir_will_be_rehashed(ctx, ino)` reports whether a directory will be rebuilt because it is listed or all directories are being compressed.
- `e2fsck_rehash_directories(ctx)` runs pass 3A over either all directories or the scheduled list.

Read/index phase:
- `fill_dir_block()` reads every directory block into a full in-memory buffer and builds a `hash_entry` array for real entries.
- It ignores `.` and `..` when not compressing, tracks the parent from `..`, validates rec_len/name_len constraints, tolerates checksum errors while reading, and handles metadata checksum tail entries.
- It computes hashes via `ext2fs_dirhash2()` unless hashes are already stored in dirents or the directory is being compressed.

Sorting and duplicate handling:
- `hash_cmp()` sorts by major hash, minor hash, and name/inode tie-breakers.
- `name_cmp()` and `name_cf_cmp()` support bytewise and casefold-aware comparisons.
- `duplicate_search_and_fix()` removes exact duplicate dirents pointing to the same inode, drops unrenamable encrypted duplicates, or mutates names using `mutate_name()` until unique.
- After any duplicate fix, entries are resorted.

Output construction:
- `copy_dir_entries()` packs valid entries into output leaf blocks with configured slack for indexed directories and minimum slack for compressed directories.
- It initializes directory entry checksum tails when metadata checksums are enabled.
- `set_root_node()` creates the htree root block with `.` and `..`, chooses SipHash for hash-in-dirent directories, and sets root limits.
- `set_int_node()`, `alloc_blocks()`, and `calculate_tree()` build one- or two-level htree index nodes over the leaf blocks.
- `write_directory()` expands the directory, writes rebuilt blocks, updates `EXT2_INDEX_FL`, sets inode size, and truncates excess blocks with `ext2fs_punch()`.

Main per-directory function:
- `e2fsck_rehash_dir(ctx, ino, pctx)` reads the inode, skips inline-data directories, allocates full-directory memory, indexes entries, falls back to compression if too small for htree, fixes duplicates, builds output blocks/tree, writes the directory, adjusts quota if size shrank, and schedules/checks extent rebuild.

Integration points:
- Uses `problem.c` codes for pass 3A and duplicate directory entries.
- Uses ext2fs block iteration, directory block read/write, dirhash, casefold, htree, allocation, and punch APIs.
- Integrates with quota accounting and extent-tree rebuild/convert paths.

Risk notes:
- The algorithm intentionally uses memory proportional to roughly twice directory size.
- Encrypted duplicate names cannot be safely mutated without a key, so repair can only clear them.
- `outdir->buf` may be reallocated while tree nodes are being built, so offsets are saved and pointers recomputed.
- `lost+found` is special-cased so extra directory blocks are not released during writeback.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/rehash.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/revoke.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/revoke.c

This file implements JBD2 revoke handling for commit-time journal records and recovery-time replay suppression.

Purpose:
- A revoke record prevents an old journaled metadata block from being replayed over newer data after a block has been freed and reused.
- Revoke semantics handle ordering: later journal data can override earlier revoke, while later revoke suppresses earlier journal data.

Data structures:
- `struct jbd2_revoke_record_s` records a revoked block and transaction sequence.
- `struct jbd2_revoke_table_s` is a power-of-two hash table of revoke records.
- Two revoke tables alternate between running and committing transactions.

Cache/table lifecycle:
- `jbd2_journal_init_revoke_record_cache()` and `jbd2_journal_init_revoke_table_cache()` create slab caches in kernel builds.
- Destroy helpers tear them down.
- `jbd2_journal_init_revoke()` allocates two hash tables and initializes locking.
- `jbd2_journal_destroy_revoke()` destroys empty tables.

Commit-time revoke path, kernel-only:
- `jbd2_journal_revoke(handle, blocknr, bh_in)` sets the journal revoke feature, marks matching buffers revoked/revoke-valid, calls `jbd2_journal_forget()` when needed, consumes revoke credits, and inserts a revoke record for the running transaction.
- `jbd2_journal_cancel_revoke(handle, jh)` cancels a pending revoke when a buffer gets journal write access.
- `jbd2_clear_buffer_revoked_flags()` clears buffer flags at transaction boundaries.
- `jbd2_journal_switch_revoke_table()` swaps running and committing revoke tables.
- `jbd2_journal_write_revoke_records()` writes all committing revoke records into journal revoke descriptor blocks.
- `write_one_revoke_record()` and `flush_descriptor()` format revoke blocks, including 64-bit block numbers and descriptor checksums.

Recovery revoke path:
- `jbd2_journal_set_revoke(journal, blocknr, sequence)` records the latest revoke transaction for a block.
- `jbd2_journal_test_revoke(journal, blocknr, sequence)` decides whether a log block should be skipped during replay.
- `jbd2_journal_clear_revoke(journal)` empties the table after recovery.

Integration points:
- Used by `recovery.c` during revoke scan and replay.
- Uses JBD2 transaction, buffer-head, list, spinlock, slab, hash, and checksum infrastructure.
- Userland e2fsprogs builds share the recovery-facing code through `jfs_user.h`.

Risk notes:
- The running revoke table is protected by `j_revoke_lock`; committing and recovery tables rely on single-threaded access by design.
- `handle->h_revoke_credits` exhaustion is treated as IO failure.
- Multiple revoke records for the same block retain only the newest transaction sequence.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/revoke.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/scantest.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/scantest.c

This is a standalone inode-scan performance test program, not part of normal e2fsck pass logic.

Behavior:
- Opens a hardcoded device path `/dev/hda3` with `ext2fs_open()`.
- Opens an inode scan with `ext2fs_open_inode_scan()`.
- Iterates all inodes with `ext2fs_get_next_inode()`.
- Prints `i_blocks` for inodes whose `i_links_count` is nonzero.
- Closes the filesystem and prints resource usage.

Local resource tracking:
- Defines a small `struct resource_track` with wall/user/system start times and initial program break.
- `init_resource_track()` captures starting memory and rusage.
- `timeval_subtract()` computes elapsed seconds.
- `print_resource_track()` prints memory delta and elapsed/user/system time.

Integration points:
- Uses libext2fs directly, plus `com_err` for error reporting.
- Includes e2fsprogs version and ext2fs headers.
- Uses `_()` translation macro in printf/com_err messages.

Risk notes:
- The device path is hardcoded and obsolete; running it unmodified is environment-specific.
- It exits immediately on any libext2fs open/scan/read error.
- It is useful as a benchmark/dev utility rather than production fsck logic.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/scantest.c -->