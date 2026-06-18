# sources/distributed-fs/ceph-client/fs/btrfs/bio.c

## Purpose
`bio.c` is the Btrfs logical I/O submission and completion layer. It wraps Linux block `bio`s in `struct btrfs_bio`, maps logical ranges to physical devices and RAID profiles, splits I/O at mapping or zone-append boundaries, performs or schedules checksum generation and verification, handles mirrored/RAID56 write completion, performs data read repair, and owns the biosets/mempool used by normal, cloned, and repair bios.

## Important APIs, types, and functions
- `btrfs_bio_init()` and `btrfs_bio_alloc()` initialize/allocate high-level Btrfs bios.
- `btrfs_bio_end_io()` merges completion status from split/cloned bios, waits for async checksum work when needed, releases ordered extents, and invokes the caller end-io callback once all pending pieces finish.
- `btrfs_submit_bbio()` is the main submit entry point; it loops through `btrfs_submit_chunk()` until the whole logical bio is mapped/submitted.
- `btrfs_submit_chunk()` maps a logical range with `btrfs_map_block()`, performs splitting, preloads read checksums, attaches write checksum work, handles zone append constraints, and dispatches to the physical submit path.
- `btrfs_submit_bio()` selects single-device, RAID56, or mirrored-write submission.
- `btrfs_submit_dev_bio()` validates the target device, rewrites zone-append bios, tracks stats, and calls `submit_bio()` or `blkcg_punt_bio_submit()`.
- `btrfs_check_read_bio()`, `repair_one_sector()`, `btrfs_end_repair_bio()`, `btrfs_repair_io_failure()`, and `btrfs_submit_repair_write()` implement checksum/error-based read repair and targeted repair writes.
- `run_one_async_start()`, `run_one_async_done()`, `should_async_write()`, and `btrfs_wq_submit_bio()` offload expensive checksum generation before write submission.
- End-io handlers `btrfs_simple_end_io()`, `btrfs_raid56_end_io()`, `btrfs_orig_write_end_io()`, and `btrfs_clone_write_end_io()` normalize device/RAID completion into Btrfs completion semantics.
- `btrfs_bioset_init()` and `btrfs_bioset_exit()` manage normal, clone, repair, and failed-bio allocation pools.

## Control flow
Submitters allocate or initialize a `btrfs_bio`, fill the embedded Linux `bio`, and call `btrfs_submit_bbio()`. The entry point asserts alignment, then repeatedly calls `btrfs_submit_chunk()`. Each chunk maps the current logical sector and length to a `btrfs_io_context` or single stripe. If the returned mapping is shorter than the remaining bio, `btrfs_split_bio()` clones the front portion, increments the original `pending_ios`, advances file and checksum offsets, and submits the split first.

For data reads, `btrfs_submit_chunk()` saves the original iterator and preloads checksums with `btrfs_lookup_bio_sums()`. For writes, it records the original logical address for fscrypt checksum generation, tracks ordered-extents that use RAID stripe tree metadata, decides whether checksums are needed, and either queues async checksum work or computes checksums synchronously. NODATASUM, remap, data-relocation, zoned, and zone-append cases take alternate checksum/dummy-sum paths. Successful chunks are passed to `btrfs_submit_bio()`.

Physical submission has three branches. Single-stripe I/O sets `mirror_num`, physical sector, device private data, and `btrfs_simple_end_io()`. RAID56 routes through parity recovery/write helpers and `btrfs_raid56_end_io()`. Mirrored writes clone the bio for all but the last stripe; clones use `btrfs_clone_write_end_io()` to update shared error state and end the original, while the original uses `btrfs_orig_write_end_io()` to apply `max_errors` tolerance before completing the high-level bbio.

Completion always returns to task context before the caller callback. Simple completions queue `simple_end_io_work()` on metadata or data endio workers. Reads of data inodes call `btrfs_check_read_bio()`, which verifies checksums block by block and starts repair reads for failed sectors. Repair reads try alternate mirrors; on success, they call `btrfs_repair_io_failure()` to synchronously rewrite bad mirrors. If repair fails on all mirrors, the original bbio gets `BLK_STS_IOERR`. Non-read or metadata paths call `btrfs_bio_end_io()` directly after optional zoned physical recording.

`btrfs_bio_end_io()` is the convergence point for split bios. Clone bios that were never submitted or are completing drop their ordered extent refs and `bio_put()` themselves, then update the original status via `cmpxchg()` so the first error wins. The original callback runs only when `pending_ios` reaches zero, and ordered extents are released after the submitter's end-io callback runs.

## State and persistence behavior
Persistent on-disk changes are indirect: submitted writes eventually update device blocks, repair writes correct bad mirrors, and write checksum generation attaches checksum state to ordered extents for later metadata insertion. Runtime state includes static biosets, the repair failed-bio mempool, per-bbio pending counts, mirror number, first error status, read checksum buffers, ordered extent refs, RAID stripe context refs, async checksum work, and saved iterators.

Device error counters are updated for read, write, flush, and repair-write failures. Filesystem I/O counters block device replace/removal races while mapped I/O or repair I/O is active. Zone append writes may have their physical sector rewritten to the zone start for submission and recorded back to ordered state on success.

## Dependencies and integration points
The file integrates Linux block-layer bios, biosets, blkcg punt submission, Btrfs volume mapping, RAID56 parity helpers, device stats, ordered extents, checksum lookup/generation/verification, fscrypt checksum handling, zoned allocation, RAID stripe tree metadata, device replace, scrub, data relocation roots, and async-thread workers. It is the common lower I/O path for data and metadata callers that submit through `btrfs_submit_bbio()`.

## Risks and test signals
Important risks include incorrect split accounting, first-error propagation races, ordered extent reference leaks, checksum buffer lifetime, async checksum completion ordering, zone append boundary alignment, device-missing/writeability checks, mirrored write tolerance thresholds, RAID56 completion context, and repair reads that accidentally loop back to the failed mirror. Repair writes deliberately bypass normal mirrored submission, so mapping and mirror-number correctness are critical.

Test signals include aligned and deliberately misaligned debug builds, reads with valid and invalid checksums, single-copy read failure, mirrored read repair success/failure, repair write to a bad mirror, RAID1/RAID10 mirrored write partial failures under `max_errors`, RAID56 read/write paths, split bios at chunk boundaries, NODATASUM and remap writes, async checksum enabled/disabled by sync flags and fast checksum flags, fscrypt write checksums, zoned sequential zone append, scrub repair writes with and without device replace, missing/non-writeable devices, cgroup punt submission, and bioset init failure unwinding.
