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
