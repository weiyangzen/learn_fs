# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vdo.c

## Purpose
`vdo.c` is the in-memory lifecycle and operating core for a VDO instance. It initializes the global VDO registry, constructs and tears down VDO objects, configures work queues and thread IDs, formats first-use devices, loads/saves geometry and component superblocks, coordinates read-only and recovery transitions, exposes statistics, and provides thread-affinity assertions used by the rest of dm-vdo.

## Important APIs, Types, and Functions
Key internal types include `sync_completion`, used to run a completion callback on a VDO work queue and wait from a caller thread, and `device_registry`, a small rwlock-protected list of live VDO instances. Public entry points include `vdo_initialize_device_registry_once()`, `vdo_find_matching()`, `vdo_make_thread()`, `vdo_make()`, `vdo_destroy()`, `vdo_load_super_block()`, `vdo_save_components()`, `vdo_enable_read_only_entry()`, `vdo_enter_read_only_mode()`, `vdo_set_compressing()`, `vdo_fetch_statistics()`, and `vdo_get_physical_zone()`.

## Control Flow
Creation starts in `vdo_make()`, which allocates a `struct vdo`, calls `initialize_vdo()`, assigns a thread-name prefix, allocates `vdo_thread` records, and constructs admin, flusher, packer, data-vio pool, I/O submitter, optional bio-ack queue, and CPU queues. `initialize_vdo()` reads the geometry block; a zeroed geometry block triggers `vdo_format()`, otherwise the geometry is decoded. Formatting creates a UUID/nonce, initializes geometry and component states, and marks `needs_formatting`. Destruction reverses construction through `finish_vdo()`, registry removal, component frees, listener frees, thread config cleanup, compression-context cleanup, and final object free.

## State and Persistence Behavior
Persistent layout state is represented by the geometry block and superblock. `record_vdo()` snapshots volatile component state into `vdo->states`; `vdo_save_super_block()` encodes it and writes it with preflush/FUA. Geometry saves are similarly encoded and written at `VDO_GEOMETRY_BLOCK_LOCATION`. A superblock write failure marks the superblock `unwritable` to avoid later persistence that could make recovery semantics inconsistent. `vdo_set_state()` and `vdo_get_state()` use atomic state plus explicit memory barriers.

## Dependencies and Integration Points
This file is the coordinator for most dm-vdo subsystems: block map, recovery journal, slab depot, logical/physical/hash zones, dedupe, packer, flusher, io-submitter, VIO metadata I/O, admin state, encodings, and statistics. It integrates with Linux block APIs for zeroout and flushes, device-mapper target naming, dm-kcopyd for layout copy support, work queues via `funnel-workqueue`, and LZ4 compression contexts for CPU queue work.

## Risks and Test Signals
Risk concentrates around lifecycle unwinding, thread-affinity assumptions, read-only transition races, and persistence ordering. Important tests should cover fresh format vs existing geometry load, partial construction failure cleanup, superblock write failure making the device read-only/unwritable, suspend/resume read-only notification gating, compression toggling from non-packer context, statistics consistency, and invalid physical block lookup paths. Fault injection around metadata reads/writes and flush errors is especially valuable.
