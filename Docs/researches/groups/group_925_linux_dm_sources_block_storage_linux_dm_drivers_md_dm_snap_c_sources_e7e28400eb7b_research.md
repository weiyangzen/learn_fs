# Group Research: group_925_linux_dm_sources_block_storage_linux_dm_drivers_md_dm_snap_c_sources_e7e28400eb7b

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/linux-dm`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-snap.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-snap.c

## Purpose
Implements the device-mapper snapshot family: `snapshot`, `snapshot-origin`, and `snapshot-merge`. It manages copy-on-write exception tables, origin-to-snapshot registration, snapshot metadata loading/commit through exception stores, snapshot merge-back into the origin, and COW-triggering for origin writes.

## Main Objects
- `struct dm_snapshot`: per snapshot/merge target state, including origin/COW devices, exception tables, exception store, pending exception mempool, merge state, tracked read chunks, and queued merge-overlap bios.
- `struct dm_exception_table`: hash table for completed or pending exceptions.
- `struct dm_snap_pending_exception`: in-flight COW work, queued origin/snapshot bios, kcopyd sequencing, and full-chunk write fast path.
- `struct origin`: global origin-device entry with ordered list of snapshots.
- `struct dm_origin`: per `snapshot-origin` target context.

## Public/Exported Surface
- Exports `dm_snap_origin()` and `dm_snap_cow()` for access to snapshot devices.
- Registers three target types:
  - `snapshot`
  - `snapshot-origin`
  - `snapshot-merge`
- Module parameters:
  - `snapshot_cow_threshold`
  - kcopyd throttle parameter via `DECLARE_DM_KCOPYD_THROTTLE_WITH_MODULE_PARM`.

## Control Flow
- `dm_snapshot_init()` initializes exception-store infrastructure, origin hash tables, slab caches, and registers all three targets.
- `snapshot_ctr()` parses `<origin_dev> <COW-dev> <p|po|n> <chunk-size> [features]`, opens devices, creates the exception store, allocates exception hash tables, creates the kcopyd client and pending exception mempool, registers the snapshot under its origin, and reads metadata unless exception-table handover will happen later.
- `snapshot_resume()` performs exception handover for same-COW table reloads, suspending/resuming the origin mapped device if needed, then marks the snapshot active.
- `snapshot_map()` handles normal snapshot I/O:
  - flushes go to COW,
  - invalid or overflowed snapshots reject writes,
  - reads without an exception go to origin and are tracked,
  - reads/writes with completed exceptions remap to COW,
  - writes create or join pending exceptions, dispatching kcopyd or full-bio copy paths.
- `origin_map()` remaps origin I/O linearly, but writes call `do_origin()` so all active snapshots get required exceptions before the origin write proceeds.
- `snapshot_merge_map()` combines snapshot and origin semantics: reads use exceptions when present, writes may queue if they overlap actively merging chunks, and otherwise origin writes create exceptions in other snapshots.
- `snapshot_merge_next_chunks()` repeatedly asks the exception store for merge ranges, ensures other snapshots have exceptions for the origin extent, waits for conflicting tracked I/O, copies COW data back to origin, flushes, commits the merge, and removes merged exceptions.
- `snapshot_dtr()` stops merge if needed, unregisters the snapshot, waits for pending exceptions, destroys exception tables, mempool, exception store, bio, and devices.

## Data Structures and Algorithms
- Origin devices are hashed globally in `_origins`, with snapshots sorted by descending chunk size.
- Completed exceptions support coalescing consecutive chunks using `DM_CHUNK_CONSECUTIVE_BITS`.
- Pending exceptions are keyed separately and do not coalesce.
- Completion order is serialized by `exception_sequence` and an RB tree of out-of-order completions.
- Read tracking uses `dm_per_bio_data()` and a small chunk hash so merge and COW completion can wait for conflicting reads before overwriting origin/COW state.
- Snapshot reload handover swaps completed exception tables and exception stores between old and new targets sharing the same COW device.

## Dependencies
- Core DM target APIs from `dm.h` and `device-mapper.h`.
- Exception-store interface from `dm-exception-store.h`.
- kcopyd for chunk copy, zero, and callback sequencing.
- Bio remapping/submission, mempools, slab caches, hlist bitlocks, rwsems, spinlocks, wait queues, RB trees.

## Notable Behaviors
- `discard_zeroes_cow` allows discards to zero completed COW chunks rather than issue discard.
- `discard_passdown_origin` depends on `discard_zeroes_cow` and can pass discard to origin without triggering snapshot exceptions.
- Persistent overflow can either invalidate the snapshot or set `snapshot_overflowed` when userspace supports overflow reporting.
- Merge failure leaves the target usable as a normal snapshot/origin path where possible, but reports `"Merge failed"`.

## Risk and Test Focus
- Race-sensitive paths: pending exception allocation/insertion, completion table insertion, read tracking, and merge overlap queuing.
- Error paths should be tested for exception-store failures, COW full/overflow, kcopyd read/write errors, and merge commit failures.
- Snapshot reload and exception handover are delicate because metadata may only be loaded into one table at a time.
- `snapshot_dtr()` busy-waits on pending exceptions; pending-count leaks or callback loss would hang teardown.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-snap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-stats.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-stats.c

## Purpose
Implements per-mapped-device I/O statistics regions controlled by DM messages. It records reads/writes, sectors, merges, service time, in-flight I/O, queue time, optional precise timestamps, and optional latency histograms.

## Main Objects
- `struct dm_stat_percpu`: per-CPU counters for one region entry.
- `struct dm_stat_shared`: shared in-flight counters, timestamp, and temporary totals.
- `struct dm_stat`: one statistics region with ID, range, step, flags, histogram boundaries, program/aux strings, per-CPU arrays, and flexible shared entries.
- `struct dm_stats_last_position`: per-CPU last sector/RW used to infer merged I/O.

## Public Surface
- `dm_statistics_init()` / `dm_statistics_exit()`
- `dm_stats_init()` / `dm_stats_cleanup()`
- `dm_stats_message()`
- `dm_stats_account_io()`
- Module parameter `stats_current_allocated_bytes`.

## Control Flow
- `dm_stats_init()` initializes the stats list, mutex, and per-CPU last-position tracking.
- `dm_stats_message()` dispatches `@stats_*` commands:
  - `@stats_create`
  - `@stats_delete`
  - `@stats_clear`
  - `@stats_list`
  - `@stats_print`
  - `@stats_print_clear`
  - `@stats_set_aux`
- `message_stats_create()` parses a sector range, step or divisor, feature arguments, program ID, and auxiliary data, then calls `dm_stats_create()`.
- `dm_stats_create()` calculates entry counts, allocation sizes, checks memory caps, allocates shared/per-CPU/histogram storage, suspends the mapped device to start exactly, assigns the lowest available ID, and inserts the region using RCU list insertion.
- `dm_stats_account_io()` is called at I/O start/end, computes merge and precise-duration metadata, then walks all RCU-visible stat regions and updates overlapping entries.
- `dm_stats_print()` folds per-CPU counters into temporary shared totals, prints region-entry counters, optionally histogram buckets, and optionally clears by subtracting snapshots of totals.
- `dm_stats_delete()` removes a region with RCU protection and chooses synchronous or callback freeing depending on whether vmalloc-backed allocations are present.

## Data and Accounting Rules
- Memory usage is globally capped to avoid user-created regions exhausting RAM or vmalloc space.
- Region ranges are split into fixed `step` entries; one bio may update multiple entries.
- Precise mode uses nanoseconds from `ktime_get()`, while normal mode uses jiffies and converts on print.
- Histograms use sorted ascending boundaries; binary search assigns buckets.
- On 32-bit architectures local IRQs are disabled around counter updates to avoid torn 64-bit updates; on 64-bit preemption is disabled.

## Dependencies
- DM core mapped-device stats ownership.
- RCU lists/callbacks.
- Per-CPU allocation and CPU-local update primitives.
- Kernel memory/vmalloc accounting and NUMA-aware allocation.

## Notable Behaviors
- Stats creation suspends/resumes the mapped device after allocation to avoid in-flight ambiguity.
- Buffer overflow for `@stats_create` is pre-tested because leaking a created region ID would otherwise be possible.
- `@stats_list` can filter by `program_id`.
- `@stats_print_clear` clears by subtracting current folded totals rather than zeroing all CPU counters.

## Risk and Test Focus
- Allocation-size overflow checks are critical due to user-controlled region sizes and histogram counts.
- RCU/freeing paths must handle both kmalloc and vmalloc storage correctly.
- Clear/print races are intentionally approximate but should not corrupt counters.
- Histogram parsing rejects unsorted or malformed boundaries; malformed input coverage matters.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-stats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-stats.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-stats.h

## Purpose
Declares the device-mapper statistics API used by DM core code and implemented in `dm-stats.c`.

## Public Types
- `struct dm_stats`: owns the stats-region list, mutex, and per-CPU last-position tracking.
- `struct dm_stats_aux`: per-I/O auxiliary accounting state, currently merge flag and precise duration timestamp.
- Forward declaration of `struct mapped_device`.

## Public Functions
- Lifecycle:
  - `dm_statistics_init()`
  - `dm_statistics_exit()`
  - `dm_stats_init()`
  - `dm_stats_cleanup()`
- Message handling:
  - `dm_stats_message()`
- I/O accounting:
  - `dm_stats_account_io()`
- Helper:
  - `dm_stats_used()` returns whether any stats regions exist.

## Dependencies
- Kernel list/mutex/types headers.
- `sector_t` and block I/O direction conventions from kernel block types.

## Contract Notes
- `dm_stats_account_io()` requires callers to pass the same `dm_stats_aux` across I/O start/end if precise timing is used.
- `dm_stats_used()` only checks list emptiness; callers must use it in a context where list lifetime is valid.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-stats.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-stripe.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-stripe.c

## Purpose
Implements the `striped` DM target, mapping logical sectors across multiple underlying devices using fixed-size stripes.

## Main Objects
- `struct stripe`: one backing device, its physical start sector, and error counter.
- `struct stripe_c`: target context with stripe count, stripe width, chunk size, shift optimizations, event work, and flexible stripe array.

## Target Surface
Registers target:
- Name: `striped`
- Version: `{1, 6, 0}`
- Features: `DM_TARGET_PASSES_INTEGRITY | DM_TARGET_NOWAIT`
- Supports map, end_io, status, iterate_devices, io_hints, and DAX direct access/zero-page when enabled.

## Control Flow
- `stripe_ctr()` parses `<number of stripes> <chunk size> [<dev_path> <offset>]+`, validates divisibility of target length by stripe count and chunk size, opens each device, configures split length and multi-bio counts for flush/discard/secure erase/write-same/write-zeroes.
- `stripe_map_sector()` computes target stripe and per-device sector from a logical sector, using shifts when stripe count or chunk size is power-of-two.
- `stripe_map()` handles:
  - flush fan-out by `target_bio_nr`,
  - discard/secure erase/write zeroes/write same by remapping only the range that hits the selected stripe,
  - normal I/O by direct stripe-sector calculation.
- `stripe_end_io()` increments per-device error counters and schedules a table event until a threshold is reached.
- `stripe_dtr()` releases devices, flushes event work, and frees context.

## DAX Path
When `CONFIG_FS_DAX` is enabled:
- `stripe_dax_pgoff()` maps page offsets to the correct stripe device and page offset.
- `stripe_dax_direct_access()` and `stripe_dax_zero_page_range()` pass through to the selected DAX device.

## Dependencies
- DM target/device APIs.
- Block bio operations and queue limits.
- Optional DAX APIs.
- Workqueue event notification via `dm_table_event()`.

## Notable Behaviors
- `iterate_devices()` reports each stripe over `stripe_width`.
- `io_hints()` sets `io_min` to chunk size and `io_opt` to chunk size multiplied by number of stripes.
- Error status marks stripes as `A` or `D` based on error count.

## Risk and Test Focus
- Sector math differs for power-of-two and non-power-of-two parameters; both need coverage.
- Range-remapping operations must correctly return empty subranges for stripes not touched by a discard-like bio.
- Error accounting identifies devices by major:minor string; test stacked or aliased devices carefully.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-stripe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-switch.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-switch.c

## Purpose
Implements the `switch` DM target: a dynamic region-to-path mapper intended for many fixed-size regions where the mapping is arbitrary and cannot be compactly represented by a simple stripe target.

## Main Objects
- `struct switch_path`: backing DM device and starting offset.
- `struct switch_ctx`: target context with path list, region size, region count, bit-packing metadata, and packed `region_table`.
- `region_table_slot_t`: machine-word storage for multiple region table entries.

## Target Surface
Registers target:
- Name: `switch`
- Version: `{1, 1, 0}`
- Feature: `DM_TARGET_NOWAIT`
- Supports map, message, status, prepare_ioctl, and iterate_devices.

## Control Flow
- `switch_ctr()` parses `<num_paths> <region_size> <num_optional_args> [optional_args] [<dev_path> <offset>]+`.
- `alloc_region_table()` calculates:
  - number of regions from target length and region size,
  - bits needed per path number,
  - entries per machine-word slot,
  - vmalloc-backed packed table storage.
- `initialise_region_table()` fills the table round-robin across paths.
- `switch_map()` converts a bio sector to a region, reads the path number, remaps the bio to that path plus offset, and returns `DM_MAPIO_REMAPPED`.
- `switch_message()` accepts only `set_region_mappings`, serialized by a static mutex.
- `process_set_region_mappings()` parses compact hex mapping updates:
  - `<region>:<path>`
  - `:<path>` for next region
  - `R<cycle_length>,<num_write>` to repeat previous mapping cycles.

## Data Structure Details
- Region entries are bit-packed into `unsigned long` slots.
- Reads use `READ_ONCE()`; writes update a full slot without explicit map-side locking.
- If a non-atomic torn read produces an invalid path number, mapping falls back to path 0.

## Dependencies
- DM argument parsing helpers.
- `vmalloc` for large region tables.
- Block bio remapping.
- Fast table-based hex parsing.

## Notable Behaviors
- Discards use one target bio because sending UNMAP down any path is considered sufficient.
- `prepare_ioctl()` passes ioctls through to the path for sector 0 only if the target exactly covers the underlying device size from that offset.
- Status table output prints only path definitions, not the current region table contents.

## Risk and Test Focus
- Packed table writes are not transactional across concurrent map reads; invalid torn reads are mitigated only by fallback to path 0.
- Message parser is performance-oriented and strict; malformed repeat/cycle updates should be covered.
- Very large region/path counts rely on overflow checks in `alloc_region_table()`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-switch.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-sysfs.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-sysfs.c

## Purpose
Provides sysfs integration for mapped devices by creating a `dm` kobject under the disk device and registering common DM attributes.

## Main Objects
- `struct dm_sysfs_attr`: wraps a sysfs `attribute` with mapped-device show/store callbacks.
- `dm_ktype`: kobject type with DM sysfs ops, default attributes, and release callback.

## Attributes
Read-only:
- `name`
- `uuid`
- `suspended`
- `use_blk_mq`

Read/write:
- `rq_based_seq_io_merge_deadline`

The read/write attribute is declared here through the macro; its show/store functions are supplied through included DM request-queue code.

## Control Flow
- `dm_attr_show()` resolves `mapped_device` from the kobject, calls the attribute-specific show handler, and drops the reference.
- `dm_attr_store()` does the same for store handlers.
- `dm_attr_name_show()` and `dm_attr_uuid_show()` copy the mapped-device name/UUID and append a newline.
- `dm_attr_suspended_show()` reports `dm_suspended_md()`.
- `dm_attr_use_blk_mq_show()` always reports true for userspace compatibility.
- `dm_sysfs_init()` initializes and adds the `dm` kobject below the disk kobject.
- `dm_sysfs_exit()` drops the kobject and waits for release completion.

## Dependencies
- `dm-core.h` for mapped-device kobject/name/UUID/reference helpers.
- `dm-rq.h` for request-queue attribute functions.
- Linux sysfs/kobject APIs.

## Risk and Test Focus
- Correct reference acquisition through `dm_get_from_kobject()` is central to avoiding use-after-free in sysfs callbacks.
- `dm_sysfs_exit()` waits for release completion; teardown ordering must ensure no stale sysfs callbacks survive mapped-device destruction.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-table.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-table.c

## Purpose
Implements DM table creation, target loading, device acquisition, target lookup indexing, table type selection, queue-limit calculation, integrity/crypto propagation, and target suspend/resume dispatch.

## Main Responsibilities
- Allocate/destroy `struct dm_table`.
- Add target lines and call target constructors.
- Manage underlying devices used by targets.
- Build a btree-like index over target end sectors for fast bio lookup.
- Decide whether a table is bio-based, DAX bio-based, or request-based.
- Calculate stacked queue limits and feature flags.
- Register/verify integrity and inline crypto profiles.
- Dispatch target lifecycle hooks for suspend/resume.

## Control Flow
- `dm_table_create()` allocates a table, initializes the devices list, rounds target capacity to index-node size, and allocates target/high arrays.
- `dm_table_add_target()` validates table continuity, target singleton/immutable/writeability constraints, resolves target type, splits target arguments, calls `ctr`, and appends the target high sector.
- `dm_split_args()` destructively tokenizes constructor/message strings with backslash quoting.
- `dm_table_complete()` determines queue mode, builds the index, registers integrity, constructs inline crypto profile, and allocates mapped-device mempools.
- `dm_table_find_target()` uses the generated index to map a sector to the target covering it.
- `dm_calculate_queue_limits()` stacks limits from each target’s devices, validates mapped device areas, handles zoned constraints, and checks logical block alignment.
- `dm_table_set_restrictions()` applies final queue flags and limits to the mapped-device queue.
- `dm_table_resume_targets()` runs all `preresume` hooks first, aborting on failure, then runs all `resume` hooks.

## Device Management
- `dm_get_device()` accepts major:minor strings or paths, reuses existing table devices, upgrades open mode when necessary, and reference-counts each `dm_dev_internal`.
- `dm_put_device()` decrements table-device references and releases devices when the count reaches zero.
- `free_devices()` warns and cleans up any leaked target device references during table destruction.

## Queue Type Rules
- Mixed bio-based and request-based targets are rejected.
- Hybrid targets inherit the live device type when possible, otherwise default to bio-based.
- DAX bio-based mode is selected only if all targets/devices support DAX or there are no devices and the live table is already DAX bio-based.
- Request-based tables must have a single immutable target, no target-level I/O splitting, and request-stackable underlying whole devices.

## Queue Limits and Feature Propagation
- Stacks physical/logical block sizes, alignment, discard, zone, and related limits.
- Validates zoned model consistency and zone size compatibility.
- Enables or disables:
  - nowait
  - discard
  - secure erase
  - write cache/FUA
  - DAX and synchronous DAX
  - nonrotational
  - write same
  - write zeroes
  - stable writes
  - add_random
- Runs zoned queue restriction setup when the resulting queue is zoned.

## Integrity and Inline Crypto
- Integrity is registered when all targets pass integrity and all devices expose matching profiles, unless a target handles integrity itself.
- On resume, integrity is reverified and unregistered if profiles no longer match.
- With `CONFIG_BLK_INLINE_ENCRYPTION`, a DM crypto profile is built as the intersection of underlying capabilities and cannot remove capabilities already exposed by the mapped-device queue.

## Dependencies
- DM core mapped-device APIs.
- Target-type registry from `dm-target.c`.
- Block queue limit, integrity, crypto, DAX, blk-mq, and zoned APIs.
- Device lookup/open helpers.

## Risk and Test Focus
- Table-line continuity and constructor failure cleanup are critical for safe table load rejection.
- Device mode upgrade must not expose partially reopened devices.
- Queue-limit stacking for mixed devices, zoned devices, and target `io_hints` is high risk.
- Request-based table acceptance has strict invariants; regressions can break block-layer assumptions.
- Inline crypto profile updates intentionally disallow capability removal.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-table.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-target.c

## Purpose
Maintains the global registry of DM target types and provides the built-in `error` target.

## Target Registry
- `_targets`: global list of registered `struct target_type`.
- `_lock`: rwsem protecting target lookup, registration, iteration, and module refcount updates.

## Public Surface
- `dm_get_target_type()` looks up a target, requests module `dm-<name>` if missing, then retries lookup.
- `dm_put_target_type()` drops the module reference.
- `dm_target_iterate()` iterates registered target types under read lock.
- `dm_register_target()` adds a target type unless the name already exists.
- `dm_unregister_target()` removes a target type and BUGs if it is not registered.
- Exports `dm_register_target` and `dm_unregister_target`.

## Built-in Error Target
- Name: `error`
- Version: `{1, 5, 0}`
- Feature: `DM_TARGET_WILDCARD`
- Constructor sets `num_discard_bios = 1` so discards fail as I/O errors instead of unsupported operations.
- Bio and request mapping always return `DM_MAPIO_KILL`.
- DAX direct access returns `-EIO`.

## Control Flow
- `dm_target_init()` registers the built-in error target.
- `dm_target_exit()` unregisters it.
- Module autoload uses `request_module("dm-%s", name)`.

## Risk and Test Focus
- Registry operations rely on callers balancing `dm_get_target_type()` and `dm_put_target_type()`.
- Duplicate registrations return `-EEXIST`; unregistering an unknown target is fatal.
- Error target is the fallback for holes or deliberately failing table regions, so discard/request/DAX behavior should stay consistently failing.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.c

## Purpose
Implements the persistent metadata engine for DM thin provisioning. It manages the thin-pool superblock, metadata and data space maps, thin-device details, hierarchical mapping btrees, snapshots, metadata transactions, metadata snapshots for userspace, allocation, resize, and read-only/fail states.

## On-Disk Model
- Superblock at block 0, designed to fit within one 512-byte sector.
- Metadata space map.
- Data space map.
- Device-details btree: `thin_id -> disk_device_details`.
- Two-level mapping btree: `(thin_id, virtual_block) -> block_time`.
- `block_time` packs a data block in the high 40 bits and transaction time in the low 24 bits.
- Superblock stores mapping roots, details root, space-map roots, transaction ID, flags, block sizes, and optional held metadata snapshot root.

## Main Objects
- `struct dm_pool_metadata`: in-core pool state, block manager, space maps, transaction managers, btree descriptors, root lock, roots, transaction ID, thin-device list, reserve, flags, and pre-commit callback.
- `struct dm_thin_device`: open thin-device state, mapped block count, creation/snapshot times, change flags, and open count.
- `struct thin_disk_superblock`: packed on-disk superblock with checksum.
- `struct disk_device_details`: packed on-disk mapped-block and timestamp details.

## Superblock and Opening
- `sb_prepare_for_write()` writes block number and checksum.
- `sb_check()` validates block number, magic, and checksum.
- `dm_pool_metadata_open()` creates the metadata object, opens or formats persistent structures, begins a transaction, and calculates metadata reserve.
- Empty all-zero superblocks are formatted only when `format_device` is true; otherwise open fails with `-EPERM`.
- Unsupported incompat or compat-ro features reject writable access.

## Transactions
- `__begin_transaction()` rereads superblock roots, time, transaction ID, flags, and data block size.
- `__commit_transaction()` writes changed thin-device details, commits data space map, pre-commits transaction manager, saves space-map roots, updates superblock fields, and commits the transaction.
- `dm_pool_commit_metadata()` commits without itself marking the pool in service, then begins the next transaction.
- `dm_pool_abort_metadata()` records which open devices had uncommitted changes, destroys/reopens persistent objects from the last good superblock, and sets `fail_io` if rollback fails.
- Most mutating public APIs take `pmd_write_lock()`, which also marks the pool `in_service`; internal/core-only paths use `pmd_write_lock_in_core()`.

## Thin Devices and Snapshots
- `dm_pool_create_thin()` creates an empty bottom-level mapping tree, inserts it in the top-level tree, and creates device details.
- `dm_pool_create_snap()` clones an origin by incrementing the origin mapping-root reference, inserts the snapshot mapping root, increments pool time, and updates origin/snapshot details.
- Snapshot sharing is inferred by comparing mapping block time with `td->snapshotted_time`.
- `dm_pool_delete_thin_device()` removes device details and mapping root, but refuses deletion when the device has more than one open reference.

## Mapping APIs
- `dm_thin_find_block()` looks up one virtual block, optionally using the non-blocking transaction-manager clone when I/O must not be issued.
- `dm_thin_find_mapped_range()` finds the next contiguous mapped range with same sharing state and contiguous pool blocks.
- `dm_pool_alloc_data_block()` allocates a new data block from the data space map.
- `dm_thin_insert_block()` inserts or replaces a virtual-to-data block mapping and updates mapped-block count on new insert.
- `dm_thin_remove_block()` removes a single mapping.
- `dm_thin_remove_range()` removes mapped leaves over a range by temporarily removing the device’s mapping tree from the top-level btree, editing it, and reinserting the updated root.

## Metadata Snapshots
- `dm_pool_reserve_metadata_snap()` commits current metadata, shadows/copies the superblock, strips space-map roots from the copy, increments preserved btree roots, and records the held root in the live superblock.
- `dm_pool_release_metadata_snap()` clears the held root, deletes preserved mapping/details roots, and decrements the held superblock block.
- `dm_pool_get_metadata_snap()` reads the held root for userspace.

## Queries and Maintenance
- Free/total data and metadata block counts.
- Metadata free count subtracts reserved commit-overhead blocks.
- Highest mapped block and mapped block count.
- Shared-block check through data-space-map reference count.
- Data and metadata resize extend space maps only.
- Read-only/read-write toggles on the block manager.
- Metadata threshold callback registration.
- Immediate `needs_check` flag update in the superblock.
- Transaction-manager prefetch issuance.
- Pre-commit callback registration.

## Dependencies
- Persistent-data block manager, transaction manager, btree, disk space map, and metadata space map.
- Device-mapper block-device types and workqueue headers.
- Kernel locking via rwsem and list management.

## Notable Contract Observations
- The header says opening the same thin device more than once fails with `-EBUSY`, but `__open_device()` increments `open_count` for existing non-create opens. Callers may rely on higher-level single-open discipline.
- The resize comment says shrinking may return `-ENOSPC` if allocated blocks would be lost, but implementation rejects all shrink attempts with `-EINVAL`.
- `fail_io` gates almost all operations after an unrecoverable abort/reopen failure.

## Risk and Test Focus
- Transaction commit ordering is critical: changed details, data space map commit, metadata pre-commit, root copy, superblock update.
- Snapshot creation and metadata snapshots both depend on correct reference-count increments/decrements of shared btree roots.
- `dm_thin_remove_range()` has complex root removal/reinsertion behavior and should be tested across unmapped holes and partial ranges.
- Non-blocking lookup behavior should be verified for `-EWOULDBLOCK`.
- Metadata reserve subtraction can report zero free metadata despite actual reserved blocks.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.h

## Purpose
Declares the public thin-pool metadata API used by the thin provisioning target and related DM code.

## Public Constants and Types
- `THIN_METADATA_BLOCK_SIZE`
- `THIN_METADATA_MAX_SECTORS`
- `THIN_METADATA_MAX_SECTORS_WARNING`
- `THIN_METADATA_NEEDS_CHECK_FLAG`
- `dm_thin_id`
- Opaque:
  - `struct dm_pool_metadata`
  - `struct dm_thin_device`
- `struct dm_thin_lookup_result` with mapped pool block and shared flag.
- `dm_pool_pre_commit_fn`

## API Areas
- Pool metadata open/close:
  - `dm_pool_metadata_open()`
  - `dm_pool_metadata_close()`
- Device lifecycle:
  - `dm_pool_create_thin()`
  - `dm_pool_create_snap()`
  - `dm_pool_delete_thin_device()`
  - `dm_pool_open_thin_device()`
  - `dm_pool_close_thin_device()`
  - `dm_thin_dev_id()`
- Transactions:
  - `dm_pool_commit_metadata()`
  - `dm_pool_abort_metadata()`
  - transaction ID get/set
- Metadata snapshots for userspace:
  - reserve, release, get held root
- Mapping operations:
  - find block
  - find mapped range
  - allocate data block
  - insert/remove block
  - remove range
- Queries:
  - changed/aborted flags
  - highest mapped block
  - mapped counts
  - free block counts
  - data/metadata device size
  - shared-block check
- Space-map refcount helpers:
  - increment/decrement data ranges
- Resize:
  - data and metadata device resize
- Mode and health:
  - read-only/read-write
  - metadata threshold registration
  - needs-check set/query
  - prefetches
  - pre-commit callback registration

## Compatibility Flags
- `THIN_FEATURE_COMPAT_SUPP`
- `THIN_FEATURE_COMPAT_RO_SUPP`
- `THIN_FEATURE_INCOMPAT_SUPP`

All are zero in this version, meaning no optional on-disk feature bits are supported.

## Contract Notes
- Snapshot creation requires a quiesced origin.
- `dm_pool_abort_metadata()` preserves open thin devices but reports whether their uncommitted changes were aborted.
- `dm_thin_find_block()` documents `-EWOULDBLOCK` for nonblocking lookup, `-ENODATA` for absent mappings, and `0` on success.
- Resize documentation describes shrink safety behavior, but the implementation rejects shrinking entirely.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.h -->