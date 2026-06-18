# Group Research: group_1738_spdk_sources_virtualization_spdk_lib_fsdev_fsdev_c_sources_virtuali_c27ae7728468

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/virtualization/spdk`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev.c -->
# File Research: sources/virtualization/spdk/lib/fsdev/fsdev.c

## Purpose
Implements SPDK's deprecated `fsdev` core registry and lifecycle layer. It manages filesystem-device modules, registered devices, names, descriptors, IO channels, shared channel resources, per-thread IO caches, and hot-remove/unregister flows.

## Main Responsibilities
- Maintains global `g_fsdev_mgr` with a mempool for `spdk_fsdev_io`, registered modules, registered fsdevs, an RB tree of names, initialization state, and a spinlock.
- Initializes and finishes the fsdev subsystem through `spdk_fsdev_initialize()` and `spdk_fsdev_finish()`.
- Registers JSON config emission via `spdk_fsdev_subsystem_config_json()`.
- Creates management channels with pre-populated per-thread `spdk_fsdev_io` caches to reduce mempool contention.
- Creates per-fsdev IO channels and deduplicates module shared resources per management channel.
- Registers/unregisters fsdevs, sends `fsdev_register` and `fsdev_unregister` notifications, and defers remove callbacks to descriptor owner threads.
- Opens and closes descriptors with SPDK-thread affinity and descriptor reference tracking.
- Submits fsdev IO to module `submit_request()` implementations, tracks outstanding counts, and completes user callbacks on the right thread.

## Key Data Structures
- `struct spdk_fsdev_mgr`: global subsystem state.
- `struct spdk_fsdev_mgmt_channel`: per-thread IO cache and shared resource list.
- `struct spdk_fsdev_shared_resource`: shared module channel plus outstanding IO and refcount.
- `struct spdk_fsdev_channel`: per-fsdev channel with submitted IO queue and outstanding count.
- `struct spdk_fsdev_desc`: open descriptor with event callback, owning thread, refs, and closed flag.

## Important Behavior
- `SPDK_LOG_DEPRECATION_REGISTER()` marks fsdev as being replaced in `v26.09`.
- Options are versioned by `opts_size`; `spdk_fsdev_set_opts()` enforces a minimum IO pool size based on cache size and SPDK thread count.
- `fsdev_io_complete()` defers completion if called inside module `submit_request()` to avoid recursive callback-driven IO submission.
- Unregister transitions through `UNREGISTERING` then `REMOVING`; open descriptors receive `SPDK_FSDEV_EVENT_REMOVE` asynchronously before final io_device unregister/destruct.
- `spdk_fsdev_unregister_by_name()` opens the device temporarily to verify module ownership before unregistering.

## Dependencies
Uses SPDK thread/io_device, mempool, notify, JSON, queue/RB-tree, spinlock, logging, and `spdk/fsdev_module.h` module callbacks.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev_internal.h -->
# File Research: sources/virtualization/spdk/lib/fsdev/fsdev_internal.h

## Purpose
Small internal header for fsdev implementation files.

## Contents
- Declares `fsdev_io_submit(struct spdk_fsdev_io *fsdev_io)`.
- Declares `fsdev_channel_get_io(struct spdk_fsdev_channel *channel)`.
- Defines `__io_ch_to_fsdev_ch(io_ch)` as an SPDK IO-channel context cast to `struct spdk_fsdev_channel`.

## Dependencies
Includes `spdk/thread.h`; relies on fsdev structs declared in public/internal fsdev headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev_io.c -->
# File Research: sources/virtualization/spdk/lib/fsdev/fsdev_io.c

## Purpose
Implements public fsdev operation wrappers. Each API allocates and fills an `spdk_fsdev_io`, sets operation-specific input fields, submits it to the fsdev module, adapts module completion to a typed user callback, and frees temporary resources.

## Operation Pattern
- `fsdev_io_get_and_fill()` obtains an IO from the channel cache/mempool and initializes common fields: fsdev, channel, descriptor, type, unique ID, user callback, internal callback, default `-ENOSYS` status, and submit flag.
- Each `spdk_fsdev_*()` function fills `u_in.<operation>` and calls `fsdev_io_submit()`.
- Each `_spdk_fsdev_*_cb()` pulls results from `u_out.<operation>`, invokes the typed user callback via `CALL_USR_CLB` or `CALL_USR_NO_STATUS_CLB`, releases any strdup/malloc data, and returns the IO to the pool.

## Covered Operations
Implements wrappers for mount, umount, lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rmdir, rename, link, open, read, write, statfs, release, fsync, xattr set/get/list/remove, flush, opendir, readdir, releasedir, fsyncdir, flock, create, abort, fallocate, and copy-file-range.

## Resource Ownership
- Copies string inputs for path/name/xattr fields using `strdup()` and releases them in completion callbacks.
- Copies xattr values into owned malloc memory for `setxattr`.
- Read/write buffers and iovecs are caller-owned and passed through.
- `readlink` expects module output `linkname` to be heap-owned and frees it after callback.
- `readdir` uses a module entry callback shim to invoke the user entry callback for each output entry.

## Notes
There is a likely typo in `spdk_fsdev_symlink()`: after `u_in.symlink.linkpath = strdup(linkpath)`, the failure check tests `if (!fsdev_io)` instead of `if (!fsdev_io->u_in.symlink.linkpath)`. That would miss allocation failure and then dereference/free through a bad state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev_io.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev_rpc.c -->
# File Research: sources/virtualization/spdk/lib/fsdev/fsdev_rpc.c

## Purpose
Provides runtime JSON-RPC handlers for fsdev subsystem options.

## RPCs
- `fsdev_get_opts`: takes no params, calls `spdk_fsdev_get_opts()`, and returns `fsdev_io_pool_size` plus `fsdev_io_cache_size`.
- `fsdev_set_opts`: decodes optional `fsdev_io_pool_size` and `fsdev_io_cache_size`, starts from current options, updates them, and calls `spdk_fsdev_set_opts()`.

## Dependencies
Uses SPDK JSON-RPC, logging, `spdk/fsdev.h`, and generated `rpc_fsdev_set_opts_ctx` from `spdk_internal/rpc_autogen.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fsdev/fsdev_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/Makefile -->
# File Research: sources/virtualization/spdk/lib/ftl/Makefile

## Purpose
Build definition for SPDK `ftl` library.

## Key Build Settings
- Sets `SPDK_ROOT_DIR`, includes `mk/spdk.common.mk`, and declares `LIBNAME = ftl`.
- Shared object version is `SO_VER := 11`, `SO_MINOR := 0`.
- Optional compile defines:
  - `SPDK_FTL_RETRY_ON_ERROR`
  - `SPDK_FTL_L2P_FLAT`
  - `SPDK_FTL_ZONE_EMU_BLOCKS=<value>`
- Adds `-I.` to local includes.

## Source Coverage
Builds core FTL files, management files, utilities, upgrade handlers, NV-cache implementations, and base-device implementations. Includes `ftl_trace.c` only for `CONFIG_DEBUG=y`.

## Clean Behavior
Adds manual clean targets for `mngt`, `utils`, and `upgrade` subdirectories before including `mk/spdk.lib.mk`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/base/ftl_base_bdev.c -->
# File Research: sources/virtualization/spdk/lib/ftl/base/ftl_base_bdev.c

## Purpose
Defines the standard base block-device type for FTL and its metadata layout operations.

## Behavior
- `is_bdev_compatible()` requires 4096-byte blocks, no separate metadata, and a write unit size of either 1 or a power of two no larger than 256 blocks.
- `md_region_setup()` initializes an `ftl_layout_region` on the base bdev with no VSS metadata.
- `md_region_create()` aligns metadata regions and reserves them through `ftl_layout_tracker_bdev_add_region()`, with data-base alignment chosen for valid-map buffer alignment.
- `md_region_open()` finds a matching region version and fills region offset, blocks, entry size, and entry count.

## Registration
Declares `base_bdev` with name `base_bdev` and registers it with `FTL_BASE_DEVICE_TYPE_REGISTER(base_bdev)`.

## Dependencies
Uses `ftl_core.h`, `ftl_layout.h`, `ftl_band.h`, and `utils/ftl_layout_tracker_bdev.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/base/ftl_base_bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.c -->
# File Research: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.c

## Purpose
Maintains the global registry of FTL base device types.

## Behavior
- Stores registered `ftl_base_device_type` entries in a global TAILQ protected by `g_devs_mutex`.
- Validates that a type has a non-empty name.
- Rejects duplicate names with an error and `ftl_abort()`.
- `ftl_base_device_get_type_by_bdev()` iterates registered types and returns the first whose `is_bdev_compatible()` callback accepts the bdev.

## Dependencies
Uses SPDK queue/logging, pthread mutexes, `ftl_core.h`, `ftl_base_dev.h`, and `utils/ftl_defs.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.h -->
# File Research: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.h

## Purpose
Declares the plugin interface for FTL base-device types.

## Key Types
- `struct ftl_base_device_ops`: compatibility callback plus `ftl_md_layout_ops`.
- `struct ftl_base_device_type`: name, ops, and TAILQ entry.

## API
- `FTL_BASE_DEVICE_TYPE_REGISTER(desc)` registers a base device type through a constructor.
- `ftl_base_device_register()` adds a descriptor to the registry.
- `ftl_base_device_get_type_by_bdev()` selects a registered type for an SPDK bdev.

## Dependencies
Includes SPDK stdinc, bdev module APIs, queues, and `ftl_layout.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_band.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_band.c

## Purpose
Implements FTL band metadata, address math, P2L map allocation/lifetime, state transitions, valid-block accounting, and garbage-collection candidate selection.

## Main Behavior
- Computes tail metadata placement and detects when a band's user area is full.
- Transitions bands among free, prep, opening, open, full, closing, and closed states.
- Allocates P2L map buffers from durable-format-aware mempools and frees them only when refcounts reach zero.
- Acquires P2L checkpoint regions for active writes and records checkpoint region type in band metadata.
- Converts between physical `ftl_addr`, band ID, and band-relative block offset.
- Tracks valid entries through `p2l_map.num_valid` and global `valid_map`.
- Calculates band invalidity as `1 - valid/user_blocks`.

## GC Selection
- Closed, non-relocating bands are eligible.
- Physical-band groups are scored by average invalidity, then write count, then physical ID.
- Supports a high-priority GC band ID from shared superblock state.
- Persists/resets GC iterator state depending on create mode, clean shutdown, fast startup, or fast recovery.

## Startup Helpers
- `ftl_valid_map_load_state()` reconstructs each band's valid count from its valid bitmap.
- `ftl_bands_load_state()` validates band metadata versions and restores free bands to the runtime free list.

## Dependencies
Uses FTL core/layout/debug/internal APIs, CRC utilities, FTL mempools, bitmap helpers, and P2L checkpoint APIs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_band.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_band.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_band.h

## Purpose
Defines FTL band states, metadata format, runtime band structure, and band-level APIs.

## Key Definitions
- `FTL_MAX_OPEN_BANDS` equals `FTL_LAYOUT_REGION_TYPE_P2L_COUNT`.
- Current band metadata version is `FTL_BAND_VERSION_2`.
- `enum ftl_band_state` covers free, prep, opening, open, full, closing, closed.
- `struct ftl_band_md` is packed to exactly one 4096-byte FTL block and stores iterator, state, type, P2L checkpoint region, sequence IDs, write count, durable P2L map object ID, and P2L map CRC.
- `struct ftl_band` stores runtime owner callbacks/refcount, P2L map, relocation flag, band IDs, addresses, metadata request, list entry, and persist callback context.

## API Surface
Declares helpers for address conversion, P2L map acquire/open/release, state/type changes, write prep, GC selection, metadata reads, band open/close/free, request read/write operations, and owner management.

## Dependencies
Includes SPDK bit array, queues, CRC, FTL IO/internal/core, and durable-format helpers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_band.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_band_ops.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_band_ops.c

## Purpose
Implements band-level asynchronous IO operations and metadata persistence for opening, closing, freeing, and reading relocation metadata.

## IO Paths
- `ftl_band_rq_write()` writes an internal multi-block relocation/compaction request to the base bdev at the band iterator, advances the iterator, and may mark the band full.
- `ftl_band_rq_read()` reads relocation request entries from the base bdev.
- `ftl_band_basic_rq_write()` and `ftl_band_basic_rq_read()` handle simpler metadata read/write operations, including P2L tail metadata.
- `-ENOMEM` submit failures are queued with SPDK bdev IO wait; other failures abort unless retry mode is enabled.

## Metadata Transitions
- `ftl_band_open()` persists band metadata with state `OPEN`.
- `ftl_band_close()` writes the tail P2L map, computes CRC, persists metadata with state `CLOSED`, and then transitions through the band state machine.
- `ftl_band_free()` persists metadata with state `FREE`, clears close sequence and P2L checksum, then releases P2L resources.
- Tail metadata reads verify P2L CRC before handing a band to GC.

## GC Entry
`ftl_band_get_next_gc()` selects a relocation band, sets owner callbacks, and reads its tail P2L map before invoking the caller.

## Dependencies
Uses SPDK bdev module APIs, FTL request structures, FTL metadata persistence, CRC, and band/core helpers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_band_ops.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_core.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_core.c

## Purpose
Implements public FTL IO entry points, core poller processing, read/trim flow, free-band selection, global init/fini buffers, and FTL statistics.

## Public IO
- `spdk_ftl_io_size()` returns `sizeof(struct ftl_io)`.
- `spdk_ftl_writev()` and `spdk_ftl_readv()` validate iovecs/LBA counts, require initialized devices, initialize `ftl_io`, and enqueue to the IO channel submission ring.
- `spdk_ftl_unmap()` validates ranges and alignment; aligned unmaps use FTL trim, unaligned user unmaps complete as NOPs.
- `spdk_ftl_get_io_channel()` wraps `spdk_get_io_channel(dev)`.

## Read Path
- Pins L2P pages before reading.
- Groups contiguous LBAs only when they map contiguously within the same storage tier, base or NV cache.
- Invalid/unwritten LBAs are zero-filled.
- On completion, pinned reads verify L2P mappings still match the read addresses; stale reads are retried via `-EAGAIN`.

## Trim Path
- Acquires a trim sequence ID from NV cache.
- Records trim progress in shared superblock state.
- Updates trim bitmap, trim metadata, and trim log, then persists trim log and trim metadata.
- Supports retry behavior under `SPDK_FTL_RETRY_ON_ERROR`.

## Core Poller
`ftl_core_poller()` processes submitted IOs, runs user and GC writers, relocation, NV-cache processing, and L2P processing. During halt it waits for inflight IO, writers, relocation, NV cache, bands, and L2P to become quiescent.

## Statistics
Tracks bdev read/write blocks and errors by stats type; supports async stats retrieval from the FTL core thread.

## Dependencies
Uses SPDK bdev/thread/NVMe status APIs, FTL band/IO/debug/internal/mngt/NV-cache/writer/reloc/L2P modules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_core.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_core.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_core.h

## Purpose
Defines the central `struct spdk_ftl_dev` runtime object and core helper APIs.

## Device State
`struct spdk_ftl_dev` contains configuration, layout, superblocks, IO-channel list, base device descriptor/type, NV cache, mempools, statistics, bands, free/shut lists, L2P state, valid/trim maps, writers, relocation, core thread/poller, queues, P2L checkpoint lists, layout trackers, and configurable properties.

## Key Constants
- `P2L_MEMPOOL_SIZE` reserves P2L buffers for open/close and relocation.
- `FTL_ZERO_BUFFER_SIZE` defines a 1 MiB DMA buffer used to avoid NULL metadata-buffer problems on some devices.

## Inline Helpers
Provides band count/block count, core-thread checks, FTL address packing and NV-cache address conversion, sequence ID allocation, P2L/tail metadata sizing, and fast-startup/fast-recovery predicates based on clean flags and shared-memory readiness.

## API
Declares limit application, address invalidation, pollers, relocation threshold checks, free-band selection, trim map updates, max sequence recovery, stats helpers, and trim entry point.

## Dependencies
Includes SPDK uuid/thread/bdev/ftl and most internal FTL headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_core.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_debug.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_debug.c

## Purpose
Provides debug-only band metadata validation and always-available device stats dumping.

## Debug Build Behavior
- `ftl_band_validate_md()` allocates a validation context, walks band P2L entries in chunks of 128 LBAs, pins matching L2P pages, and checks whether valid band P2L entries agree with current L2P mappings unless the current mapping is invalid or in NV cache.
- `ftl_dev_dump_bands()` logs valid-block counts, user-block counts, write counts, and state for all bands.

## Non-Debug Behavior
The header supplies asynchronous no-op validation in non-debug builds to preserve callback timing.

## Stats Dump
`ftl_dev_dump_stats()` logs device UUID, total valid LBAs, total writes, user writes, and write amplification factor; debug builds also log free-band limit counters.

## Dependencies
Uses `spdk/ftl.h`, `ftl_debug.h`, `ftl_band.h`, L2P pinning, bitmap checks, and FTL logging.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_debug.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_debug.h

## Purpose
Declares and conditionally stubs FTL debug helpers.

## Contents
- In `DEBUG`, declares `ftl_band_validate_md()` and `ftl_dev_dump_bands()`.
- In non-debug builds, implements `ftl_band_validate_md()` as an asynchronous success callback on the core thread and `ftl_dev_dump_bands()` as no-op.
- `ftl_debug_inject_trim_error()` aborts after 256 trims when `FTL_CRASH_ON_TRIM` is set in debug builds; otherwise no-op.
- Always declares `ftl_dev_dump_stats()`.

## Dependencies
Includes FTL internal, band, and core headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_init.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_init.c

## Purpose
Implements FTL device allocation, startup, shutdown, and core-thread setup.

## Startup
- `allocate_dev()` allocates `spdk_ftl_dev`, initializes properties and config, creates or selects the core thread, initializes IO queues, and initializes user/GC writers.
- `spdk_ftl_dev_init()` creates callback context, allocates the device, and starts the management startup sequence via `ftl_mngt_call_dev_startup()`.
- `dev_init_cb()` handles startup retry when `dev->init_retry` is set, otherwise reports final status and frees failed devices.

## Shutdown
- `spdk_ftl_dev_free()` calls management shutdown via `ftl_mngt_call_dev_shutdown()`.
- `dev_free_cb()` frees the device on successful shutdown and invokes the user callback.
- `free_dev()` tears down the core thread when it was created from `core_mask`, deinitializes config/properties, and frees memory.

## Core Thread
If `conf.core_mask` is set, a named `ftl_core_thread` is created on the parsed cpuset; otherwise the current SPDK thread is used.

## Dependencies
Uses SPDK thread/cpuset/bdev/config APIs, FTL core/IO/band/debug/NV-cache/writer/utils, and management startup/shutdown.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_init.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_internal.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_internal.h

## Purpose
Defines shared internal constants, address types, P2L map structures, trim log format, and cross-module internal prototypes for FTL.

## Key Constants And Types
- `FTL_ADDR_INVALID`, `FTL_LBA_INVALID`, and `FTL_BLOCK_SIZE` of 4096 bytes.
- P2L and P2L-log metadata version constants.
- `typedef uint64_t ftl_addr`, where addresses below base size point to base bdev and higher addresses point into NV cache.
- `enum ftl_md_type`, `enum ftl_band_type`, and `enum ftl_md_status`.

## Metadata Structures
- `struct ftl_p2l_map_entry`: LBA plus sequence ID.
- `struct ftl_p2l_map`: valid count, refcount, valid bitmap, runtime map pointer, DMA metadata entry pointer, and checkpoint reference.
- `struct ftl_p2l_ckpt_page` and `_no_vss` describe persisted P2L checkpoint page formats.
- `struct ftl_trim_log` is exactly one FTL block and stores trim VSS header plus padding.

## API Groups
Declares P2L checkpoint lifecycle/restore/persist APIs, relocation lifecycle, P2L log lifecycle/flush/acquire/release/read APIs, and management helpers.

## Dependencies
Includes SPDK stdinc/CRC/util/uuid/ftl plus FTL bitmap and metadata utility headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_io.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_io.c

## Purpose
Implements generic FTL user-IO descriptor helpers.

## Behavior
- Tracks inflight request counts with `ftl_io_inc_req()` and `ftl_io_dec_req()`.
- Provides LBA and iovec cursor helpers.
- `ftl_iovec_num_blocks()` validates block-size alignment and computes block count.
- `ftl_io_init()` zeroes and initializes an `ftl_io`, sets callback/user context, LBA, iovecs, type, invalid initial address, and trace ID.
- `ftl_io_complete()` clears initialized state, verifies/unpins L2P for pinned IO, and sends completion into the IO-channel completion ring.
- `ftl_io_cb()` handles error/retry logic; `-EAGAIN` reschedules reads, writes, or trims to the appropriate device queue.
- `ftl_io_fail()` marks a status and advances to completion.
- `ftl_io_clear()` resets cursor, status, flags, done state, and band pointer for retry.

## Important Safety Behavior
Pinned non-write IO verifies that current L2P entries still match the addresses read. If not, it converts completion to `-EAGAIN` so stale data is not returned.

## Dependencies
Uses FTL core, band, debug, L2P, mempool, trace, and SPDK rings through channel state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_io.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_io.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_io.h

## Purpose
Defines FTL user IO, internal relocation request, basic metadata request, IO channel, and helper APIs.

## Key Types
- `struct ftl_io_channel`: device pointer, channel list entry, map pool, poller, submission ring, completion ring.
- `struct ftl_io`: user IO descriptor with LBA, physical address, iovec cursor, metadata, status, request count, callback, flags, type, trace ID, queue entry, NV-cache chunk, L2P pin context, mapping array, and bdev wait entry.
- `struct ftl_rq_entry`: one block of an internal relocation/compaction request with payload, metadata, address, LBA, sequence ID, owner, band IO info, L2P pin context, and bdev IO info.
- `struct ftl_rq`: variable-length internal request with owner callbacks, iterator state, IO state, and entries.
- `struct ftl_basic_rq`: simpler metadata IO request for P2L map and related reads/writes.

## Helpers
Defines request-entry loop macros, basic request initialization/owner setters, `ftl_rq_from_entry()`, and `ftl_io_done()`.

## Dependencies
Includes SPDK stdinc/NVMe/ftl/bdev/util and FTL internal/trace/L2P/metadata headers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_io.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p.c

## Purpose
Dispatches L2P operations to either the flat or cached backend and implements shared L2P update semantics.

## Backend Selection
Uses compile-time macro `SPDK_FTL_L2P_FLAT`:
- Defined: routes `FTL_L2P_OP(name)` to `ftl_l2p_flat_name`.
- Default: routes to `ftl_l2p_cache_name`.

## Common API
Initializes deferred pin list, wraps pin/unpin/set/get/clear/restore/persist/trim/process/halt/resume, and completes/defer pins through `ftl_l2p_pin_complete()`.

## Update Semantics
- `ftl_l2p_update_cache()` handles user writes to NV cache. It resolves write-after-write races by chunk sequence ID or address ordering within the same chunk, ignores writes older than trim metadata, updates NV-cache P2L/valid state before L2P, then invalidates old address.
- `ftl_l2p_update_base()` handles GC/compaction writes to base. It updates base band valid state and L2P only if current L2P still matches the expected old address; otherwise it invalidates the new relocated address. Old address is invalidated afterward.

## Dependencies
Uses FTL band, NV cache, cached L2P, flat L2P, trim metadata, and core-thread assertions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p.h

## Purpose
Declares the L2P mapping abstraction used by FTL core, writers, GC, and recovery.

## API
- Lifecycle: `ftl_l2p_init()`, `ftl_l2p_deinit()`.
- Pinning: `ftl_l2p_pin()`, `ftl_l2p_unpin()`, `ftl_l2p_pin_skip()`, `ftl_l2p_pin_complete()`.
- Mapping: `ftl_l2p_set()`, `ftl_l2p_get()`.
- Metadata operations: clear, trim, restore, persist, process.
- Flow control: halt, resume, is_halted.
- Update helpers: `ftl_l2p_update_cache()` and `ftl_l2p_update_base()`.

## Key Type
`struct ftl_l2p_pin_ctx` stores requested LBA/count, completion callback, callback context, and queue link for deferred pins.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.c

## Purpose
Implements the paged/cached L2P backend for large devices with a bounded DRAM resident set.

## Data Model
- L2P is split into 4 KiB pages.
- `l2_mapping` maps L2P page number to durable-format object ID for resident page context.
- Resident pages are allocated from `l2_ctx_pool`, backed by `l1_md` buffers, and tracked with state, update count, pin count, waiters, LRU membership, checkpoint sequence, and IO context.
- Page sets group pin requests that span up to `L2P_MAX_PAGES_TO_PIN` pages.
- Cache state tracks running/shutdown, in-flight IOs, resident/available/evicting pages, deferred page sets, lazy trim work, and management process context.

## Initialization
Creates metadata objects for L2 mapping, page contexts, and resident page buffers. Computes resident-page cap from `conf.l2p_dram_limit`, initializes LRU/deferred lists, restores shared-memory state for fast startup/recovery, and caches the L2P layout bdev/offset/ioch.

## Pin/Get/Set
- Pin requests either pin resident ready pages, queue waiters on pages being loaded, or defer page sets until memory is available.
- Page-in reads one L2P page from metadata storage and wakes queued waiters.
- `get` and `set` require pinned pages, lazily apply trim invalidation if the trim bit is set, promote the page in LRU, and `set` increments page updates.

## Eviction And Persistence
- Eviction chooses cold unpinned ready pages while maintaining a reserve of available pages.
- Dirty pages are written back; clean pages are removed.
- `persist` walks all pages, writes dirty residents, applies trim invalidation, and removes pages.
- `trim` allocates/loads trimmed pages, invalidates entries, writes them out, and clears trim bits.
- `clear` uses metadata clear to initialize persistent L2P to invalid addresses.

## Shutdown
`halt` moves to shutdown and completes only when no page IO and no evictions remain. `process` handles deferred pin page-ins, eviction, and lazy trim while running.

## Dependencies
Uses SPDK bdev IO wait, thread/event/env utilities, FTL core/layout/NV-cache IO/mngt steps, address utilities, mempools, metadata, trim map, and stats.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.h

## Purpose
Declares the cached L2P backend API and metadata object names.

## Contents
- Metadata names: `l2p_l1`, `l2p_l2`, and `l2p_l2_ctx`.
- Declares cached backend functions for init/deinit, pin/unpin, get/set, trim, clear, restore, persist, process, halt/resume, and halt-state query.

## Dependencies
Relies on types from FTL core/L2P headers included by callers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.c

## Purpose
Implements the simple flat in-memory L2P backend, backed directly by the L2P metadata buffer.

## Behavior
- `ftl_l2p_flat_init()` allocates a small backend object and points `l2p_flat->l2p` at the L2P metadata buffer.
- `set` and `get` store/load packed FTL addresses using `ftl_addr_store()` and `ftl_addr_load()`.
- `pin` and `unpin` only assert range validity; all entries are already resident.
- `clear` fills the buffer with `FTL_ADDR_INVALID` and persists metadata.
- `restore` and `persist` forward to `ftl_md_restore()`/`ftl_md_persist()`.
- `trim`, `process`, `halt`, and `resume` are no-ops; `is_halted()` always returns true.

## Dependencies
Uses FTL L2P/core/band/utils/flat header and address packing utilities.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.h

## Purpose
Declares the flat L2P backend API.

## API
Provides init/deinit, pin/unpin, get/set, trim, clear, restore, persist, process, halt-state, halt, and resume functions matching the backend dispatch layer in `ftl_l2p.c`.

## Dependencies
Relies on `struct spdk_ftl_dev`, `struct ftl_l2p_pin_ctx`, `ftl_l2p_cb`, and `ftl_addr` declarations from included callers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_l2p_flat.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_layout.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_layout.c

## Purpose
Computes, creates, loads, validates, dumps, stores, and upgrades FTL metadata/data layout regions across NV cache and base bdev.

## Region Sizing
- Superblock region size is aligned to base bdev write unit size and at least `FTL_SUPERBLOCK_SIZE`.
- Metadata region byte/block helpers align to superblock region size.
- Region names are mapped from `enum ftl_layout_region_type`.

## Setup Modes
`ftl_layout_setup()` chooses:
- `NO_RESTRICT` for create mode: creates a fresh default layout.
- `LEGACY_DEFAULT` when the superblock blob area is empty: recreates pre-v5 static layout assumptions.
- `LOAD_CURRENT` when a blob layout exists: loads and applies stored layout.

## Default Layout
- NV cache: L2P, band metadata plus mirror, P2L checkpoints, trim metadata plus mirror, trim log plus mirror, NV-cache metadata plus mirror, and NV-cache data via type-specific setup.
- Base bdev: data region and valid map.
- Superblock setup creates primary superblock on NV cache and mirror on base.

## Legacy Layout
Reopens regions using legacy versions and sizes, verifies only one matching version exists, restores legacy NV-cache chunk count, and adds placeholders for trim log regions during upgrade.

## Validation And Introspection
- `ftl_validate_regions()` rejects overlapping active regions on the same bdev.
- `ftl_layout_dump()` logs regions grouped by NV cache and base device.
- `ftl_layout_base_md_blocks()` estimates base metadata footprint for valid map and superblock.

## Blob Support
`ftl_layout_blob_store()` serializes region type, entry size, and entry count. `ftl_layout_blob_load()` validates blob size/type and restores those fields. `ftl_layout_upgrade_add_region_placeholder()` marks missing upgrade regions as placeholders.

## Dependencies
Uses SPDK bdev APIs, FTL core/utils/band/layout/NV-cache/superblock, NV-cache device ops, bdev layout tracker, and layout upgrade helpers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_layout.c -->