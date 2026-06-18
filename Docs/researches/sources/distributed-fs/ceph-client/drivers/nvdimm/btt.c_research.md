# sources/distributed-fs/ceph-client/drivers/nvdimm/btt.c

## Purpose
`btt.c` implements the Block Translation Table runtime for NVDIMM namespaces. It discovers or creates on-media BTT arenas, exposes the resulting translated namespace as a Linux block disk, and provides sector-level power-fail atomicity by writing data to reserved free blocks before atomically updating per-LBA map metadata. The code sits below the `nd_btt` device wrapper and above the namespace byte accessors supplied by `claim.c`.

## Important APIs, Types, And Functions
The primary external entry points are `nvdimm_namespace_attach_btt()` and `nvdimm_namespace_detach_btt()`, exported for the BTT personality driver. `btt_init()` constructs a `struct btt` from an `nd_btt`, raw namespace size, LBA size, namespace UUID, and parent region. `btt_fini()` tears down the gendisk, arenas, and debugfs state. The block device operations are `btt_submit_bio()` and `btt_getgeo()`.

Arena metadata helpers include `btt_info_read()`, `btt_info_write()`, `discover_arenas()`, `create_arenas()`, `btt_arena_write_layout()`, and `btt_meta_init()`. Map/log helpers include `btt_map_read()`, `btt_map_write()`, `btt_log_read()`, `btt_flog_write()`, `log_set_indices()`, `btt_freelist_init()`, `btt_rtt_init()`, and `btt_maplocks_init()`. I/O is split through `btt_read_pg()`, `btt_write_pg()`, `btt_do_bvec()`, `btt_data_read()`, `btt_data_write()`, and optional `btt_rw_integrity()`.

The file uses `struct btt` and `struct arena_info` from `btt.h`, `struct nd_btt` and `struct nd_region` from `nd.h`, and namespace byte APIs `nvdimm_read_bytes()` / `nvdimm_write_bytes()` through the `nd_namespace_common`.

## Control Flow
Attach begins in `nvdimm_namespace_attach_btt()`: it validates that UUID, namespace, and LBA size are configured, enables the namespace with `devm_namespace_enable()`, resolves BTT version/initial offset with `nd_btt_version()`, checks minimum raw size, and calls `btt_init()`. `btt_init()` initializes in-memory state, discovers existing arenas, or creates and writes new arena metadata when no existing layout is present and the region is writable. It then allocates a block disk, sets capacity, applies region read-only state, and initializes debugfs.

Existing arena discovery reads the first info block at each arena offset. A valid BTT superblock is parsed into `arena_info`, log padding layout is detected with `log_set_indices()`, the freelist is reconstructed from the latest log entries, and RTT/map-lock arrays are allocated. If no valid metadata is found at offset zero, the instance transitions to create mode. Create mode slices the namespace into arenas up to `ARENA_MAX_SIZE`, calculates data/map/log/info offsets, initializes map and log areas, writes duplicated info blocks, and marks `INIT_READY`.

BIO submission iterates each segment and rejects segments that are larger than a page, smaller than the BTT sector size, or not sector aligned. Reads map a premap LBA to a postmap block, publish the postmap in the read tracking table, re-read the map to detect races with writes, then copy persistent data or zero-fill trimmed entries. Writes acquire a per-region lane, choose that lane's free block, wait while any RTT entry references it, write data and integrity metadata to the free block, lock the map stripe, write a log transaction with old/new map entries, then update the map. The old postmap becomes the lane's next free block.

## State And Persistence Behavior
BTT persistence is held in each arena's primary and backup `struct btt_sb`, zero-initialized map table, lane log groups, and data area. The two-phase write sequence is: write new data to a free internal block, persist a log entry that records old and new map state, then persist the map update. On startup `btt_freelist_init()` replays incomplete transactions when a log entry says a map should have moved but the map still points to the old block.

Map entries encode trim and error bits in the top two bits. BTT treats all-zero maps as initial identity mapping and `MAP_ENT_NORMAL` as a normal initialized entry. Media read errors trigger persistent error tracking by setting the map error flag. Free-list entries with error state are zero-written by `arena_clear_freelist_error()` before reuse. The read tracking table is volatile state that prevents a writer from reusing a free block while a read may still be consuming it.

Version state is stored on `nd_btt`: v1.1 uses a 4 KiB initial offset, while v2.0 starts at zero. The file writes BTT metadata only when no valid metadata exists, so already formatted namespaces are reopened by discovery rather than reformatted.

## Dependencies And Integration Points
This file integrates with the block layer (`gendisk`, queue limits, bio accounting, optional integrity metadata), libnvdimm namespace byte accessors, badblock tracking through `is_bad_pmem()`, region lane allocation through `nd_region_acquire_lane()` / `nd_region_release_lane()`, debugfs, and the BTT device wrapper in `btt_devs.c`.

`nvdimm_namespace_attach_btt()` relies on `claim.c` for `devm_namespace_enable()` and on `btt_devs.c` for version validation. The block disk name comes from `nvdimm_namespace_disk_name()` in `namespace_devs.c`. Region read-only state is synchronized through `nvdimm_check_and_set_ro()` in `bus.c`.

## Risks And Edge Cases
The power-fail protocol depends on correct atomicity assumptions for 8-byte halves of 16-byte log entries and durable namespace writes. Misordered writes or incorrect `NVDIMM_IO_ATOMIC` handling would affect recovery. `log_set_indices()` supports legacy and fixed padding layouts; unknown padding schemes fail arena discovery. `lba_to_arena()` is a linear scan, acceptable for few arenas but a scaling risk for very large namespace layouts.

Concurrency is subtle: reads rely on RTT publication and a compiler barrier, while writes spin waiting for RTT entries before reusing free blocks. Incorrect lane management or map lock indexing can produce stale reads or double allocation. Error clearing currently logs failures and has a FIXME noting BTT should become read-only if clearing fails during init. Segment alignment rejection in `btt_submit_bio()` is a functional test point for callers.

## Test Signals
Useful tests include formatting a fresh namespace and verifying `btt_meta_init()` writes valid duplicated superblocks, reopening an existing namespace and checking log replay, inducing incomplete flog/map transactions, validating both old `(0,2)` and new `(0,1)` log padding schemes, exercising badblock/error flag persistence, read-after-write under concurrent lanes, discard/trim zero-fill behavior via map flags, and read-only region attach failure when metadata is absent. Block tests should verify capacity, disk read-only propagation, integrity metadata sizes for 520/528/4104/4160/4224-byte LBAs, and bio alignment errors.
