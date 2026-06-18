# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinpool.rs

## Purpose

This file implements Stratis thin-pool management over device-mapper. It owns creation, setup, teardown, resizing, metadata recording, filesystem lifecycle operations, snapshot/revert scheduling, device remapping, status diffing, and integration tests for `ThinPool<B>` over both v1 and v2 backstores.

The main abstraction is `ThinPool<B>`, parameterized by an `InternalBackstore` implementation. It coordinates four flex-device areas:

- thin metadata device
- thin metadata spare device
- thin data device
- metadata volume device, or MDV

## Main Types And Constants

- `DEFAULT_FS_LIMIT`: default maximum filesystem count, currently `100`.
- `DATA_BLOCK_SIZE`: thin-pool data block size, `1 MiB`.
- `INITIAL_MDV_SIZE`: initial MDV allocation, `512 MiB`.
- `DATA_ALLOC_SIZE` and `DATA_LOWATER`: production values are `50 GiB` allocation and `15 GiB` low-water; tests use smaller `5 GiB` and `4 GiB`.
- `FeatureArg`: maps thin-pool feature arguments to snake-case strings: `error_if_no_space`, `no_discard_passdown`, `skip_block_zeroing`.
- `Segments`: records physical segment vectors for metadata, metadata spare, data, and MDV.
- `ThinPoolSizeParams`: initial sizing bundle for metadata, data, and MDV.
- `ThinPool<B>`: device-mapper thin pool plus segment metadata, thin ID generator, filesystem table, MDV, current backing device, cached status, allocation size, filesystem limit, overprovisioning flag, and metadata-space flag.
- `ThinPoolState`: lightweight state used for `StateDiff`, tracking allocated and used bytes.

## Important Helper Logic

- `sectors_to_datablocks()` and `datablocks_to_sectors()` convert between device-mapper units using `DATA_BLOCK_SIZE`.
- `thin_pool_identifiers()` formats DM name, device number, and devnode for status logs.
- `coalesce_segs()` appends segment lists while merging a boundary pair if adjacent.
- `room_for_data()` subtracts MDV and two metadata-device allocations from usable backstore space.
- `calc_total_physical_used()` adds thin data usage, metadata size, spare size, and MDV size when thin status exposes data usage.
- `setup_metadev()` runs `thin_check` on inactive pools and swaps metadata/spare segments if `thin_repair` succeeds.
- `attempt_thin_repair()` builds a spare linear device, repairs into it, tears down old metadata, and renames repaired spare to the canonical metadata device.

## Construction And Setup

`ThinPool<v1::Backstore>::new()` and `ThinPool<v2::Backstore>::new()` are near-parallel constructors. They allocate metadata, spare metadata, data, and MDV segments from the backstore, create linear DM devices for each, wipe the first up-to-8 sectors of the fresh metadata device, initialize the MDV, and create the `ThinPoolDev` with `no_discard_passdown` and `skip_block_zeroing`.

`ThinPool<B>::setup()` reconstructs an existing pool from `ThinPoolDevSave` and `FlexDevsSave`. It:

- recreates the MDV and reads filesystem metadata
- rejects duplicate filesystem names or UUIDs in MDV records
- analyzes scheduled snapshot merge/revert metadata and rejects ambiguous duplicate or chained revert requests
- repairs thin metadata if needed
- sets up data and thin-pool DM devices
- migrates older metadata without saved feature args by adding default feature args and switching queue-if-no-space behavior
- performs ready snapshot merges with `merge()`, `set_uuid()`, MDV save/remove, and thin device deletion messages
- sets up remaining filesystems and repopulates the `Table<FilesystemUuid, StratFilesystem>`
- rebuilds `ThinDevIdPool` from existing filesystem thin IDs
- restores `fs_limit` and overprovisioning settings, with defaults for older metadata

## Filesystem Lifecycle

The file exposes lookup and iteration helpers over the filesystem `Table`:

- `get_filesystem_by_uuid()`, `get_mut_filesystem_by_uuid()`
- `get_filesystem_by_name()`, `get_mut_filesystem_by_name()`
- `has_filesystems()`
- `filesystems()`, `filesystems_mut()`

`create_filesystem()` checks the MDV for duplicate names, allocates a new thin ID, initializes `StratFilesystem`, saves metadata to the MDV, inserts the filesystem into the table, and triggers udev symlink updates. If MDV save fails, it retries filesystem destruction for cleanup.

`snapshot_filesystem()` creates a thin snapshot of an existing origin, assigns a fresh filesystem UUID and thin ID, saves metadata, inserts it in the table, and updates udev.

`destroy_filesystem()` removes the filesystem from the table, destroys the thin device, clears the out-of-metadata flag, removes MDV metadata, and reinserts the filesystem if destruction fails.

`destroy_filesystems()` implements multi-delete semantics with snapshot origin handling. It prevents destruction while involved snapshots have merge/revert scheduled, destroys requested filesystems, and rewrites surviving snapshot origins when their origin filesystem is removed.

`rename_filesystem()` uses the existing `rename_filesystem_pre!` validation macro, removes the filesystem from the table, saves MDV metadata under the new name, reinserts on success, and rolls back the table if MDV save fails.

`set_fs_size_limit()` delegates to the filesystem object and persists the changed limit to MDV.

`set_fs_merge_scheduled()` only permits scheduling on snapshots with origins, rejects ambiguous merge chains and multiple snapshots targeting the same origin, updates the filesystem flag, and persists to MDV.

## Pool State, Modes, And Eventing

`set_state()` updates cached thin-pool status and logs status digest changes. Non-good transitions are warned; good transitions are informational.

`used()` parses cached `ThinPoolStatus` into data-used sectors and metadata-used blocks.

`total_physical_used()` adds parsed data usage to physical metadata/spare/MDV allocations.

`set_error_mode()` and `set_queue_mode()` toggle thin-pool out-of-space behavior through device-mapper feature messages. The naming is subtle:

- error mode is enabled when the pool is not already configured as out of alloc space
- queue mode is enabled when the pool is already in error-if-no-space mode and newly allocated space is expected

`out_of_alloc_space()` detects the `error_if_no_space` feature in the thin-pool table.

`get_eventing_dev_names()` returns DM names for thin metadata, thin data, MDV, thin-pool device, and all filesystem thin devices.

`suspend()` suspends the thin pool then MDV, rolling back by resuming the thin pool if MDV suspend fails. `resume()` resumes MDV first, then the thin pool.

`current_fs_metadata()` serializes live filesystem records from memory. `last_fs_metadata()` serializes saved records from MDV.

`min_logical_sector_size()` computes the minimum logical sector size across all filesystems, returning `None` for empty pools.

## Resize And Space Management

`check()` is the central pool maintenance path. It asserts the backstore cap device has not changed, captures old state, attempts metadata extension when needed, extends the data device when data low-water is crossed and the pool is not in error-if-no-space mode, refreshes low-water and resumes, dumps new state, and returns both a metadata-save boolean and a `ThinPoolDiff`.

`check_fs()` scans filesystem usage and grows filesystems as needed. If overprovisioning is disabled, it computes remaining logical space and passes it through filesystem growth decisions. It runs filesystem checks in scoped threads, persists changed filesystem records to MDV in parallel, and returns per-filesystem diffs for changed size or usage.

`extend_thin_data_device()` allocates up to `DATA_ALLOC_SIZE` from remaining backstore space, updates the data linear table while the thin pool is suspended, coalesces segment records, resumes the thin pool, and returns `(changed, result)`. If no space remains, it switches to error mode and returns out-of-space.

`extend_thin_meta_device()` either doubles metadata size on low-water or recomputes metadata size for a new filesystem limit. It enforces overprovisioning-disabled constraints, needs matching metadata and spare allocations, sets `out_of_meta_space` when growth cannot proceed, and updates metadata/spare segment records only after successful table changes.

`set_fs_limit()` validates monotonic increase, checks the MDV maximum filesystem limit, extends metadata as needed, and persists the new limit when successful.

`total_fs_limit()` returns the maximum total logical filesystem size allowed when overprovisioning is disabled.

`set_overprov_mode()` disables overprovisioning only if current logical filesystem size is within available data budget; enabling it clears the metadata-space flag.

## Backstore Device Remapping

`set_device()` rewrites all internal linear/flakey target tables when the upper backstore device changes, for example when adding cache. It maps start offsets forward or backward with overflow/underflow checks, computes new metadata/data/MDV tables and segment lists, then applies metadata, data, and MDV table changes with rollback attempts on partial failure. On success, it updates recorded segment vectors and `backstore_device`.

## Serialization And Metadata Recording

`Into<Value> for &ThinPool<B>` emits JSON containing filesystem records merged with name and UUID.

`Recordable<FlexDevsSave> for Segments` and for `ThinPool<B>` records MDV, thin metadata, thin data, and spare metadata segment vectors.

`Recordable<ThinPoolDevSave> for ThinPool<B>` records data block size, sorted feature args, filesystem limit, and overprovisioning mode.

`DumpState` caches and dumps allocated size and total physical used. `dump()` also refreshes thin-pool status and cached allocated size from the backstore.

## Integration Points

This file depends heavily on:

- `devicemapper` for `ThinPoolDev`, `LinearDev`, target tables, status, messages, and units.
- Stratis backstore v1/v2 allocation and cap-device APIs.
- Stratis DM naming helpers for thin pool, flex devices, and filesystems.
- MDV persistence via `MetadataVol`.
- `StratFilesystem` for filesystem setup, snapshot, destroy, resize, metadata records, and udev changes.
- command wrappers for `thin_metadata_size`, `thin_check`, `thin_repair`, and XFS `set_uuid`.
- shared helpers `merge()` and `shift_allocation_offset()`.
- `Table` for UUID/name indexed filesystem storage.

## Safety And Correctness Notes

- Fresh thin metadata devices must be zeroed before creating the thin pool; the constructor wipes the initial sectors for this reason.
- Metadata extension always needs matching metadata and spare allocations; failure can set `out_of_meta_space` and switch pool behavior.
- Several methods return a boolean alongside `StratisResult` because a partial allocation/table update may require metadata saving even when the final operation reports an error.
- `setup()` deliberately handles ambiguous scheduled merges conservatively, warning and skipping ambiguous operations rather than guessing order.
- `set_device()` has rollback paths, but rollback failures are surfaced as `RollbackError` with `ActionAvailability::NoPoolChanges`.
- `check_fs()` uses scoped threads over mutable filesystem references; correctness relies on each thread receiving a distinct filesystem from `Table::iter_mut()`.
- `thin_pool_status` is cached; methods using `used()` depend on a prior status refresh through construction, setup, or `dump()`/`check()`.

## Tests

The test module contains block-device integration tests for both v1 and v2 backstores. They cover:

- lazy data allocation and low-water extension
- filling a pool, adding devices, and recovering to good status
- filesystem snapshot content preservation
- filesystem rename persistence and udev symlink behavior
- setup of an already-active pool with existing filesystem data
- thin device destruction and MDV cleanup
- suspend/resume idempotency
- v1 `set_device()` after cache construction
- v2 cache initialization behavior
- filesystem size limits, growth, snapshot inheritance, and rejection of too-small limits
- origin and merge-scheduled behavior during destruction

The tests require loopback or real block-device environments and mount XFS filesystems, so they are integration-heavy rather than pure unit tests.
