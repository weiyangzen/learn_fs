# Group Research: group_921_linux_dm_sources_block_storage_linux_dm_drivers_md_dm_crypt_c_source_3b3b20a508f7

Scope checked: `Docs/research_subset_a.md` includes `sources/block-storage/linux-dm`. All files listed for this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-crypt.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-crypt.c

## Role
Implements the `crypt` device-mapper target: a transparent block encryption/decryption layer that maps a logical range to an underlying block device while transforming bio data with Linux Crypto API skcipher or AEAD algorithms.

## Main Structures
- `struct crypt_config` stores the target-wide device, offset, cipher transforms, key material, IV generator, workqueues, write-ordering thread, mempools, bioset, integrity settings, sector size, and feature flags.
- `struct dm_crypt_io` is per-bio state containing the original bio, optional integrity metadata buffer, pending counters, async crypto context, error state, sector, and write-tree node.
- `struct convert_context` tracks multi-sector crypto conversion progress across input/output bios and async crypto restarts.
- `struct crypt_iv_operations` abstracts IV mode lifecycle and generation/postprocessing.

## Target Interface
- Constructor syntax is `<cipher> [<key>|:<key_size>:<user|logon|encrypted|trusted>:<key_description>] <iv_offset> <dev_path> <start> [<#opts> <opts>...]`.
- `crypt_ctr()` parses optional features first, configures cipher/IV/key state, validates offsets, opens the backing device, creates request/page/tag mempools, allocates workqueues, and starts the ordered write submission thread.
- `crypt_map()` bypasses flush and discard directly to the lower device, validates sector alignment and size against the internal encryption sector size, allocates integrity metadata when needed, and submits reads or writes into the crypto pipeline.
- `crypt_status()` emits table, info, and IMA status. Table status can emit either the hex key or a keyring descriptor.
- `crypt_message()` supports suspended-only key operations: `key set <key>` and `key wipe`.
- `crypt_preresume()` rejects resume if no valid key is installed.

## Crypto and IV Modes
- Supports legacy cipher syntax (`cipher[:keycount]-mode-iv:ivopts`) and new Crypto API syntax (`capi:cipher_api_spec-iv:ivopts`).
- IV generators include `plain`, `plain64`, `plain64be`, `essiv`, `benbi`, `null`, `lmk`, `tcw`, `random`, `eboiv`, and `elephant`.
- Compatibility modes implement Loop-AES LMK, old TrueCrypt TCW whitening, BitLocker EBOIV, and BitLocker Elephant diffuser behavior.
- `essiv` is represented through the Crypto API transform string, while this file supplies the plain sector-number IV input.
- Multi-key modes distribute sectors over `tfms_count`, with LMK using 64 transforms and key splitting.

## Data Path
- Writes allocate a new clone bio with freshly allocated pages, encrypt from the original bio into that clone, then submit the encrypted clone to the lower device.
- Reads clone and submit the original bio layout to the lower device first; successful completion queues in-place decryption into the original bio.
- `crypt_convert()` walks one encryption sector at a time, allocates/reuses crypto requests, handles synchronous and asynchronous Crypto API completion, and maps errors to block status.
- `kcryptd_async_done()` handles Crypto API callbacks, post-IV transforms, AEAD authentication failures, request cleanup, and final read/write completion.
- Separate `io_queue`, `crypt_queue`, and `dmcrypt_write` thread keep IO submission, CPU crypto work, and ordered write dispatch from blocking each other.
- Zoned devices force no write workqueue and inline write completion to preserve write ordering; zone append is emulated to avoid IV mismatch.

## Integrity Support
- Optional `integrity:<tag_size>:aead` enables AEAD authenticated encryption over sector number, IV, data, and tag.
- Optional `integrity:<tag_size>:none` provides per-sector on-disk metadata space, including random IV storage when needed.
- Requires the lower device integrity profile `DM-DIF-EXT-TAG` with matching tuple/tag size and interval size.
- AEAD failures log rate-limited integrity errors and audit events and surface as `BLK_STS_PROTECTION`.

## Key Handling
- Hex keys are decoded into `cc->key`, installed into all transforms, then the supplied key string is wiped in-place.
- Keyring descriptors may reference `logon`, `user`, `encrypted`, or `trusted` keys when configured; key descriptors with whitespace are rejected because DM table status does not escape them.
- HMAC-based `authenc(...)` AEAD keys are repacked into the Crypto API `crypto_authenc_key_param` format.
- `crypt_wipe_key()` clears key validity, randomizes key material into transforms, wipes IV-private material, clears stored keyring state, and zeroes the in-memory key.

## Important Invariants
- Bios must be aligned and sized to `sector_size`; `iv_offset` must also align to that sector size.
- Request memory layout is carefully aligned as crypto request, private `dm_crypt_request`, IV, original IV, original sector, and tag offset.
- Buffer page allocation is serialized on fallback to avoid mempool deadlock when multiple large bios need the whole pool.
- Page usage is capped per dm-crypt client from a global low-memory page budget.
- Flush and discard bypass crypto because they carry no transformable data; discard ordering is left to callers via flush.
- Inline write mode waits for all async crypto completions before submitting writes that require ordering.

## Filesystem/Storage Relevance
`dm-crypt` is the main Linux block encryption target used beneath filesystems and above raw disks, partitions, LVM, RAID, or other DM targets. Its sector sizing, integrity tag handling, discard policy, and zoned-device behavior directly affect filesystem correctness, performance, and recoverability.

## Notable Risks
- Key, IV, integrity, and async completion paths are tightly coupled; ordering mistakes can create silent corruption or authentication failures.
- Legacy compatibility modes intentionally preserve older, weaker on-disk formats and should be understood as compatibility paths.
- Memory pressure behavior is complex because crypto requests, clone bios, pages, and integrity tags all have independent pools and fallback paths.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-delay.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-delay.c

## Role
Implements the `delay` device-mapper target, which remaps bios to one or more lower devices while delaying read, write, and optionally flush classes by configurable millisecond intervals.

## Target Interface
- Constructor accepts exactly 3, 6, or 9 arguments.
- Three arguments define a single class used for reads, writes, and flushes: `<device> <offset> <delay>`.
- Six arguments define separate read and write classes, with flush using the write class.
- Nine arguments define independent read, write, and flush classes.

## Core Mechanics
- `struct delay_class` stores the lower device, start sector, delay in milliseconds, and count of delayed operations.
- `delay_map()` chooses a class based on bio direction and `REQ_PREFLUSH`, remaps the bio to the class device/start, then calls `delay_bio()`.
- Delayed bios store `struct dm_delay_info` in per-bio data, including class pointer and expiration jiffies.
- A global `delayed_bios_lock` protects each target's delayed list; a per-target timer schedules a work item when the next bio expires.
- `flush_expired_bios()` drains expired bios into a local list and submits them outside the list lock.
- `delay_presuspend()` disables new delays, cancels the timer, and flushes all queued bios.

## Status and Device Iteration
- Info status reports queued operation counts for read, write, and flush classes.
- Table status reconstructs only the classes explicitly supplied in the original argument count.
- `iterate_devices` reports all three class devices, even if they refer to the same underlying device.

## Important Invariants
- Bios already have their target device and sector rewritten before being delayed.
- `may_delay` prevents suspend from racing in new delayed bios after the flush-all path begins.
- Timer updates are serialized by `timer_lock` so the earliest expiry is preserved.

## Filesystem/Storage Relevance
This is a timing/fault-injection target for block-stack testing. It can model asymmetric read/write/flush latency and can expose ordering or timeout assumptions in filesystems and upper storage layers.

## Notable Risks
- The delayed bio list lock is global rather than per-target.
- Delays are based on jiffies and workqueue scheduling, so timing is approximate.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-delay.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-dust.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-dust.c

## Role
Implements the `dust` test target, which emulates bad blocks by failing reads for selected logical blocks and optionally failing a configured number of writes before a write clears a bad block.

## Data Model
- `struct dust_device` stores the lower device, start sector, block size, sectors-per-block mapping, rb-tree of bad blocks, count, lock, read-fail enable flag, and quiet/verbose mode.
- `struct badblock` is an rb-tree entry keyed by logical block number and stores an 8-bit remaining write-failure count.

## Target Interface
- Constructor syntax is `<device_path> <offset> <blksz>`.
- Block size must be at least 512 bytes, a power of two, and no larger than the target length or 1 GiB.
- The target maximum IO length is set to exactly one configured block.

## Runtime Messages
- `enable` and `disable` toggle failing reads/writes on listed bad blocks.
- `addbadblock <block> [write_fail_count]` inserts a bad block, with `write_fail_count` capped at 255.
- `removebadblock <block>` deletes one bad block.
- `queryblock <block>`, `countbadblocks`, `listbadblocks`, and `clearbadblocks` inspect or reset state.
- `quiet` toggles diagnostic logging.

## IO Behavior
- `dust_map()` always remaps the bio to the lower device and target-relative sector.
- When enabled, reads whose logical block appears in the rb-tree return `DM_MAPIO_KILL`.
- Writes to a listed block fail while `wr_fail_cnt` is nonzero, decrementing that count each time.
- Once the write-fail count reaches zero, a write removes the block from the badblock tree and is remapped normally.

## Important Invariants
- The rb-tree and badblock count are protected by `dust_lock`.
- Logical block conversion uses `sect_per_block_shift`, relying on the constructor’s power-of-two block size validation.
- IO splitting to a single dust block keeps read/write lookup semantics unambiguous.

## Filesystem/Storage Relevance
`dm-dust` is a deterministic media-error emulator. It is useful for testing filesystem read-error handling, repair paths, scrubbing, retries, and behavior when writes appear to repair sectors.

## Notable Risks
- The message API keeps all badblock state in memory; it is not persistent.
- Range validation compares selected block values against lower-device size after sector-to-block conversion and is intentionally simple for a test target.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-dust.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ebs-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ebs-target.c

## Role
Implements the `ebs` target, which emulates a smaller logical block size on an underlying device with a larger native block size, for example 512-byte logical sectors on a 4 KiB-native device.

## Target Interface
- Constructor syntax is `<dev_path> <offset> <ebs> [<ubs>]`.
- `<ebs>` and optional `<ubs>` are block sizes in 512-byte sectors and must be powers of two.
- If `<ubs>` is omitted, it is derived from the lower device logical block size.
- The target rejects offsets not aligned to the underlying block size.

## Core Mechanics
- `struct ebs_c` stores the lower device, dm-bufio client, ordered workqueue, queued bio list, start sector, emulated block size, underlying block size, and sector-to-buffer block shift.
- A dm-bufio client is created using the underlying block size in bytes.
- Partial or overlapping bios are queued to `__ebs_process_bios()`, which uses bufio reads or new buffers to copy between bio pages and underlying-size blocks.
- Fully aligned bios bypass the workqueue and are remapped directly after forgetting any overlapping cached buffers.
- Discards are trimmed to complete underlying blocks only; partial first and last underlying blocks are not discarded.

## Read/Write Handling
- Reads copy bytes from bufio blocks into bio vectors and flush the page cache line state with `flush_dcache_page()`.
- Writes use read-modify-write when a bio only partially overwrites an underlying block and use `dm_bufio_new()` when a full block is overwritten.
- Dirty buffers are written before bio completion so `REQ_FUA` and `REQ_SYNC` semantics are preserved as far as this target can enforce them.
- Prefetching is used for reads and for misaligned write edge blocks.

## Status and Limits
- Table status emits `<dev> <start> <ebs>` or `<dev> <start> <ebs> <ubs>` depending on whether `<ubs>` was supplied.
- IO hints expose logical block size as `<ebs>` and physical block size as `<ubs>`.
- Flush and discard are enabled; secure erase, write same, and write zeroes are disabled.

## Important Invariants
- `to_bytes(ebs)` must fit in one page.
- Direct IO paths must drop relevant bufio cache state before remapping.
- The workqueue is ordered, serializing bufio-mediated read-modify-write sequences.

## Filesystem/Storage Relevance
This target lets upper layers and filesystems exercise smaller logical block sizes even when the lower device requires larger physical writes. It is especially relevant for testing filesystem behavior on 4K-native media with 512-byte emulation.

## Notable Risks
- Partial-block read-modify-write depends on bufio cache coherence with directly remapped aligned IO.
- The target is not a general transformation layer for all block operations; several write-like operations are explicitly disabled.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ebs-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-era-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-era-target.c

## Role
Implements the `era` target, a persistent changed-block tracker. It records which fixed-size data blocks were written during each era, supports checkpointing to advance eras, and exposes metadata snapshots for userspace inspection.

## Persistent Metadata
- The superblock lives at block 0 and includes checksum, magic, version, metadata space-map root, data block size, metadata block size, block count, current era, current writeset, writeset tree root, era array root, and metadata snapshot block.
- Uses dm persistent-data components: block manager, transaction manager, space map, disk bitset, btree, and array.
- A writeset is a disk bitset plus an in-core bitset cache of blocks written in the current era.
- The writeset tree maps era number to archived writeset metadata.
- The era array maps data block number to the most recent era known after archived writesets are digested.

## Metadata Lifecycle
- `metadata_open()` creates persistent-data objects, formatting an all-zero metadata device when allowed or opening an existing superblock.
- `metadata_resize()` reallocates the two in-core writesets and resizes the era array when the target size changes.
- `metadata_era_rollover()` archives the current writeset if present, creates a fresh disk bitset in the alternate writeset slot, atomically swaps the current writeset pointer with RCU, and increments the era.
- `metadata_commit()` flushes the current bitset, pre-commits the transaction manager, saves the space-map root, rewrites the superblock, and commits.
- `metadata_take_snap()` rolls over, commits, shadows the superblock, and increments roots so userspace can inspect a stable metadata snapshot.
- `metadata_drop_snap()` deletes the snapshot’s cloned writeset tree and era array and drops the cloned superblock reference.

## Digest Process
- Archived writesets are digested incrementally by `struct digest`.
- `metadata_digest_lookup_writeset()` finds the lowest-era archived writeset.
- `metadata_digest_transcribe_writeset()` scans up to 100 bits per step and writes matching blocks’ era values into the era array.
- `metadata_digest_remove_writeset()` removes the archived writeset after transcription.
- The incremental coroutine avoids long metadata stalls in the worker thread.

## IO Path
- Constructor syntax is `<metadata dev> <data dev> <data block size (sectors)>`.
- Block size must be positive and a multiple of `MIN_BLOCK_SIZE` sectors.
- `dm_set_target_max_io_len()` limits bios to one era block.
- `era_map()` remaps all bios to the origin device. Non-flush writes whose block is not yet marked in the current writeset are deferred to the worker; other bios pass through.
- The worker marks deferred writes in the on-disk current writeset, commits if any new bit was set, updates the in-core bitset only after successful commit, and submits or errors the queued bios.

## Worker and RPC Model
- A single ordered workqueue serializes digest work, deferred write marking, and RPC metadata operations.
- Messages are implemented as RPCs to the worker: `checkpoint`, `take_metadata_snap`, and `drop_metadata_snap`.
- `postsuspend` archives the current era and then stops/flushed the worker.
- `preresume` resizes metadata if needed, starts the worker, and performs an era rollover.

## Status and Limits
- Info status reports metadata block size, used/total metadata blocks, current era, and held metadata snapshot block or `-`.
- Table status reports metadata device, origin device, and sectors per block.
- IO hints set optimal IO size to the era block size when existing stacked limits are incompatible.

## Important Invariants
- Current writeset pointer changes are synchronized with RCU so IO paths see either the old or new writeset safely.
- The in-core bitset is updated only after the corresponding on-disk bit and metadata commit succeed.
- A metadata snapshot must be unique; taking a second snapshot before dropping the first is rejected.
- `valid_nr_blocks()` keeps bit counts within both dm-bitset and `test_bit()` practical limits.

## Filesystem/Storage Relevance
`dm-era` is a block-level dirty-region history engine. It can support backup, replication, or userspace tracking tools that need to know which blocks changed between checkpoints without depending on filesystem internals.

## Notable Risks
- Several error paths are marked `FIXME: fail mode`; metadata write failures can currently stop progress or error deferred bios rather than entering a polished recovery mode.
- Digestion of old eras is asynchronous, so users of metadata snapshots must understand the difference between archived writesets and transcribed era-array state.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-era-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-exception-store.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-exception-store.c

## Role
Implements the registry and common constructor/destructor helpers for device-mapper snapshot exception stores. Exception stores manage COW metadata for persistent and transient snapshots.

## Registry Mechanics
- `_exception_store_types` is a global list protected by `_lock`.
- `dm_exception_store_type_register()` adds a named store type if not already present.
- `dm_exception_store_type_unregister()` removes an existing type.
- `get_type()` first searches loaded types, then tries to autoload `dm-exstore-<type_name>`, truncating at the last dash and retrying for compound type names.
- Store type references are protected with module reference counts via `try_module_get()` and `module_put()`.

## Store Creation
- `dm_exception_store_create()` expects at least two arguments: persistence selector and chunk size.
- The first argument must start with `P` for persistent or `N` for transient; remaining characters are passed as store-type options.
- The chunk size is parsed and validated through `dm_exception_store_set_chunk_size()`.
- The selected type constructor is called, and the helper returns the number of consumed arguments.

## Chunk Size Validation
- Chunk size 0 is accepted as an unset/special state.
- Nonzero chunk size must be a power of two.
- It must be a multiple of both origin and COW device logical block sizes.
- It must fit within `INT_MAX >> SECTOR_SHIFT`.

## Lifecycle
- `dm_exception_store_init()` registers transient and persistent store implementations.
- `dm_exception_store_exit()` unregisters persistent then transient implementations.
- `dm_exception_store_destroy()` invokes the store-specific destructor, drops the module reference, and frees the common wrapper.

## Filesystem/Storage Relevance
Snapshot exception stores are the metadata layer that records origin-to-COW chunk mappings for DM snapshots. They are central to copy-on-write snapshot correctness and merge behavior.

## Notable Risks
- Autoload depends on the `dm-exstore-*` module naming convention.
- Chunk size choices are constrained by both origin and COW block sizes; invalid sizing would break snapshot chunk addressing.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-exception-store.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-exception-store.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-exception-store.h

## Role
Declares the device-mapper snapshot exception-store API shared by the snapshot target and store implementations.

## Public Types
- `chunk_t` represents snapshot chunk numbers.
- `struct dm_exception` maps an `old_chunk` from the origin to a `new_chunk` in the COW device.
- `struct dm_exception_store_type` is the store implementation vtable.
- `struct dm_exception_store` is the common store instance wrapper with type pointer, owning snapshot, chunk geometry, implementation context, and userspace overflow support flag.

## Store Vtable
Store implementations provide:
- `ctr` and `dtr` lifecycle methods.
- `read_metadata()` to load COW metadata and report exceptions through a callback.
- `prepare_exception()` and `commit_exception()` for allocating and committing new COW chunks.
- `prepare_merge()` and `commit_merge()` for snapshot merge progress.
- `drop_snapshot()` to invalidate metadata.
- `status()` and `usage()` reporting hooks.

## Chunk Helpers
- The high 8 bits of `new_chunk` can encode a count of consecutive following chunks when `chunk_t` is 64-bit.
- `dm_chunk_number()`, `dm_consecutive_chunk_count()`, and increment/decrement helpers manipulate that packed representation.
- `sector_to_chunk()` converts sectors to chunk numbers using the store’s `chunk_shift`.

## Exposed Functions
Declares type register/unregister, chunk-size setup, store create/destroy, global store init/exit, and the two built-in store implementation init/exit pairs.

## Filesystem/Storage Relevance
This header defines the abstraction that lets DM snapshots use different COW metadata formats while presenting the same copy-on-write and merge semantics to upper block/filesystem layers.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-exception-store.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-flakey.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-flakey.c

## Role
Implements the `flakey` device-mapper test target, which alternates between up and down intervals and can fail, drop, or corrupt IO during the down interval.

## Target Interface
- Constructor syntax is `<dev_path> <offset> <up interval> <down interval> [<#feature args> [<arg>]*]`.
- Intervals are seconds measured from target construction time using jiffies.
- Optional features are `drop_writes`, `error_writes`, and `corrupt_bio_byte <Nth_byte> <r|w> <value> <bio_flags>`.
- `drop_writes` and `error_writes` are mutually exclusive and cannot be combined with write corruption.

## IO Behavior
- During up intervals, bios are remapped normally to the lower device and start offset.
- During down intervals:
  - Plain reads are killed unless a feature path maps them for later corruption or write-handling semantics.
  - Writes can be silently ended (`drop_writes`), completed with error (`error_writes`), corrupted before submission, or killed by default.
  - Reads submitted during the down interval can be corrupted in `flakey_end_io()` after successful lower-device completion.
- Zone management operations bypass flakey failure logic and are remapped.

## Corruption Logic
- `corrupt_bio_data()` overwrites the configured 1-based byte offset in the bio payload with an 8-bit value.
- Optional `bio_flags` require all configured flags to be present before corruption.
- Direction controls whether corruption happens before lower-device write submission or after read completion.

## Status and Device Helpers
- Table status reconstructs the lower device, offset, intervals, and feature list.
- `prepare_ioctl()` passes ioctls through only when the target covers the whole lower device with zero offset.
- Zoned devices support `report_zones` by remapping the requested sector through the target offset.

## Important Invariants
- Per-bio data records whether a bio was submitted during a down interval so `end_io` only mutates eligible reads.
- Up/down interval sum must be nonzero and must not overflow.
- Feature parser tracks duplicate/conflicting options explicitly.

## Filesystem/Storage Relevance
`dm-flakey` is a broad failure-injection target for testing filesystem and storage-stack behavior under intermittent device failure, lost writes, write errors, and data corruption.

## Notable Risks
- Dropped writes are completed successfully, intentionally modeling dangerous storage behavior.
- Corruption is byte-offset based inside bio segments and does not understand filesystem or sector structure.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-flakey.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ima.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ima.c

## Role
Implements IMA measurement support for device-mapper. It serializes DM device/table metadata into key-value strings, measures them through `ima_measure_critical_data()`, and stores hashes tying later device events to measured table state.

## Serialization Helpers
- `fix_separator_chars()` escapes backslash, semicolon, equals, and comma characters in names/UUIDs so key-value lists remain parseable.
- `dm_ima_alloc()` optionally wraps allocations in `memalloc_noio_save()` for no-IO contexts.
- `dm_ima_alloc_and_copy_name_uuid()` copies and escapes mapped-device name and UUID.
- `dm_ima_alloc_and_copy_device_data()` builds common device metadata: name, UUID, major, minor, minor count, and target count.
- `dm_ima_alloc_and_copy_capacity_str()` records current disk capacity.

## Table Load Measurement
- `dm_ima_measure_on_table_load()` builds one or more `dm_table_load` IMA records.
- Each record starts with `DM_IMA_VERSION_STR` and device metadata, then appends per-target metadata: index, begin sector, length, and target-specific `STATUSTYPE_IMA` status.
- If the measurement buffer would overflow, the current buffer is measured and hashed, then a new record starts again with device metadata.
- A SHA-256 hash over the measured table-load buffers is stored as the inactive table hash.
- Inactive table device metadata and target count are also saved on the mapped device.

## Device Event Measurements
- `dm_ima_measure_on_device_resume()` optionally swaps inactive table metadata/hash into the active table, then measures active table metadata, active table hash, and capacity. If no table data exists, it records name/UUID with `device_resume=no_data`.
- `dm_ima_measure_on_device_remove()` measures active/inactive table metadata and hashes, `remove_all`, and capacity, then frees all stored IMA table state and resets the structure.
- `dm_ima_measure_on_table_clear()` measures inactive table data or a no-data record, capacity, and optionally repoints inactive state to active state for a new map.
- `dm_ima_measure_on_device_rename()` updates active device metadata after rename and measures old metadata plus new name/UUID and capacity.

## Important Invariants
- Stored active/inactive metadata pointers may alias; free paths check pointer identity to avoid double-free.
- Target-specific IMA data comes from each target’s `status(..., STATUSTYPE_IMA, ...)` hook and is best-effort.
- Measurements include the DM version string prefix from `dm_ima_reset_data()`.
- Table-load hash uses the same buffers submitted to IMA, allowing later events to refer to an already measured table.

## Filesystem/Storage Relevance
This file adds measured-boot/attestation visibility for DM device configuration. For encrypted, verified, or stacked storage, it lets integrity policy observe not only device nodes but also the DM table attributes that define the block device seen by filesystems.

## Notable Risks
- Measurement is best-effort; allocation, crypto setup, or target status failures can skip or truncate measurement paths.
- Fixed-size buffers require chunking table-load measurements and careful no-data fallback paths.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ima.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ima.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ima.h

## Role
Declares device-mapper IMA measurement constants, stored metadata structures, and measurement hooks.

## Constants
- Defines buffer sizes for full measurements, device metadata, target metadata, target data, and capacity strings.
- Uses `sha256` as `DM_IMA_TABLE_HASH_ALG`.
- Builds `DM_IMA_VERSION_STR` from `DM_VERSION_MAJOR`, `DM_VERSION_MINOR`, and `DM_VERSION_PATCHLEVEL`.

## Data Structures
- `struct dm_ima_device_table_metadata` stores serialized device metadata, target count, and the hash string for one table state.
- `struct dm_ima_measurements` stores active and inactive table metadata plus cached DM version string length.

## API Surface
When `CONFIG_IMA` is enabled, declares reset, table-load, resume, remove, table-clear, and rename measurement functions. When disabled, all hooks are static no-ops.

## Filesystem/Storage Relevance
The header is the integration point that lets DM core call IMA measurement hooks without making IMA support mandatory.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ima.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-init.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-init.c

## Role
Implements early-boot creation of mapped devices from the `dm-mod.create=` kernel/module parameter.

## Input Format
- Top-level format is `<name>,<uuid>,<minor>,<flags>,<table>[,<table>+][;<device>...]`.
- Each table entry is `<start_sector> <num_sectors> <target_type> <target_args>`.
- Maximums are 256 devices, 256 targets per device, and a 4096-byte input string.

## Parser Flow
- `dm_init_init()` duplicates the `create` string, parses devices, waits for device probing, then calls `dm_early_create()` for each parsed device.
- `dm_parse_devices()` splits device entries on semicolons and allocates `struct dm_device` records.
- `dm_parse_device_entry()` splits name, UUID, minor, flags, and table; `ro` sets read-only and `rw` is accepted as writable.
- `dm_parse_table()` loops comma-separated table entries.
- `dm_parse_table_entry()` parses start, length, target type, and target args, allocates a `dm_target_spec`, validates the target type, and stores a duplicated argument string.
- `dm_setup_cleanup()` frees all allocated specs, argument strings, and device records.

## Safety and Scope
- Allowed early-boot targets are restricted to `crypt`, `delay`, `linear`, `snapshot-origin`, `striped`, and `verity`.
- `str_field_delimit()` trims leading/trailing whitespace but explicitly does not support escaped separator characters.
- Supplying a minor number sets `DM_PERSISTENT_DEV_FLAG`.

## Important Invariants
- The parameter string must fit within `DM_MAX_STR_SIZE`; oversized input is rejected before parsing.
- Each parsed table target must be one of the allowlisted target types.
- Target args are copied with `kstrndup()` before the temporary parse string is freed.

## Filesystem/Storage Relevance
This file enables initramfs-less or early userspace storage stacks, such as encrypted or verified root devices, to be configured directly by the kernel command line before normal userspace tooling is available.

## Notable Risks
- The grammar is intentionally simple and lacks escaped separators, so names, UUIDs, and target args must avoid unescaped delimiters in this early-boot path.
- Creation stops at the first `dm_early_create()` failure, but the parser returns the parse result rather than per-device create status.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-init.c -->