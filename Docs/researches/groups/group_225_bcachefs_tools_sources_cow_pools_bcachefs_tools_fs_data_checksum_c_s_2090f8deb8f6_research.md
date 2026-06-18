# Group Research: bcachefs-tools fs/data integrity, compression, copygc, EC, and extents

Scope: `Docs/research_subset_a.md` source tree `sources/cow-pools/bcachefs-tools`.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/checksum.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/checksum.c

Implements checksum, authenticated checksum, encryption, and filesystem encryption-key setup for bcachefs data paths.

Key responsibilities:
- Maintains `bch2_checksum_state`, abstracting mergeable CRC-style checksums and stateful `xxhash`.
- Implements `bch2_checksum()` for `none`, `crc32c`, `crc64`, `xxhash`, and Chacha20-Poly1305 MAC variants.
- Implements `bch2_checksum_bio()` and `__bch2_checksum_bio()` over bio segments, including highmem-safe mapping.
- Implements `bch2_encrypt()` and `__bch2_encrypt_bio()` using Chacha20, with explicit checks that the fs encryption key is loaded.
- Implements `bch2_checksum_merge()` for mergeable checksum types by advancing the left checksum over zero bytes and XORing with the right checksum.
- Implements `bch2_rechecksum_bio()` for splitting/recomputing extent CRC metadata while verifying against the old checksum.
- Defines superblock crypt-field validation/text output via `bch_sb_field_ops_crypt`.
- Handles kernel/user key lookup, passphrase fallback in userspace, key revocation in userspace, and superblock-key decryption.
- Initializes and clears `c->chacha20_key`.

Important interactions:
- Uses nonce helpers from `checksum.h`, extent CRC metadata, bio iteration, kernel keyring or userspace keyutils, and superblock crypt fields.
- Encryption checksum types are both encryption and authentication-sensitive; missing keys become filesystem inconsistency/error paths.
- `bch2_rechecksum_bio()` depends on consistent encrypted-vs-unencrypted checksum type transitions.

Notable concerns:
- `bch2_crc_cmp()` is used through the header as non-equality; comments note constant-time comparison is not guaranteed.
- Bio encryption requires every non-final segment length to be Chacha block aligned; misalignment returns `-EIO`.
- Disabled `#if 0` code documents planned runtime encryption enable/disable paths but is not active.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/checksum.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/checksum.h

Declares checksum/encryption interfaces and defines checksum option, nonce, and checksum utility helpers.

Key responsibilities:
- Defines mergeable checksum types: `none`, `crc32c`, and `crc64`.
- Defines nonce domain constants for extents, btree, journal, priority data, and Poly1305.
- Declares checksum, encryption, key request/revoke, bio checksum/encryption, rechecksum, and encryption init/exit APIs.
- Provides `bch2_csum_opt_to_type()`, `bch2_data_checksum_type()`, `bch2_data_checksum_type_rb()`, and `bch2_meta_checksum_type()`.
- Validates checksum type/key availability with `bch2_checksum_type_valid()`.
- Provides nonce helpers: `nonce_add()`, `null_nonce()`, `extent_nonce()`, `__bch2_sb_key_nonce()`, and `bch2_sb_key_nonce()`.
- Provides text formatting helpers for checksums and checksum errors.
- Provides `bch2_key_is_encrypted()` for encrypted superblock-key detection.

Important interactions:
- Data checksum selection is disabled for `nocow`; encryption overrides configured checksum with Chacha20-Poly1305 MACs.
- Metadata under encryption always uses 128-bit Chacha20-Poly1305.
- `extent_nonce()` encodes version, compressed size/type, extent domain, and sector offset into the nonce.

Notable concerns:
- `nonce_add()` asserts Chacha block-size alignment.
- `bch2_crc_cmp()` is logically “not equal” and is intentionally simple, with a comment noting constant-time concerns.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/checksum.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/compress.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/compress.c

Implements extent-level compression/decompression for lz4, gzip, and zstd, plus compression option parsing and workspace initialization.

Key responsibilities:
- Documents compression behavior: per-file/per-directory, extent granularity up to encoded extent max, random-read tradeoffs, and background recompression.
- Implements bounce-buffer handling for bio memory that may be non-contiguous or highmem-backed.
- Implements `buf_uncompress()` for lz4, gzip, and zstd, including workspace-pool lookup and superblock feature repair paths.
- Implements `bch2_bio_uncompress_inplace()` and `bch2_bio_uncompress()` to decompress into bios and normalize extent CRC metadata after in-place decompression.
- Implements `attempt_compress()` and `bch2_compress()` for lz4/lz4hc, gzip, and zstd.
- Pads compressed output to block size and marks data incompressible when compression does not shrink enough.
- Optional `verify_compress` immediately decompresses and compares compressed output.
- Tracks compression feature bits and lazily initializes missing compression workspaces if fsck allows repairing the superblock feature set.
- Initializes/exits compression workspace and bounce mempools.
- Parses and formats compression options in `type[:level]` form with levels up to 15.

Important interactions:
- Uses `bch2_check_set_has_compressed_data()` to set compression feature bits in the superblock and allocate workspace pools.
- Compression is limited by `c->opts.encoded_extent_max`.
- zstd stores the exact compressed byte length in the first 4 bytes because sector-rounded compressed size is insufficient for decompression.

Notable concerns:
- zstd compression subtracts a 7-byte “fudge factor” for a noted zstd overrun behavior.
- If compression workspace is not initialized and fsck repair is declined, compression/decompression returns bcachefs-specific errors.
- `bch2_bio_uncompress_inplace()` assumes caller allocated enough bio vectors; comment notes the assertion is indirect.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/compress.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/compress.h

Public interface and packed option representation for compression.

Key responsibilities:
- Maps compression option enum values to on-disk compression types.
- Defines `union bch_compression_opt` as an 8-bit value split into 4-bit type and 4-bit level, endian-aware.
- Validates compression options, rejecting nonzero level with `none`.
- Declares bio compression/decompression APIs, workspace init/exit, feature-setting helper, and option parse/format/validate APIs.
- Defines `bch2_opt_compression` option function table.

Important interactions:
- The 4-bit level field matches the `0..15` parser limit in `compress.c`.
- Compression option-to-type mapping feeds checksum/extent metadata and compression workspaces.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/compress_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/compress_types.h

Defines per-filesystem compression state.

Key responsibilities:
- `struct bch_fs_compress` stores read/write bounce mempools, per-compression-option workspace mempools, and cached zstd workspace size.

Important interactions:
- Allocated and released by `bch2_fs_compress_init()` / `bch2_fs_compress_exit()` in `compress.c`.
- Used by compression and decompression paths to avoid blocking allocations in data I/O paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/compress_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/copygc.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/copygc.c

Implements copy-on-write garbage collection: relocating live data out of fragmented buckets/stripes so buckets can be reused.

Key responsibilities:
- Documents copygc behavior, reserve pressure, and fragmentation LRU usage.
- Tracks buckets in flight with an rhashtable, FIFO list, sector counts, and evacuation array.
- Determines whether a bucket is movable by checking device state, open-bucket status, backpointer mismatch state, alloc metadata, generation, and LRU race.
- Selects normal fragmented buckets from `BTREE_ID_lru` / `BCH_LRU_BUCKET_FRAGMENTATION`.
- Selects stripe buckets from stripe-fragmentation LRU when EC stripe fragmentation is more urgent.
- `should_do_ec_copygc()` compares stripe and bucket fragmentation ratios.
- `bch2_copygc()` flushes write buffers, selects candidates, evacuates buckets via `bch2_evacuate_bucket()`, tracks move stats, and frees temporary state.
- Computes per-device and whole-fs wait amounts based on free space and fragmented movable data.
- Provides diagnostic text including wait state and copygc task backtrace.
- Runs a freezable kernel thread that waits on io-clock thresholds, copygc enable state, kicks, and allocator pressure.
- Starts/stops copygc thread and workqueue; initializes waitqueue/running state.

Important interactions:
- Depends on allocation LRUs, backpointers, moving context, EC trigger helpers, allocator watermarks, and io-clock waiting.
- `bch2_copygc_can_make_progress()` uses hysteresis tuned to avoid allocator hangs just below reserve thresholds.
- Copygc wakeups increment `kick_count` in `copygc.h`.

Notable concerns:
- Copygc avoids devices not RW/online and buckets still open for writes.
- EC-aware copygc may evacuate stripe data blocks, not only standalone buckets.
- Near-full filesystems can see write latency increase while copygc frees space.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/copygc.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/copygc.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/copygc.h

Declares copygc control, diagnostics, and wakeup APIs.

Key responsibilities:
- Declares wait amount helpers, diagnostic text output, progress predicate, start/stop, and fs init/exit functions.
- Defines `bch2_copygc_wakeup()` to increment `kick_count` and wake the copygc thread under RCU.

Important interactions:
- Used by allocator paths and EC creation/allocation paths to avoid waiting forever when copygc can free fragmented space.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/copygc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/copygc_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/copygc_types.h

Defines per-filesystem copygc state.

Key responsibilities:
- `struct bch_fs_copygc` tracks the copygc thread, write point, wait timing, running flag, run/kick counters, running waitqueue, and dedicated workqueue.

Important interactions:
- Populated by `copygc.c` and embedded in `struct bch_fs`.
- `write_point` is passed into moving context so copygc relocations use a dedicated writepoint.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/copygc_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/create.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/create.c

Implements background erasure-code stripe creation, reuse, widening, extent-pointer updates, and degraded-stripe repair.

Key responsibilities:
- Documents EC model: foreground writes replicated normally, background work groups immutable buckets into stripes, writes parity, and atomically updates extent pointers.
- Maintains per-disk-label `ec_dev_stripe_state` for allocator striping state.
- Deletes empty stripes via stripe-fragmentation LRU and `stripe_delete_work`.
- Creates stripe keys with reconcile marking and insertion into `BTREE_ID_stripes`.
- Updates extents pointing to old data buckets:
  - Finds backpointers.
  - Verifies pointer/stripe match.
  - Drops stale stripe pointers.
  - Rewrites the data pointer to the new stripe block.
  - Inserts the new stripe pointer.
  - Drops excess replicas while preserving target durability.
  - Commits changes under no-ENOSPC/no-check-RW flags.
- Uses logged operation `logged_op_stripe_update` so extent updates can resume after interruption.
- Finalizes stripe creation by validating old stripe data, reusing old blocks if applicable, generating parity/checksums, writing moved data/parity blocks, committing stripe key/logged op, then updating extents.
- Holds device write iorefs while committing stripes to avoid racing device removal.
- Allocates EC devices by disk label/target, bucket size, durability, and active RW devices.
- Computes and caches stripe widening eligibility (`can_widen`) from RW member counts.
- Allocates new stripe structures and bucket sets, including parity/data bucket allocation and shrink/fallback behavior when allocation is blocked.
- Reuses old fragmented stripes when full-stripe allocation is unavailable.
- Manages stripe indices, open stripe handles, pending creation lists, and stripe heads keyed by disk label/algo/redundancy/watermark.
- Provides `bch2_ec_stripe_head_get()` for allocator integration.
- Repairs degraded stripes by evacuating blocks if necessary or creating a replacement stripe, reading old data, allocating new buckets, and queueing creation.

Important interactions:
- Central to EC write integration with allocator, copygc, moving context, btree logged ops, backpointers, reconcile state, and EC I/O.
- Uses `bch2_ec_generate_ec()`, `bch2_ec_generate_checksums()`, `bch2_ec_block_io()`, and `bch2_stripe_buf_read()` from `io.c`.
- Uses trigger-side open-stripe/bucket tracking to prevent deletion/rebalance races.
- Uses `bch2_bkey_set_needs_reconcile()` to keep reconcile subsystem aware of stripe and extent changes.

Notable concerns:
- Stripe creation carefully handles device removal races; stale copied pointers to removing devices are rejected before commit.
- Reuse path cannot yet repair invalid blocks directly during reuse; comments note needed backpointer-update codepath.
- If insufficient devices remain, allocator is expected to fall back to replication.
- Stripe index allocation scans slots and has a comment noting need for a future free-stripe bitrange btree.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/create.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/create.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/create.h

Defines EC stripe creation state structures, helpers, and public interfaces.

Key responsibilities:
- Defines `ec_dev_stripe_state`, `ec_stripe_new_bucket`, `ec_stripe_handle`, `ec_stripe_new`, and `ec_stripe_head`.
- Defines `STRIPE_REF_io` and `STRIPE_REF_stripe` reference classes.
- Provides helpers for data/parity block counts and iteration ranges.
- Declares EC device selection, stripe formability, widening cache, stripe cancellation, bucket cancellation, stripe-head get/put, stripe create/delete, stripe repair, diagnostics, and logged-op resume APIs.
- Implements `ec_stripe_new_get()` / `ec_stripe_new_put()`.
- On final IO ref drop, assigns a monotonic `seq`, wakes flush waiters, and starts stripe creation work.
- Provides bkey ops for logged stripe-update operations.

Important interactions:
- `ec_stripe_new` ties together allocation state, old/new stripe buffers, open stripe handles, block maps, disk reservation, and moving context.
- `ec_stripe_head` is the allocator-facing staging object for each disk-label/algorithm/redundancy/watermark tuple.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/create.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/format.h

Defines the on-disk stripe value layout.

Key responsibilities:
- Defines packed `struct bch_stripe` with:
  - stripe sector count,
  - algorithm,
  - `needs_reconcile`,
  - 3-bit saturating `can_widen`,
  - block and redundancy counts,
  - checksum granularity/type,
  - disk label,
  - variable-length extent pointer array.
- Documents variable-length sections after pointers: per-block checksums and per-block sector counts.

Important interactions:
- `trigger.h` computes offsets into the variable-length checksum and block-count sections.
- `create.c` initializes geometry and `can_widen`.
- `io.c` uses checksum fields for per-block validation/recovery.

Notable concerns:
- Comment notes target IDs should eventually be 16-bit; current `disk_label` is 8-bit.
- Comment notes checksum layout makes block sector counts inaccessible if checksum type is unknown.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/init.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/init.c

Implements EC startup/shutdown, device-removal invalidation, flush/wait logic, and stripe-reference fsck checks.

Key responsibilities:
- `bch2_invalidate_stripe_to_dev()` invalidates stripe pointers to a removed device, marks stripe `needs_reconcile`, updates disk accounting before/after mutation, and checks force flags for degraded/lost data.
- Skips open stripes during device removal because EC creation owns their migration; callers flush outstanding creates and retry.
- `bch2_dev_remove_stripes()` scans `bucket_to_stripe` refs for a device and invalidates referenced stripes, retrying open-stripe cases up to a fixed iteration limit.
- Stops EC creation globally or per device by canceling in-progress stripe heads that reference the stopped device.
- Flushes all pending stripes or only those commit-ready at call time using `stripe_new_seq`.
- Initializes and exits EC locks, lists, waitqueues, stripe delete work, stripe create workqueue, and block bioset.
- Checks and repairs stripe reference consistency:
  - Ensures stripe fragmentation LRU entries exist.
  - Ensures each stripe block has `bucket_to_stripe` refs.
  - Ensures each `bucket_to_stripe` ref points to an existing matching stripe.
  - Updates alloc stripe refcounts via `bucket_stripe_ref_mod()`.
- Provides `bch2_bucket_nr_stripes()`.

Important interactions:
- Works closely with EC create/open-stripe tracking to avoid invalidating stripes mid-creation.
- Uses allocation accounting, LRUs, btree bitsets, write-buffer flush coordination, and fsck repair paths.

Notable concerns:
- `bch2_stripes_read()` is currently a stub returning 0.
- Device-removal retry has a finite 10-iteration guard and reports `remove_stripes_did_not_terminate` if open stripes persist.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/init.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/init.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/init.h

Declares EC init/shutdown, device removal, flush, and stripe-reference check APIs.

Key responsibilities:
- Exposes stripe invalidation, device stripe removal, per-device/global EC stop, full/outstanding flush, stripe read initialization, fs init/exit, bucket stripe count, and stripe reference check functions.

Important interactions:
- Used by device removal, recovery/fsck, and filesystem lifecycle code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/init.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/io.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/io.c

Implements EC stripe buffer allocation, RAID parity generation/recovery, per-block checksum handling, block I/O, and reconstruct reads.

Key responsibilities:
- Wraps kernel RAID5/6 helpers, including an older-kernel `xor_gen()` shim.
- Implements RAID5/6 parity generation and recovery for up to two failures.
- Allocates bounded stripe buffers with `bch2_ec_stripe_buf_init()`, honoring `ec_stripe_buf_limit` and optional closure wait.
- Releases stripe buffers, memory accounting, and closure state.
- Computes per-block checksums with `bch2_checksum()` and writes them into stripe keys.
- Validates stripe block checksums, records good/bad checksums, and reports device checksum errors.
- Reconstructs failed data blocks if failure count does not exceed redundancy.
- Distinguishes spurious stale-pointer races for unpinned stripes from pinned-stripe allocator inconsistencies.
- Logs detailed pre/post-recovery errors and successful reconstruction messages.
- Issues per-block bio reads/writes with device iorefs, stale pointer detection, per-device IO accounting, and closure completion.
- Implements `bch2_ec_read_extent()`:
  - Relocks transaction to inspect original extent and stripe key.
  - Verifies extent stripe pointer matches stripe key.
  - Checks stale pointers while key is still live/locked.
  - Allocates a partial stripe buffer for the read range.
  - Reads stripe blocks, validates/reconstructs, and copies recovered data into caller bio.

Important interactions:
- Uses checksum helpers, EC trigger layout helpers, read path structures, block bioset from `init.c`, and RAID helpers.
- `create.c` uses the same buffer and parity/checksum routines when creating stripes.

Notable concerns:
- `bch2_ec_read_extent()` has a typo in an error string: “read is biffer than stripe”.
- Recovery returns stale-race-specific errors so the upper read path can retry appropriately.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/io.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/io.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/io.h

Defines EC bio and stripe-buffer state plus EC I/O interfaces.

Key responsibilities:
- Defines `struct ec_bio` wrapper containing device, stripe buffer, block index, direction, submit time, and embedded bio.
- Defines pre/post recovery error slots.
- Defines `struct ec_stripe_buf` with closure, fs pointer, buffered range, per-block errors, data buffers, stale bitmap, checksum diagnostics, and stripe key.
- Provides `ec_nr_failed()` helper.
- Declares stripe buffer init/exit, auto-free cleanup, EC generation/checksum, validation, block I/O, full-stripe read, and reconstruct-read APIs.

Important interactions:
- Shared by EC creation, repair, and read recovery paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/io.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.c

Implements stripe bkey validation/text output, stripe triggers, bucket/accounting updates, open-stripe tracking, and new-stripe bucket tracking.

Key responsibilities:
- Validates stripe key position, value size, checksum granularity, nonzero sector count, and pointer validity.
- Formats stripe keys, including algorithm, sectors, data/redundancy geometry, checksum type/granularity, disk label, `needs_reconcile`, `can_widen`, pointers, and block counts.
- Marks/unmarks stripe buckets:
  - Distinguishes data stripe buckets from parity buckets.
  - Checks parity buckets are not already dirty on insertion.
  - Validates stripe refcount/data type/sector state on deletion.
  - Updates bucket refs, `bucket_to_stripe` btree bit, stripe refcount, alloc data type, and dev counters.
- Maintains stripe backpointers for stripe pointers.
- `bch2_trigger_stripe()`:
  - Schedules stripe delete work for empty stripes.
  - Refreshes `can_widen`.
  - Deletes empty unopened stripes transactionally.
  - Updates stripe fragmentation LRU.
  - Updates reconcile high-priority work bits and reconcile accounting.
  - Updates disk accounting for parity sectors.
  - Updates bucket marks/backpointers.
  - Creates GC stripe mirror state during GC triggers.
- Allocates GC stripe memory.
- Tracks buckets involved in in-flight new stripes to avoid rebalance races.
- Tracks open stripe indices with hash tables so deletion/invalidation can skip stripes being created or rewritten.

Important interactions:
- Hooks into btree update trigger system via `bch2_bkey_ops_stripe` in `trigger.h`.
- Coordinates with `create.c` stripe handles and bucket tracking.
- Coordinates with `init.c` reference checking and device-removal safety.

Notable concerns:
- Contains comments about runtime GC assumptions needing revision if runtime GC returns.
- Correctness depends on trigger flags: transactional vs GC vs atomic paths perform different side effects.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.h

Declares stripe bkey operations and inline helpers for stripe variable layout, LRU scoring, pointer matching, GC stripe locking, and open-stripe tracking.

Key responsibilities:
- Defines `bch2_bkey_ops_stripe` with validate, text, swab, trigger, check/repair, and minimum value size.
- Computes checksums-per-device, checksum offsets, blockcount offsets, stripe value size, checksum get/set.
- Computes widening target and clamped `can_widen` value.
- Defines `STRIPE_LRU_POS_EMPTY` and `stripe_lru_pos()`:
  - Empty stripes get special delete-worker position.
  - Reusable stripes are scored by empty data blocks plus `can_widen`.
- Provides pointer-to-stripe matching helpers for live stripe keys and GC stripe mirrors.
- Provides GC stripe bitlock helpers.
- Declares GC stripe memory allocation, new-stripe bucket lookup/add/delete, open-stripe check, and stripe handle tryget/put.

Important interactions:
- Layout helpers must match `ec/format.h` variable-length `struct bch_stripe`.
- `stripe_lru_pos()` drives both deletion and reuse/copygc prioritization.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/types.h

Defines in-memory EC summary, GC mirror, and per-filesystem EC state.

Key responsibilities:
- Defines compact `struct stripe` summary fields.
- Defines `struct gc_stripe` with lock, alive flag, geometry, block sector counters, pointers, and replica accounting.
- Defines `struct bch_fs_ec` with:
  - stripe buffer memory accounting and waitlist,
  - open stripe/new bucket hash tables,
  - stripe-head and per-device stripe-state lists/locks,
  - pending stripe list/waitqueue/sequence,
  - stripe create workqueue,
  - stripe hint,
  - stripe delete work,
  - EC block bioset,
  - genradix GC stripe storage.

Important interactions:
- Embedded in `struct bch_fs` and initialized by `init.c`.
- Used by create/trigger/io code for all EC lifecycle state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/ec/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extent_update.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extent_update.c

Implements transaction-size guardrails for atomic extent insertion/update.

Key responsibilities:
- Counts how many alloc/EC/LRU/freespace/discard/reflink iterators an extent update may require.
- Handles direct extent/reflink-v keys and reflink-p indirection into the reflink btree.
- Enforces `EXTENT_ITERS_MAX` of 64.
- `bch2_extent_trim_atomic()` scans existing overlapping keys and whiteouts, estimates iterator requirements, and trims the inserted key’s back edge if the update would exceed the iterator limit.
- Emits `extent_trim_atomic` tracepoint when trimming occurs.

Important interactions:
- Prevents large extent updates from exceeding btree transaction iterator capacity.
- Uses extent pointer accounting from `extents.c` and btree update/interior helpers.

Notable concerns:
- Trimming changes the inserted key size, so callers must handle partial progress.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extent_update.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extent_update.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extent_update.h

Declares atomic extent trimming API.

Key responsibilities:
- Exposes `bch2_extent_trim_atomic()` for btree transaction update code.

Important interactions:
- Used where extent insert/update operations need to stay within transaction iterator limits.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extent_update.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents.c

Large extent utility implementation covering read pointer selection, btree pointer validation, extent merging, CRC entry packing, durability, pointer mutation, cached pointer cleanup, formatting, validation, byte-swapping, and key cutting.

Key responsibilities:
- Tracks and formats per-device read failures, including checksum, IO, and EC reconstruction errors.
- Chooses read devices with `bch2_bkey_pick_read_device()`:
  - Ignores stale cached pointers.
  - Honors hard/soft preferred-device flags.
  - Handles missing/offline devices.
  - Selects EC reconstruction when needed.
  - Biases random choice by squared device latency.
  - Returns precise no-device/checksum/io error classes.
- Validates and formats `KEY_TYPE_btree_ptr` and `KEY_TYPE_btree_ptr_v2`, including min-key/version compatibility.
- Merges adjacent extents when pointer order, devices, generations, EC stripe pointers, compression, CRC nonce/type, bucket boundary, and checksum mergeability permit it.
- Validates and merges reservation keys.
- Packs/unpacks and appends CRC entries in crc32/crc64/crc128 forms based on checksum size, extent size, and nonce range.
- Narrows CRC entries when rewriting another replica so remaining replicas point only to live data.
- Computes pointer counts, dirty pointer counts, allocated/fully allocated pointer counts, compressed sectors, incompressible status, replica count, and durability.
- Drops extent entries, pointers, devices, and EC stripe entries with helpers that preserve associated CRC/stripe metadata rules.
- Appends decoded pointers and optional stripe pointers to keys, reusing or appending matching CRC entries.
- Tests for devices/targets/bad devices and pointer/extent equivalence.
- Manages cached pointers:
  - Drops duplicate cached pointers.
  - Rejects cached pointers on EC data.
  - Drops stale/bad/evacuating/wrong-target cached pointers.
  - Converts excess durability to cached pointers or removes pointers entirely.
- Drops extra EC durability while preserving requested replica durability.
- Formats extent pointers, CRCs, and all extent entry types.
- Validates extent pointer entries:
  - Unknown entry types.
  - Btree pointer allowed entry types.
  - duplicate devices.
  - pointer bounds and bucket spanning.
  - checksum and compression type validity.
  - encoded extent size.
  - encrypted nonce consistency.
  - redundant CRC/stripe entries.
  - written/unwritten mixing.
  - missing/all-invalid dirty pointers.
- Swaps extent pointer entries for endian conversion.
- Adds extent flags entry, requesting the incompatible feature first.
- Cuts front/back of keys for extents, reflinks, inline data, and indirect inline data while adjusting sizes, pointer offsets, CRC offsets, reflink indices, and value size.

Important interactions:
- Central dependency for read path, write path, btree validation, EC creation, compression, checksum, reconcile, and device removal.
- Uses checksum mergeability from `checksum.h` and compression metadata from `compress.h`.
- EC pointer semantics interact with `ec/trigger.h` pointer matching and stripe pointer validation.
- Durability helpers account for EC redundancy as pointer durability.

Notable concerns:
- Cached pointers are deliberately incompatible with EC and are dropped.
- Extents may not straddle buckets; merge and validation enforce bucket-boundary constraints.
- Validation distinguishes btree pointers from data extents because dead btree nodes may keep pointer fields without becoming `KEY_TYPE_error`.
- Read selection can force EC reconstruction via static branch for testing/debug behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/data/extents.c -->