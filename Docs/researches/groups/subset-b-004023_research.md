# Research: subset-b-004023

Grouped research for device-mapper files under `sources/distributed-fs/ceph-client/drivers/md`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-crypt.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-crypt.c`

## Purpose

`dm-crypt.c` implements the `crypt` device-mapper target, providing transparent encryption and decryption over a linear backing block-device range. It maps bios to the configured backing device, encrypts writes into cloned output bios, decrypts reads after lower-device completion, supports multiple IV schemes, supports optional authenticated/integrity metadata, handles key loading from hex strings or kernel keyrings, and exposes suspend-time key update/wipe messages.

## Important APIs, Types, and Functions

The core state is `struct crypt_config`: backing `dm_dev`, start sector, cipher/IV configuration, key material, integrity tag parameters, crypto transform arrays, request/page/tag mempools, bioset, IO and crypto workqueues, write-submission kthread, and flags such as `DM_CRYPT_KEY_VALID`, `DM_CRYPT_NO_READ_WORKQUEUE`, and `DM_CRYPT_WRITE_INLINE`. `struct dm_crypt_io` is per-bio state, carrying the base bio, integrity metadata, conversion context, pending counters, saved iterators, error state, and write-ordering tree node. `struct convert_context` tracks multi-sector crypto progress and async restart completion.

`crypt_ctr()` parses `<cipher> <key> <iv_offset> <dev_path> <start> [features]`, allocates all persistent resources, selects workqueue policy, handles zoned-device constraints, configures integrity, and registers per-IO data size. `crypt_map()` is the runtime entry point: it bypasses flush/discard, splits oversized bios where safe, validates sector alignment, allocates per-bio integrity metadata, and queues reads or writes. `crypt_convert()`, `crypt_convert_block_skcipher()`, and `crypt_convert_block_aead()` drive per-sector crypto through the Linux crypto API. Completion and scheduling are split across `crypt_endio()`, `kcryptd_queue_crypt()`, `kcryptd_crypt_read_convert()`, `kcryptd_crypt_write_convert()`, `kcryptd_async_done()`, and the `dmcrypt_write()` kthread.

The IV framework is represented by `struct crypt_iv_operations` and implementations for `plain`, `plain64`, `plain64be`, `essiv`, `benbi`, `null`, `lmk`, `tcw`, `random`, `eboiv`, and `elephant`. Constructor helpers `crypt_ctr_cipher_new()`, `crypt_ctr_cipher_old()`, `crypt_ctr_ivmode()`, `crypt_ctr_auth_cipher()`, and `crypt_ctr_optional()` translate device-mapper table syntax into crypto API transforms and feature flags. Key helpers include `crypt_set_key()`, `crypt_set_keyring_key()`, `crypt_setkey()`, and `crypt_wipe_key()`.

## Control Flow

On table load, optional features are parsed before cipher allocation because integrity and sector-size choices affect transform setup. The constructor allocates crypto transforms, initializes IV handling, decodes or fetches the key, creates request/page/tag mempools, opens the backing device, configures integrity profiles if requested, creates IO and crypto queues, and starts the write-submission thread.

For reads, `crypt_map()` clones and submits the original bio to the backing device through `kcryptd_io_read()`. Lower-device completion calls `crypt_endio()`, which queues decryption. Decryption runs in a safe context, possibly asynchronously through the crypto API, and completes the original bio when all pending sectors have finished. For AEAD read failures, `crypt_dec_pending()` performs a second read into a private buffer for recheck before logging an integrity audit failure.

For writes, `crypt_map()` queues encryption first. `kcryptd_crypt_write_convert()` allocates an output bio, encrypts sector-sized chunks into it, and then submits it directly, through a workqueue, or through `dmcrypt_write()` depending on workqueue flags and ordering requirements. A red-black tree sorted by original sector preserves write-submission ordering for the write thread. Flush and discard are remapped directly because no data conversion is needed.

## State and Persistence Behavior

Persistent on-disk state is the ciphertext and, when configured, lower-device integrity tuples containing AEAD tags or stored IVs. In-memory state includes key bytes, IV private data, transform handles, per-client page budget counters, mempools, and pending IO counters. Key material is treated as sensitive: constructor key strings are zeroed after use, `crypt_wipe_key()` clears validity, overwrites key material, wipes IV private state, and uses `kfree_sensitive()`/`memzero_explicit()` on teardown. `postsuspend`, `preresume`, and `resume` gate key replacement: `crypt_message()` accepts `key set` and `key wipe` only while suspended, and `crypt_preresume()` refuses resume without a valid key.

## Dependencies and Integration Points

The target integrates with device mapper through `struct target_type crypt_target`, providing `.ctr`, `.dtr`, `.map`, `.status`, `.postsuspend`, `.preresume`, `.resume`, `.message`, `.iterate_devices`, `.io_hints`, and optional zoned `.report_zones`. It depends heavily on the kernel crypto API (`skcipher`, `aead`, `authenc`, `ahash`, AES helpers), block integrity APIs, keyrings (`user`, `logon`, `encrypted`, `trusted` when enabled), mempools, biosets, workqueues, kthreads, red-black trees, and `dm-audit`. It advertises `DM_TARGET_ZONED_HM` and `DM_TARGET_ATOMIC_WRITES`, requests zone-append emulation when needed, and tightens queue limits to its encryption sector size and bio-vector constraints.

## Risks and Edge Cases

Correctness depends on strict alignment between bio sectors, configured encryption sector size, lower-device logical block size, and integrity interval size. The async crypto paths are sensitive to pending-count balance, request lifetime, and restart completions. AEAD mode must keep sector number, IV, tag offset, and integrity metadata synchronized, otherwise reads fail with protection errors. Zoned devices require inline write completion and no write workqueue to preserve ordering. Memory pressure is a major risk, mitigated by per-client page budgets and mempools, but the allocation paths are complex. Legacy IV modes (`lmk`, `tcw`, `elephant`) include compatibility-only algorithms with additional key material and sector-size restrictions. A notable implementation signal is the very dense resource unwinding in `crypt_ctr()`/`crypt_dtr()`, which should be regression-tested around every constructor failure point.

## Test Signals

Useful tests include table creation for old and `capi:` cipher syntax, all IV modes, keyring and hex keys, suspended `key set`/`key wipe`, integrity `none` and `aead`, non-512 sector sizes, discard/flush bypass, bio splitting limits, AEAD bad-tag logging, zoned device write ordering, atomic writes, and failure injection for mempool/workqueue/crypto allocation paths. Runtime tests should verify data survives remounts and table reloads, status output round-trips table syntax, IMA status omits secret key bytes, and no pending-page counter leaks remain after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-crypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-delay.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-delay.c`

## Purpose

`dm-delay.c` implements the `delay` target, a testing and simulation target that remaps reads, writes, and flushes to configured devices while delaying each class independently. It can use the same backing mapping for all operations, separate read/write mappings, or separate read/write/flush mappings.

## Important APIs, Types, and Functions

`struct delay_class` stores a `dm_dev`, starting sector, millisecond delay, and active operation count for one IO class. `struct delay_c` owns the delayed-bio list, timer or low-latency worker, workqueue, locks, `may_delay` suspend gate, and the three classes. `delay_ctr()` parses 3, 6, or 9 arguments and chooses either a kthread for delays under 50 ms or a timer plus workqueue for longer delays. `delay_map()` selects read/write/flush class, remaps the bio, and delegates to `delay_bio()`. `flush_delayed_bios()` drains expired or all delayed bios, decrements class counters, rearms timers, and submits bios through `dm_submit_bio_remap()`.

## Control Flow

Mapped bios are immediately rewritten to the selected backing device and sector. If the selected class delay is zero, `delay_bio()` returns `DM_MAPIO_REMAPPED`. Otherwise, per-bio `dm_delay_info` is filled, the bio is appended to `delayed_bios`, and either the fast kthread is woken or the timer is reduced to the new expiry. The timer queues `flush_expired_bios()` on `kdelayd`; the fast worker loops, drains expired bios, and sleeps for a fraction of the minimum requested delay.

Suspend sets `may_delay=false`, deletes the timer for timer mode, and flushes all delayed bios. Resume re-enables delay for future IO. Destruction shuts down timer/workqueue or kthread and releases every referenced `dm_dev`.

## State and Persistence Behavior

The target has no persistent metadata. Runtime state is the delayed bio queue and per-class operation counters. The `process_bios_lock` serializes list extraction and flushing, while `delayed_bios_lock` protects list mutation and suspend gating.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.presuspend`, `.resume`, `.status`, `.iterate_devices`, and optional zoned `.report_zones`. It uses device-mapper per-bio data, timers, workqueues, kthreads, bio lists, and `dm_report_zones()` for the read class. It advertises integrity pass-through and host-managed zoned support.

## Risks and Edge Cases

Suspend races are controlled by `may_delay` under the list spinlock, but latency behavior depends on jiffies granularity for timer mode and sleep interval selection for fast mode. The constructor may acquire the same device multiple times when read/write/flush share arguments, so destructor must release all three class references. Status info reports in-flight delayed counts and can be used to detect leaks.

## Test Signals

Tests should cover 3/6/9 argument tables, zero delay pass-through, short-delay kthread mode, long-delay timer mode, flush-specific routing, suspend flushing, status counters, and zoned report forwarding from the read device. Timing tests should allow scheduler tolerance while verifying ordering and eventual completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-dust.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-dust.c`

## Purpose

`dm-dust.c` implements the `dust` test target, which emulates media read errors for selected logical blocks and optional transient write failures. It is designed for fault-injection tests that need deterministic bad-block behavior above a normal block device.

## Important APIs, Types, and Functions

Bad blocks are represented by `struct badblock`, keyed by block number in an RB tree and carrying a remaining write-fail count. `struct dust_device` stores the backing `dm_dev`, RB tree root, badblock count, lock, configured block size and sector shift, starting offset, and mode flags. `dust_ctr()` parses `<device_path> <offset> <blksz>`, validates a power-of-two block size, opens the backing device, initializes the badblock tree, and caps target max IO length to one dust block. `dust_map()` remaps the bio and dispatches to `dust_map_read()` or `dust_map_write()`. Runtime control is via `dust_message()` with commands such as `addbadblock`, `removebadblock`, `queryblock`, `countbadblocks`, `clearbadblocks`, `listbadblocks`, `enable`, `disable`, and `quiet`.

## Control Flow

Reads are only failed when `fail_read_on_bb` is enabled. The sector is converted to dust block number, the badblock tree is searched under `dust_lock`, and matching reads return `DM_MAPIO_KILL`. Writes to a bad block either decrement `wr_fail_cnt` and fail while the count remains positive, or remove the block from the badblock tree and remap normally. Messages mutate or query the RB tree while holding the spinlock, except bulk clear swaps the tree out under lock and frees it outside the critical section.

## State and Persistence Behavior

Bad-block state is entirely in memory and is lost when the mapping is destroyed. There is no on-disk metadata. The backing device receives normal remapped IO for non-failed operations, and successful writes can clear a badblock entry.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.message`, `.status`, `.prepare_ioctl`, and `.iterate_devices`. It uses Linux RB trees, device-mapper messages, `dm_set_target_max_io_len()`, and block ioctl forwarding when the mapping covers the full lower device exactly.

## Risks and Edge Cases

Block-range validation checks `block > size`, which means a block equal to the computed count is accepted even though valid zero-based block indexes normally end at `size - 1`; boundary tests should verify intended semantics. The free path relies on `struct rb_node` being the first field of `struct badblock`, so `kfree(node)` works by layout. Quiet mode suppresses many diagnostics, which can hide command mistakes in tests. The target serializes all tree access with a spinlock, so list output can hold the lock while emitting potentially many lines.

## Test Signals

Tests should create bad blocks, enable/disable read failure, verify read kill versus bypass, verify write-fail counters, verify successful writes remove bad blocks, exercise query/list/count/clear messages, test boundary block numbers, and confirm table/status output round-trips. Ioctl forwarding should be checked for full-size and offset mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-dust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ebs-target.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-ebs-target.c`

## Purpose

`dm-ebs-target.c` implements the `ebs` target, which emulates a smaller exposed logical block size on a backing device with a larger logical block size. It is intended for cases such as 512-byte sector emulation over 4K-native media and for testing `dm-bufio` overhead.

## Important APIs, Types, and Functions

`struct ebs_c` stores the backing device, `dm_bufio_client`, ordered workqueue, queued bio list, lock, start sector, emulated and underlying block sizes, sector-to-block shift, and whether the underlying size was explicitly configured. `ebs_ctr()` parses `<dev_path> <offset> <ebs> [<ubs>]`, validates power-of-two sector sizes, infers `ubs` from the lower device if omitted, validates start alignment, creates the bufio client, and creates an ordered workqueue. `ebs_map()` remaps flushes directly, queues partial or overlapping IO for bufio processing, and remaps fully aligned IO directly after forgetting cached buffers. `__ebs_process_bios()` performs read, write, and discard processing from the queued list.

## Control Flow

Partial reads and writes are queued to the worker. The worker first prefetches all read buffers and misaligned write-edge buffers, then copies data between bio vectors and bufio blocks through `__ebs_rw_bio()`/`__ebs_rw_bvec()`. Writes use read-modify-write unless a full underlying block is overwritten, in which case `dm_bufio_new()` avoids an unnecessary read. Discards forget cached buffers and issue lower-device discards only for complete underlying blocks, avoiding partial-block data loss. Dirty buffers are written before bios are ended so FUA/sync semantics are addressed.

## State and Persistence Behavior

There is no independent metadata. Data persistence is the lower block device content, mediated by `dm-bufio` for partial-block modifications. `ebs_postsuspend()` resets the bufio client, dropping cached state at suspend.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.postsuspend`, `.status`, `.io_hints`, `.prepare_ioctl`, and `.iterate_devices`. It depends on `dm-bufio`, ordered workqueues, bio lists, block queue limits, and lower-device logical block size. IO hints expose the emulated logical size and underlying physical size to upper layers.

## Risks and Edge Cases

Correctness depends on handling partial first and last underlying blocks without discarding or overwriting unrelated data. The worker records an error if any per-buffer copy fails but still attempts remaining buffers, so tests should inspect final bio status. Fully aligned direct IO must invalidate bufio cache ranges or stale cached data could later overwrite direct writes. Flushes are remapped, not bufio-queued, so dirty bufio write ordering around flush-sensitive workloads is an important test area.

## Test Signals

Tests should cover omitted and explicit `ubs`, invalid sizes and offsets, partial read/write at both edges, full-block direct IO, discard alignment, cache invalidation after direct writes, postsuspend cache reset, io-hints values, and ioctl forwarding only for exact full-device mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ebs-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-era-target.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-era-target.c`

## Purpose

`dm-era-target.c` implements the `era` target, which tracks which data blocks were written during monotonically numbered eras. It maintains persistent metadata on a separate metadata device, marks writes in the current writeset, archives old writesets, and digests them into an era array that userspace can inspect via metadata snapshots.

## Important APIs, Types, and Functions

The metadata layer uses `struct era_metadata`, containing block manager, transaction manager, space map, current era, two preallocated writesets, writeset btree root, era array root, bitset info, array info, metadata snapshot location, and archive flag. `struct writeset` contains persistent writeset metadata plus an in-core bitmap. On-disk layout is `struct superblock_disk`, validated by `sb_validator`.

Metadata operations include `format_metadata()`, `open_metadata()`, `metadata_resize()`, `metadata_era_rollover()`, `metadata_commit()`, `metadata_checkpoint()`, `metadata_take_snap()`, `metadata_drop_snap()`, and `metadata_get_stats()`. Digest processing is implemented as a resumable `struct digest` state machine with lookup, transcribe, and remove steps. Target state is `struct era`, containing metadata and origin devices, block-size fields, ordered workqueue, deferred bio queue, RPC queue, digest state, and suspended flag.

## Control Flow

Constructor parsing is `<metadata dev> <data dev> <data block size (sectors)>`. `era_ctr()` opens both devices, validates the block size, sets max IO length to one era block, opens or formats metadata, creates the worker, and initializes deferred and RPC queues.

`era_map()` remaps every bio to the origin device. Non-flush writes to blocks not yet marked in the current writeset are deferred. The worker marks those blocks in the on-disk bitset, commits metadata if any new bit was set, then submits the bios. Already-marked writes, reads, flushes, and discards pass through. Control messages are sent as RPCs to the same worker so metadata mutation is serialized.

On preresume, the target resizes metadata if the target length changed, starts the worker, and rolls over to a new era. On postsuspend, it archives the current era, stops the worker, and commits metadata. Old archived writesets are digested incrementally into the era array in `INSERTS_PER_STEP` batches to reduce latency.

## State and Persistence Behavior

Era metadata is persistent. The superblock stores data and metadata block sizes, number of tracked blocks, current era, current writeset root, writeset tree root, era array root, and held metadata snapshot location. Current writesets are maintained both on disk and in memory; archived writesets are inserted into a btree keyed by era, then eventually transcribed into the era array and removed. Metadata snapshots increment reference counts on the superblock clone, writeset tree root, and era array root until dropped.

## Dependencies and Integration Points

The file depends on device-mapper persistent-data libraries: transaction manager, disk bitset, btree, array, space map, and block manager. It integrates through `.ctr`, `.dtr`, `.map`, `.postsuspend`, `.preresume`, `.status`, `.message`, `.iterate_devices`, and `.io_hints`. Messages supported are `checkpoint`, `take_metadata_snap`, and `drop_metadata_snap`.

## Risks and Edge Cases

The IO path defers first writes to unmarked blocks until metadata can be committed, so metadata-device latency directly affects first-write latency per era. Several error paths contain `FIXME: fail mode` comments; failed bitset updates or commits currently error affected bios but do not implement a broader target failure mode. RCU protects current-writeset swaps, and all metadata mutation is intended to run on the ordered worker; tests should stress suspend/resume and message races. The `valid_nr_blocks()` limit is below 2^31 due to both disk bitset and in-core bitmap constraints.

## Test Signals

Tests should cover first-write deferral, repeated writes to already-marked blocks, checkpoint era rollover, suspend/resume archive and commit, metadata resize after table length changes, metadata snapshot take/drop, status used/total/current-era output, digest progress for archived writesets, invalid superblock/version/checksum handling, and metadata-device IO failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-era-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.c`

## Purpose

`dm-exception-store.c` provides the registry and common constructor/destructor logic for snapshot exception-store implementations. Exception stores manage how snapshot copy-on-write metadata records old-to-new chunk mappings and merge progress.

## Important APIs, Types, and Functions

The file maintains `_exception_store_types`, protected by `_lock`. `dm_exception_store_type_register()` and `dm_exception_store_type_unregister()` add and remove implementations. `_get_exception_store_type()` finds a registered type and pins its module. `get_type()` autoloads modules named `dm-exstore-<type_name>`, repeatedly truncating suffixes after `-` to support families such as `clustered-shared`. `put_type()` releases the module reference.

`dm_exception_store_create()` parses snapshot exception-store arguments, chooses persistent (`P`) or transient (`N`) store type, validates chunk size, calls the selected type constructor, and returns a `struct dm_exception_store`. `dm_exception_store_destroy()` calls the type destructor and releases the module. `dm_exception_store_set_chunk_size()` enforces power-of-two chunk sizes that are multiples of both origin and COW logical block sizes.

## Control Flow

Snapshot target construction calls `dm_exception_store_create()`. The first argument selects persistent or transient mode using its first character; any suffix after that character is passed as type-specific options. The second argument is chunk size. Once the type is found and pinned, the common store object records the snapshot pointer and chunk geometry, then delegates to the type constructor. Initialization registers both built-in transient and persistent snapshot store types; exit unregisters them in reverse order.

## State and Persistence Behavior

This file itself persists no metadata. Persistence is delegated to the selected store type, typically persistent snapshot metadata on the COW device or transient in-memory metadata. Common state is the registered type list, module references, chunk size/mask/shift, and the type-specific `context` pointer.

## Dependencies and Integration Points

It integrates with `dm-snap` through `dm_snap_origin()`, `dm_snap_cow()`, and `struct dm_snapshot`, and with store implementations such as the persistent and transient stores. It uses module autoloading, block logical-size queries, exported symbols for external store modules, and device-mapper error reporting via `ti->error`.

## Risks and Edge Cases

Chunk-size validation must match both origin and COW devices or snapshot metadata can become unaligned. Autoload fallback by truncating names can load a broader module than the exact requested type; the subsequent lookup still requires the requested registered type. Registration is protected by a spinlock, but implementation objects must remain valid until unregister. Constructor failure unwinds module references and allocated store state.

## Test Signals

Tests should register duplicate types, unregister missing types, create `P` and `N` stores, reject invalid chunk sizes, verify module autoload naming fallback, and exercise constructor failure unwinding. Snapshot integration tests should confirm chunk geometry matches table status and that store destruction releases module references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.h -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.h`

## Purpose

`dm-exception-store.h` defines the snapshot exception-store interface shared by `dm-snap`, common registry code, and concrete persistent/transient store implementations. It describes snapshot chunk identifiers, exception records, store operations, and helper functions for packed consecutive chunk counts.

## Important APIs, Types, and Functions

`chunk_t` aliases `sector_t` for snapshot chunk numbers. `struct dm_exception` maps `old_chunk` to `new_chunk`; on 64-bit chunk values, the top 8 bits of `new_chunk` encode a count of following contiguous chunks. `struct dm_exception_store_type` is the implementation vtable: constructor/destructor, metadata loading, exception preparation/commit, merge preparation/commit, snapshot drop, status, usage, and registry list node. `struct dm_exception_store` holds the chosen type, parent snapshot, chunk geometry, type-specific context, and an overflow-support flag.

Inline helpers include `dm_chunk_number()`, `dm_consecutive_chunk_count()`, increment/decrement helpers for the packed count, `get_dev_size()`, and `sector_to_chunk()`. Public functions register/unregister store types, set chunk size, create/destroy stores, and initialize/exit built-in store modules.

## Control Flow

The snapshot target includes this header to create a store, load metadata through `read_metadata()`, allocate and commit exceptions while copying chunks, and coordinate merge operations. Store implementations include this header to provide a `dm_exception_store_type` and to call registration helpers during module init.

## State and Persistence Behavior

The header defines the contract for persistent state but does not implement it. Persistent behavior is implementation-specific: persistent stores record metadata on the COW device, while transient stores keep it in memory. The packed consecutive-count bits are part of the in-memory/public exception representation and must be handled carefully by all users.

## Dependencies and Integration Points

The header depends on block-device, hash-list, list, and device-mapper definitions. It forward-declares `struct dm_snapshot` and exposes `dm_snap_origin()` and `dm_snap_cow()` so common code can validate chunk sizes against both devices. Built-in implementations are declared as `dm_persistent_snapshot_init/exit()` and `dm_transient_snapshot_init/exit()`.

## Risks and Edge Cases

The packed high bits in `new_chunk` reduce available chunk-number bits to 56 when used; code must call `dm_chunk_number()` before treating it as a raw chunk. Increment and decrement helpers use `BUG_ON()` for overflow/underflow detection. Store vtable callbacks have asynchronous and failure-sensitive semantics, especially `commit_exception()` and merge operations, so implementation tests need to verify callback completion and metadata validity.

## Test Signals

Tests should validate packed consecutive chunk handling, sector-to-chunk conversion, store type registration lifecycle, create/destroy API behavior, merge callback semantics, overflow support reporting, and usage/status output across persistent and transient implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-flakey.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-flakey.c`

## Purpose

`dm-flakey.c` implements the `flakey` test target, which simulates intermittent device failures and data corruption. It alternates between configured up and down intervals and can error reads, drop or error writes, corrupt fixed bytes, or randomly corrupt reads/writes with configured probabilities.

## Important APIs, Types, and Functions

`struct flakey_c` stores the backing device, start time, offset, up/down intervals, feature flags, fixed corruption parameters, and random corruption probabilities. `struct per_bio_data` records whether a bio can be corrupted and preserves the original iterator for read completion corruption. `parse_features()` handles `error_reads`, `drop_writes`, `error_writes`, `corrupt_bio_byte`, `random_read_corrupt`, and `random_write_corrupt`, while rejecting conflicting combinations. `flakey_map()` implements interval-based behavior. `flakey_end_io()` applies read corruption after successful lower-device completion. `clone_bio()` creates private write copies so corrupting a write does not mutate the caller's original bio.

## Control Flow

Constructor syntax is `<dev_path> <offset> <up interval> <down interval> [<#feature args> [<arg>]*]`. If no feature is specified, down intervals default to erroring both reads and writes. During up intervals, bios are simply remapped. During down intervals, reads may be killed, passed through for later corruption, or randomly corrupted on completion. Writes may be dropped, failed, fixed-byte corrupted, random-byte corrupted, or passed through. Zone-management operations bypass failure behavior and are always remapped.

## State and Persistence Behavior

The target has no persistent metadata. Runtime behavior is based on `jiffies - start_time` modulo the up/down period, so reloading the table resets the failure schedule. Corruption settings and random probabilities live only in `flakey_c`.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.end_io`, `.status`, `.prepare_ioctl`, `.iterate_devices`, and optional zoned `.report_zones`. It uses device-mapper argument parsing, per-bio data, random helpers, bio cloning, page allocation, and block ioctl forwarding. It advertises zoned host-managed support and crypto pass-through.

## Risks and Edge Cases

Feature conflicts are important: dropping or erroring writes cannot be combined with write corruption, and erroring reads cannot be combined with read corruption. Write corruption clones can fail allocation, in which case the original bio is remapped uncorrupted. Random corruption probabilities are compared against `PROBABILITY_BASE` and should be tested at 0, 1, and full-base values. The target mutates data buffers, so read corruption only occurs after successful IO and only when the saved iterator still describes the original data range.

## Test Signals

Tests should cover interval transitions, default all-IO failure mode, each feature and conflict, fixed-byte corruption offsets, flag-mask matching, random corruption probabilities, write-clone allocation failure behavior, zone-management bypass, status table round-trip, ioctl forwarding, and report-zones forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-flakey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ima.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-ima.c`

## Purpose

`dm-ima.c` implements Integrity Measurement Architecture support for device mapper. It builds structured measurements for table load, resume, remove, table clear, and rename events so IMA can record security-relevant DM device and target metadata.

## Important APIs, Types, and Functions

`fix_separator_chars()` escapes backslash, semicolon, equals, and comma so generated key-value records can be parsed safely. `dm_ima_alloc()` optionally wraps allocation in `memalloc_noio_save()` for paths that cannot recurse into IO. `dm_ima_alloc_and_copy_name_uuid()`, `dm_ima_alloc_and_copy_device_data()`, and `dm_ima_alloc_and_copy_capacity_str()` build metadata strings. `dm_ima_measure_data()` calls `ima_measure_critical_data()`. Public lifecycle functions are `dm_ima_reset_data()`, `dm_ima_measure_on_table_load()`, `dm_ima_measure_on_device_resume()`, `dm_ima_measure_on_device_remove()`, `dm_ima_measure_on_table_clear()`, and `dm_ima_measure_on_device_rename()`.

## Control Flow

On table load, the file allocates buffers, prefixes the DM version and device metadata, calls each target's `STATUSTYPE_IMA` status callback, emits one or more `dm_table_load` measurements if the fixed buffer fills, and computes a SHA-256 hash over measured table data. That hash and device metadata are stored as the inactive table state. On resume with table swap, inactive table hash and metadata become active before measuring `dm_device_resume` with current capacity. Remove measures all active/inactive metadata and hashes, then frees and resets IMA state. Table clear measures inactive table state and, for `new_map`, moves active state into inactive slots. Rename rebuilds active device metadata and measures old plus new identity.

## State and Persistence Behavior

IMA data is not block-device metadata; it is measurement-log evidence. `struct mapped_device` carries active and inactive table metadata strings, hashes, lengths, target counts, and DM version length. Ownership is transferred between active/inactive slots during resume and table clear; remove frees all owned buffers and resets the structure.

## Dependencies and Integration Points

The implementation depends on `dm-core.h`, `dm-ima.h`, Linux IMA, SHA-256 helpers, mapped-device naming helpers, disk capacity, and each target's `STATUSTYPE_IMA` status. It is compiled only when `CONFIG_IMA` enables the non-stub declarations in the header.

## Risks and Edge Cases

Measurements are best-effort: allocation failure generally skips measurement rather than failing table operations. Fixed buffer lengths require chunking on table load; correctness depends on hashing exactly what was measured. String escaping must cover all separators used by the key-value format. Pointer-sharing between active and inactive slots is explicitly checked before freeing to avoid double-free, so table swap and clear paths need careful ownership tests.

## Test Signals

Tests should exercise table loads with many targets, targets with long IMA status strings, resume with and without swap, table clear with and without `new_map`, rename, remove-all versus single remove, allocation failure paths, separator escaping in names/UUIDs/status strings, and hash stability for identical tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ima.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ima.h -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-ima.h`

## Purpose

`dm-ima.h` defines the data structures, buffer limits, version string, and public hooks for device-mapper IMA measurements. It also provides no-op inline stubs when IMA support is disabled.

## Important APIs, Types, and Functions

The header defines fixed buffer sizes for full measurements, device metadata, target metadata, target data, and capacity strings. `DM_IMA_VERSION_STR` encodes the device-mapper major/minor/patchlevel into the measurement prefix. Under `CONFIG_IMA`, `struct dm_ima_device_table_metadata` stores device metadata, table hash, and target count for one table slot, while `struct dm_ima_measurements` contains active and inactive slots plus version-string length. Public hooks cover reset, table load, device resume, device remove, table clear, and device rename.

## Control Flow

Core device-mapper code calls these hooks at lifecycle points. With IMA enabled, the implementation in `dm-ima.c` emits measurements and updates active/inactive hashes. With IMA disabled, inline stubs compile away the calls, keeping call sites simple and avoiding conditional code in the DM core.

## State and Persistence Behavior

The header describes in-memory measurement state embedded in `struct mapped_device`. It does not define persistent block metadata. Measurement results are intended for IMA logs through the implementation.

## Dependencies and Integration Points

It depends on DM version macros and forward declarations of `struct mapped_device` and `struct dm_table` from the including DM core context. The target status integration is indirect: table-load measurement code requests `STATUSTYPE_IMA` from each target.

## Risks and Edge Cases

The fixed buffer-size contract means implementation and target IMA status output must stay within expected limits or measurement chunking/truncation behavior becomes relevant. Stub functions must exactly match enabled prototypes so call sites remain build-stable across `CONFIG_IMA`.

## Test Signals

Build tests should cover `CONFIG_IMA=y` and `CONFIG_IMA=n`. Runtime tests should verify active/inactive state transitions, version-string formatting, target status inclusion, and no-op behavior when IMA is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ima.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-init.c -->
# `sources/distributed-fs/ceph-client/drivers/md/dm-init.c`

## Purpose

`dm-init.c` implements early boot creation of mapped devices from kernel module parameters. It parses `dm-mod.create=...` table descriptions and optional `dm-mod.waitfor=...` device names, waits for dependencies, and invokes `dm_early_create()`.

## Important APIs, Types, and Functions

`struct dm_device` wraps `struct dm_ioctl`, an array of up to `DM_MAX_TARGETS` target specs, an array of target argument strings, and a list node. `dm_allowed_targets` restricts early boot setup to `crypt`, `delay`, `linear`, `snapshot-origin`, `striped`, and `verity`. `str_field_delimit()` splits and trims fields in place. `dm_parse_table_entry()` parses `<start_sector> <num_sectors> <target_type> <target_args>`. `dm_parse_device_entry()` parses `name,uuid,minor,flags,table`. `dm_parse_devices()` builds the list of requested devices. `dm_init_init()` is registered as a `late_initcall`.

## Control Flow

If `create` is unset, initialization exits. Otherwise the string is length-checked, duplicated, parsed into `dm_device` objects, and device probing is waited for. Each `waitfor` path is repeatedly resolved through `early_lookup_bdev()` with a short sleep until available. Then every parsed device is passed to `dm_early_create()` with its ioctl header, target specs, and target argument strings. Cleanup frees all allocated specs, argument strings, devices, and the duplicated input buffer.

## State and Persistence Behavior

This file has no persistent metadata of its own. It creates mapped devices during boot; their persistence depends on the resulting DM targets and userspace policy. Parser allocations are marked `__init` flow and freed after setup.

## Dependencies and Integration Points

It integrates with module parameters `create` and `waitfor`, kernel initcall ordering, block-device probing, `early_lookup_bdev()`, device-mapper ioctl structures, and `dm_early_create()`. It deliberately limits target types for early boot safety and availability.

## Risks and Edge Cases

Parsing is in-place and currently lacks escaped-character support, so names, UUIDs, and target arguments cannot contain delimiters that need escaping. Fixed limits cap devices, targets, wait-for entries, and string length. Error handling aborts on malformed fields or disallowed targets, but devices parsed before the error are cleaned up. The wait loop has no timeout, so a missing `waitfor` device can stall boot indefinitely.

## Test Signals

Tests should cover valid single and multi-device strings, multi-target tables, empty UUID/minor handling, persistent minor encoding, read-only/read-write flags, disallowed target rejection, malformed delimiters, length and count limits, waitfor behavior, and cleanup after mid-parse allocation or validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-init.c -->
