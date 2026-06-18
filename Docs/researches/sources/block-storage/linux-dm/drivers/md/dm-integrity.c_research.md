# File Research: sources/block-storage/linux-dm/drivers/md/dm-integrity.c

## Purpose
Implements the Device Mapper `integrity` target. It stores and verifies per-block integrity tags either supplied through block-integrity payloads or generated internally with a hash/MAC. It supports direct writes, journaled writes, bitmap write tracking, recovery mode, optional metadata device separation, journal encryption/MAC, discard handling, and background tag recalculation.

## Main Interfaces
- Target lifecycle: `dm_integrity_ctr()`, `dm_integrity_dtr()`, `dm_integrity_postsuspend()`, `dm_integrity_resume()`.
- I/O path: `dm_integrity_map()`, `dm_integrity_map_continue()`, `integrity_end_io()`, `integrity_metadata()`.
- Journal handling: `write_journal()`, `replay_journal()`, `do_journal_write()`, `init_journal()`, `__journal_read_write()`.
- Metadata/tag access: `get_metadata_sector_and_offset()`, `dm_integrity_rw_tag()`, `integrity_sector_checksum()`.
- Bitmap/recalculation: `block_bitmap_op()`, `bitmap_block_work()`, `bitmap_flush_work()`, `integrity_recalc()`.
- Reporting and limits: `dm_integrity_status()`, `dm_integrity_iterate_devices()`, `dm_integrity_io_hints()`.

## Control Flow
Construction parses the target line `<dev> <start> <tag_size|-> <mode> <feature args>`, opens the data and optional metadata devices, reads or initializes the superblock, computes journal/metadata geometry, creates workqueues, dm-io and dm-bufio clients, optional crypto transforms, journal memory, bitmap state, and recalculation buffers.

`dm_integrity_map()` validates bounds, block alignment, integrity-payload size, mode restrictions, flush/FUA semantics, and maps the logical sector to data and metadata locations. Flushes are deferred to commit handling. Normal I/O is passed to `dm_integrity_map_continue()`.

In journal mode, writes reserve journal entries under `endio_wait.lock`, copy data and tags into the in-memory journal, and later commit journal sections to disk. Reads first check whether a newer block exists in the journal tree and can be served from the journal. A writer workqueue later copies committed journal entries to the data device and persists tags.

In direct and bitmap modes, bios go to the data device while tag verification or tag writes happen through metadata work. Reads with internal hashes and discards may be forced through synchronous offloaded paths so metadata checks or updates happen after the underlying bio completes.

Background recalculation scans data, reads blocks, computes tags, writes metadata, and advances `sb->recalc_sector`. Bitmap mode uses on-disk bitmap blocks in the journal area to remember regions needing recalculation or delayed write permission, then flushes and clears bitmap state when safe.

## State And Synchronization
`struct dm_integrity_c` owns target geometry, devices, dm-io/dm-bufio clients, superblock, journal page lists, crypto state, tag hash/MAC specs, workqueues, journal ring positions, range locks, bitmap pages, recalculation buffers, flush lists, timers, and failure/mismatch counters.

`endio_wait.lock` protects overlapping in-progress ranges, waiters, flush lists, and journal allocation state. An rb-tree tracks active ranges to prevent overlapping metadata/data updates. A second rb-tree maps logical sectors to journal entries. Workqueues separate metadata hashing, waiting/offload, commit, writer, and recalc work. Failure is latched in `ic->failed` and propagated to later bios.

## Integration Points
Uses Device Mapper target hooks, `dm_io` for synchronous/asynchronous metadata and journal I/O, `dm_bufio` for tag blocks, Linux crypto shash/skcipher APIs for internal hashes and journal protection, block-integrity registration when tags are externally supplied, audit logging for MAC/checksum failures, and reboot notifiers to force synchronous bitmap flushing before shutdown.

## Notable Behaviors
- Modes are `J` journaled, `B` bitmap, `D` direct, and `R` recovery/read-only style mode.
- `internal_hash` disables external integrity payloads and generates tags from sector number plus data.
- `journal_crypt` can use full skcipher operation or precomputed XOR stream for byte-granular ciphers.
- `journal_mac` protects journal section metadata; `fix_hmac` adds salt and fixed HMAC behavior in newer superblock versions.
- Recalculation with keyed HMAC is blocked unless `legacy_recalculate` is specified, because regenerating tags can weaken authenticity assumptions.
- FUA writes are completed only after the target’s required metadata/journal flush path runs.
- Discards are only allowed with internal hashes and mark tags with a discard filler.
- Bitmap mode sets `SB_FLAG_DIRTY_BITMAP` on resume and clears it during clean suspend after flushing.

## Risks And Review Focus
- Journal commit ordering is durability-critical: entries must not be exposed as committed before copied data, tags, MACs, and flushes are ordered correctly.
- The range rb-tree and wait-list logic is central to avoiding overlapping journal replay, recalc, discard, and normal I/O races.
- Superblock version/flag compatibility affects padding, MAC behavior, separate metadata devices, bitmap state, and recalculation.
- Tag comparison allows discard filler as a special case; review paths that mix discard, internal hashes, and partial tag comparisons carefully.
- Error latching means one failed metadata, crypto, MAC, or I/O path changes behavior for all later bios.
