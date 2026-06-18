# Group Research: group_208_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_data_checksum_c_sour_196031f63445

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/bcachefs`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.c

Implements checksum, MAC, encryption, and encryption-key setup for bcachefs data and metadata paths. It abstracts checksum state across CRC32C, CRC64, xxhash, and ChaCha20-Poly1305 MAC modes, with bio variants that walk `bio_vec`s safely under highmem.

Key entry points:
- `bch2_checksum()` and `bch2_checksum_bio()` compute checksums/MACs over memory or bios.
- `bch2_encrypt()` and `__bch2_encrypt_bio()` apply ChaCha20 encryption when the checksum type is encryption-backed.
- `bch2_rechecksum_bio()` recomputes split extent CRCs after extent splitting, verifying the old checksum first.
- `bch2_fs_encryption_init()` decrypts/stores the filesystem ChaCha20 key from the superblock crypt field.

Important details:
- Poly1305 keys are derived with ChaCha20 from the fs key and nonce, with `BCH_NONCE_POLY` separation.
- Bio encryption requires segment lengths aligned to `CHACHA_BLOCK_SIZE` except final-call semantics are avoided by rejecting unaligned segments.
- Mergeable checksums are recomputed over zero pages then XORed with the second checksum, used only for selected non-encryption checksum types.
- Userspace builds include keyutils/passphrase paths; kernel builds request `user` keys from the kernel keyring.

Dependencies and interactions:
- Uses nonce helpers and checksum type policy from `checksum.h`.
- Consumes extent CRC metadata and `extent_nonce()`.
- Writes superblock crypt field text/validation through `bch_sb_field_ops_crypt`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.h

Declares checksum/encryption APIs and inline policy helpers for data, metadata, and extent nonce construction.

Key contents:
- Mergeability predicate for `none`, `crc32c`, and `crc64`.
- Nonce domain constants for extents, btree, journal, prio, and Poly1305.
- Option-to-checksum mapping helpers for metadata/data checksum choices.
- `extent_nonce()` constructs per-extent nonces from bversion, compression state, size, and CRC nonce.

Important invariants:
- Encryption checksum types require `c->chacha20_key_set`.
- `bch2_crc_cmp()` returns true on mismatch and is intended to avoid early-exit comparison.
- `nonce_add()` advances by ChaCha blocks and asserts block alignment.
- NOCOW data returns checksum type `0`, while encrypted filesystems force ChaCha20-Poly1305 data MACs.

Dependencies and interactions:
- Used by compression, extents, EC IO, and read/write paths for checksum selection, formatting, and nonce handling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.c

Implements data compression/decompression for extents, plus compression option parsing and workspace initialization. Supported algorithms are lz4, gzip, and zstd, with incompressible tagging.

Key entry points:
- `bch2_bio_compress()` maps or bounces source/destination bios, compresses, and returns on-disk compression type.
- `bch2_bio_uncompress()` and `bch2_bio_uncompress_inplace()` decompress encoded extents into target bios.
- `bch2_fs_compress_init()` and `bch2_fs_compress_exit()` manage bounce/workspace mempools.
- `bch2_opt_compression_parse()` parses `type[:level]` option strings.

Important details:
- `bio_map_or_bounce()` prefers direct contiguous mapping, then vmap, then bounce buffers.
- Zstd stores exact compressed length in the first 4 bytes because sector padding cannot be passed to the zstd decompressor.
- Compression retries with smaller source sizes when output does not fit, aligned to filesystem block size.
- Optional `verify_compress` immediately decompresses and compares output for debugging.
- Superblock compression feature bits are lazily set when compressed data is encountered or configured.

Dependencies and interactions:
- Uses checksum/extent CRC fields to describe encoded extents.
- Uses filesystem `encoded_extent_max`, block size, and compression feature flags.
- On missing workspace for an on-disk compression type, may invoke fsck-style repair to mark the feature in the superblock.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.h

Public compression API and compact compression-option encoding.

Key contents:
- `union bch_compression_opt` packs type and level into one byte using endian-aware bitfields.
- Validation rejects unknown types and nonzero level for `none`.
- Declares bio compression/decompression, compression feature initialization, option parse/to-text/validate helpers.
- Defines `bch2_opt_compression` as the option-function descriptor.

Dependencies and interactions:
- Maps user-facing compression options to on-disk compression types.
- Included by extent/write paths that need compression choice or encoded extent decoding.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/compress_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/compress_types.h

Defines the filesystem compression runtime state.

Key contents:
- `struct bch_fs_compress` contains read/write bounce mempools.
- Per-compression-option workspace mempools are indexed by `BCH_COMPRESSION_OPT_NR`.
- Stores computed zstd compression workspace size.

Dependencies and interactions:
- Embedded in `struct bch_fs`.
- Initialized and torn down by `compress.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/compress_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.c

Implements copy garbage collection: selecting fragmented buckets or stripes, evacuating live data, and pacing the background copygc thread.

Key entry points:
- `bch2_copygc()` selects work from fragmentation LRUs and calls `bch2_evacuate_bucket()`.
- `bch2_copygc_wait_amount()` and `bch2_copygc_dev_wait_amount()` compute how long copygc can sleep based on free/fragmented space.
- `bch2_copygc_thread()` runs the kthread loop with freezer support, io-clock waits, wakeups, and shutdown handling.
- `bch2_copygc_start()`, `bch2_copygc_stop()`, and fs init/exit manage thread/workqueue lifecycle.

Important details:
- Tracks buckets in flight with an rhashtable and FIFO list to avoid duplicate evacuation and to bound outstanding work.
- Bucket movability checks device RW/online state, open bucket status, backpointer mismatch bitmap, alloc state, and LRU race conditions.
- EC-aware copygc can prefer stripe fragmentation LRU when stripe fragmentation is significantly worse than normal bucket fragmentation.
- Uses `BCH_WATERMARK_copygc` for relocation writes.
- Emits trace events with sectors seen/moved and bucket counts.

Dependencies and interactions:
- Depends on alloc LRUs, backpointers, move/evacuate infrastructure, EC trigger helpers, io clocks, and write buffer flushing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.h

Public interface for copygc state reporting, wakeup, lifecycle, and progress heuristics.

Key contents:
- Declares wait/progress calculations and wait-state text formatter.
- `bch2_copygc_wakeup()` increments `kick_count` and wakes the copygc thread under RCU.
- Declares start/stop and fs init/exit hooks.

Dependencies and interactions:
- Used by allocator paths to wake copygc when allocation is blocked or fragmentation requires progress.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc_types.h

Defines persistent in-memory copygc state in `struct bch_fs_copygc`.

Key fields:
- RCU-protected copygc kthread pointer.
- Dedicated `write_point` for relocation writes.
- Wait accounting (`wait_at`, `wait`), running flag, run count, kick count.
- Waitqueue for observers waiting on running state.
- Dedicated workqueue for btree updates.

Dependencies and interactions:
- Embedded in `struct bch_fs`; initialized by `bch2_fs_copygc_init()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.c

Implements erasure-coded stripe creation, reuse, widening support, and repair/resilver stripe replacement.

Key entry points:
- `bch2_ec_stripe_head_get()` exposes stripe-head allocation to the sector allocator.
- `bch2_ec_stripe_create_start()` queues completed stripe creation work.
- `bch2_resume_logged_op_stripe_update()` resumes interrupted extent updates after a logged stripe update op.
- `bch2_stripe_repair()` creates replacement stripes for degraded stripes.

Important details:
- Stripe creation allocates data/parity buckets, fills data buffers, generates Reed-Solomon parity/checksums, writes parity/moved blocks, inserts the stripe key, and updates all extents pointing to stripe blocks.
- Extent updates walk backpointers for old buckets, replace direct pointers with new stripe pointers, drop stale EC pointers, and commit with disk reservations.
- Logged operation records old/new stripe indexes and old block map so crash recovery can complete extent updates.
- Stripe reuse selects reusable fragmented stripes from the stripe fragmentation LRU, can retain live data blocks, and allocates only missing/new blocks.
- `can_widen` is computed from RW member sets so stripes can later be reused at wider geometry.
- Device write refs protect devices during stripe creation and repair.

Dependencies and interactions:
- Uses allocation stripe state, open buckets, disk labels/targets, EC IO buffers, EC triggers, backpointers, logged ops, move/copygc contexts, and reconcile marking.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.h

Declares stripe-creation state machines and allocator-facing EC interfaces.

Key contents:
- `struct ec_dev_stripe_state` tracks per-disk-label allocation striping state for data and parity buckets.
- `struct ec_stripe_new` represents an in-progress stripe, including refs, allocated buckets, old/new stripe buffers, block maps, and repair/move context.
- `struct ec_stripe_head` groups in-progress stripe creation by disk label, algorithm, redundancy, and watermark.
- Inline ref handling starts stripe creation when IO refs drain and frees when stripe refs drain.
- Iteration macros define data, parity, and combined block ranges.

Dependencies and interactions:
- Shared by allocator/write path, EC create worker, copygc/repair, and trigger/open-stripe tracking.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/format.h

Defines the on-disk `struct bch_stripe` format.

Key fields:
- Stripe sectors, algorithm, `needs_reconcile`, `can_widen`, block count, redundancy count.
- Checksum granularity and checksum type.
- `disk_label` for target grouping.
- Flexible array of extent pointers followed by variable-length checksums and per-block sector counts.

Important details:
- `can_widen` is a 3-bit saturating value.
- Comments note a format limitation: checksum size is implicit, making blockcount access dependent on known checksum type.
- Format is packed and 8-byte aligned.

Dependencies and interactions:
- Accessor layout helpers live in `trigger.h`.
- Used by EC create, IO, trigger, fsck/check, and read reconstruction.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.c

Handles EC startup/shutdown, device removal invalidation, stripe flushing, and stripe-reference consistency checks.

Key entry points:
- `bch2_invalidate_stripe_to_dev()` marks a removed device pointer invalid in stripe keys and adjusts replica accounting.
- `bch2_dev_remove_stripes()` walks bucket-to-stripe refs for a device.
- `bch2_fs_ec_stop()` and `bch2_ec_stop_dev()` cancel in-flight stripes.
- `bch2_fs_ec_flush()` and `bch2_fs_ec_flush_outstanding()` wait for committed/in-flight stripe work.
- `bch2_check_stripe_refs()` repairs/checks stripes-to-buckets and bucket-to-stripe references.

Important details:
- Device invalidation refuses operations that would degrade or lose data unless force flags allow it.
- Teardown frees stripe heads, dev stripe state, workqueue, and EC bioset, asserting no pending stripe_new entries.
- Flush-outstanding waits only for stripe_new entries that already reached commit-ready sequence numbers.
- Reference checking repairs missing `bucket_to_stripe` bits and removes refs to missing or mismatched stripes.

Dependencies and interactions:
- Works with alloc accounting, LRU, replicas, write buffer, EC create/trigger helpers, and reconcile triggers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.h

Public EC lifecycle and consistency API.

Key contents:
- Device stripe invalidation/removal declarations.
- EC stop/flush/flush-outstanding lifecycle declarations.
- Startup/shutdown hooks and `bch2_stripes_read()`.
- Bucket stripe-count and stripe-reference check declarations.

Dependencies and interactions:
- Included by device removal, fs init/exit, fsck/recovery, and EC trigger paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.c

Implements EC stripe buffer allocation, parity generation/recovery, checksum validation, block IO, and reconstruct-read path.

Key entry points:
- `bch2_ec_stripe_buf_init()` and `bch2_ec_stripe_buf_exit()` manage per-stripe block buffers under a memory limit.
- `bch2_ec_generate_ec()` and `bch2_ec_generate_checksums()` compute parity and per-block checksums.
- `bch2_stripe_buf_validate_msg()` validates checksums and reports recoverability.
- `bch2_ec_block_io_range()` submits EC block read/write bios.
- `bch2_ec_read_extent()` reconstructs a failed EC-backed extent read.

Important details:
- Kernel builds use RAID5/RAID6 xor/pq helpers; non-kernel builds include userspace RAID helpers.
- Buffer ranges are rounded to checksum granularity.
- Validation records pre- and post-recovery per-block errors; checksum failures update device IO error accounting.
- Reconstruction requires failures not exceed redundancy and validates recovered data checksums.
- Read reconstruction checks stale stripe pointers while btree locks are still held, then releases locks before allocation/IO.

Dependencies and interactions:
- Uses checksum helpers, EC trigger stripe layout accessors, read path structs, device io refs, bioset from EC init.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.h

Declares EC IO structures and APIs.

Key contents:
- `struct ec_bio` wraps a bio with device, stripe buffer, block index, direction, and submit time.
- `struct ec_stripe_buf` stores stripe key, data buffers, errors, stale bitmap, checksum diagnostics, and IO closure.
- `ec_nr_failed()` counts block failures for pre/post recovery phases.
- Declares stripe buffer lifecycle, EC generation/checksum APIs, block IO, stripe read, and reconstruct extent read.

Dependencies and interactions:
- Included by EC create, repair, and read paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.c

Implements stripe bkey validation/text formatting, transactional/GC triggers, stripe bucket accounting, open-stripe tracking, and new-stripe bucket tracking.

Key entry points:
- `bch2_stripe_validate()` validates stripe bkey positions, value size, checksum granularity, sectors, and pointers.
- `bch2_stripe_to_text()` prints stripe geometry, label, flags, pointers, and block counts.
- `bch2_trigger_stripe()` updates LRU entries, reconcile bits/accounting, replica accounting, bucket refs, and GC stripe state.
- `bch2_ec_stripe_mem_alloc()` allocates GC stripe memory when needed.
- `bch2_stripe_handle_tryget()` / `put()` track open stripes to prevent deletion races.

Important details:
- Parity bucket marking asserts parity buckets do not already contain data and keeps dirty sectors/stripe refcount consistent.
- Transactional triggers maintain `bucket_to_stripe` btree bits and bucket backpointers.
- Empty stripes are converted to deleted keys when not open, or queued for delete work.
- `can_widen` is refreshed transactionally from current RW-member device counts.
- Hash tables track buckets participating in new stripes to avoid rebalance races.

Dependencies and interactions:
- Works with alloc accounting, LRU, replicas, backpointers, reconcile work, EC create/init structures, and recovery/fsck passes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.h

Public EC stripe bkey operations and inline stripe layout helpers.

Key contents:
- `bch2_bkey_ops_stripe` binds validate, text, swab, trigger, and min value size.
- Helpers compute checksum count, checksum offsets, blockcount offsets, value size, checksum get/set.
- `stripe_widen_target_nr_data()` and `stripe_widen_value()` compute widening capacity.
- `stripe_lru_pos()` scores empty/reusable stripes for deletion or reuse.
- Pointer-match helpers compare extent pointers to stripe blocks.
- GC stripe lock helpers and declarations for open-stripe/new-bucket hash operations.

Dependencies and interactions:
- Used throughout EC create, IO, init, trigger, copygc, and extents logic.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/types.h

Defines EC runtime and GC data structures.

Key contents:
- `struct stripe` is a compact in-memory stripe summary for heap/scan use.
- `struct gc_stripe` stores GC-time stripe state, block sector counts, pointers, and replicas entry.
- `struct bch_fs_ec` holds stripe buffer accounting, open-stripe/new-bucket hash tables, stripe heads, dev stripe state, pending stripe list/waitqueue/sequence, create workqueue, stripe hint/delete work, EC bioset, and GC stripe genradix.

Dependencies and interactions:
- Embedded in `struct bch_fs`.
- Fields are initialized by EC init and mutated by create/trigger/IO paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.c

Implements trimming of large extent updates so atomic btree transactions do not require too many alloc/EC iterators.

Key entry point:
- `bch2_extent_trim_atomic()` scans overlapping keys and cuts back an insert if the estimated iterator count would exceed `EXTENT_ITERS_MAX`.

Important details:
- Counts alloc and EC btree iterator needs from extent pointer entries, cached-pointer LRU updates, and reflink indirections.
- Handles whiteouts with type-aware filtering while still supplying max keys needed by snapshot ancestry assertions.
- For reflink pointers, walks the reflink btree to account for referenced extents and their alloc pointer updates.
- Emits an `extent_trim_atomic` trace event when trimming occurs.

Dependencies and interactions:
- Uses extent pointer decoding helpers from `extents.h`, btree iter/update APIs, and interior btree logic.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.h

Small public header for atomic extent update trimming.

Key contents:
- Declares `bch2_extent_trim_atomic()`.

Dependencies and interactions:
- Included by extent update/write paths that need to bound transaction iterator pressure before inserting extents.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.c

Core extent and pointer utility implementation: read-device selection, btree pointer validation, extent merging, CRC packing, pointer mutation, durability accounting, cached pointer cleanup, validation, text formatting, endian swabbing, extent flags, and key cutting.

Key entry points and areas:
- Read selection: `bch2_bkey_pick_read_device()` chooses a readable pointer considering failed devices, checksum retries, EC reconstruction, preferred device flags, device latency, and forced debug modes.
- Validation/text: `bch2_bkey_ptrs_validate()`, `bch2_btree_ptr_validate()`, `bch2_btree_ptr_v2_validate()`, and text helpers validate/format pointers, CRCs, EC entries, reconcile entries, and btree pointers.
- Merge/cut: `bch2_extent_merge()`, `bch2_reservation_merge()`, `bch2_cut_front_s()`, and `bch2_cut_back_s()` combine or trim keys while preserving pointer/CRC semantics.
- CRC helpers: `bch2_extent_crc_append()`, `bch2_bkey_narrow_crc()`, and packing helpers select crc32/crc64/crc128 entry formats based on checksum width, size, and nonce.
- Pointer mutation: drop pointer/device/EC helpers, append decoded pointers, cached pointer marking, stale cached pointer dropping, extra durability dropping.
- Accounting: dirty pointer counts, allocated pointer counts, compressed sectors, incompressible propagation, replica/durability calculations, readability tests.

Important invariants:
- Direct extents cannot contain duplicate device pointers, mixed written/unwritten pointers, redundant CRC/stripe entries, cached+EC pointers, or all-invalid dirty pointer sets at commit.
- Pointer validation checks device existence when possible, bucket bounds, and that pointers do not span buckets.
- Extent merge refuses to cross buckets, merge incompatible compression/nonce/EC metadata, or exceed encoded extent size/CRC field limits.
- Cached pointers are limited to one suitable non-stale pointer and are incompatible with EC.
- EC durability may be reduced by dropping EC metadata only when online durability remains sufficient.

Dependencies and interactions:
- Central dependency for read/write, compression, checksum, EC, reconcile, allocator accounting, fsck validation, btree pointer handling, and debug trace output.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/data/extents.c -->