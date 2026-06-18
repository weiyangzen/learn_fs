# Group Research: group_1784_stratisd_sources_block_storage_stratisd_src_engine_strat_engine_thi_2aa4c90e2615

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinpool.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinpool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/udev.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/udev.rs

## Purpose

This file centralizes udev helpers for Stratis block-device discovery and ownership classification. It builds block-device enumerators, reads udev properties through the project’s `UdevEngineDevice` wrapper, and classifies devices as Stratis, LUKS, multipath members, unowned, or owned by another subsystem.

## Constants

- `FS_TYPE_KEY`: udev property key `ID_FS_TYPE`.
- `STRATIS_FS_TYPE`: udev filesystem type value `stratis`.
- `CRYPTO_FS_TYPE`: udev filesystem type value `crypto_LUKS`.
- `SUBSYSTEM_BLOCK`: udev subsystem value `block`.

## Main API

`block_enumerator(context)` creates a `libudev::Enumerator`, restricts it to the block subsystem, and returns libudev errors directly.

`get_udev_property(device, property_name)` reads a udev property and converts it into `Option<StratisResult<String>>`. Missing properties return `None`; conversion failures remain as `Some(Err(...))`.

`decide_ownership(device)` classifies one udev device and wraps any property-conversion failure in a `StratisError::Chained` with context.

`block_device_apply(device_path, f)` creates a fresh libudev context, enumerates initialized block devices, finds the one whose devnode equals the provided `DevicePath`, wraps it as `UdevEngineDevice`, and applies a caller-supplied function. It returns `Ok(None)` when the device is not found.

## Classification Rules

`UdevOwnership` has five variants:

- `Luks`
- `MultipathMember`
- `Stratis`
- `Theirs`
- `Unowned`

`Display` maps these to user-facing ownership descriptions.

The classification order is intentional:

1. Multipath member status is checked first using `DM_MULTIPATH_DEVICE_PATH == "1"`.
2. Stratis ownership checks `ID_FS_TYPE == "stratis"`.
3. LUKS checks `ID_FS_TYPE == "crypto_LUKS"`.
4. Unowned checks that there is no partition table unless the device is a partition, and no `ID_FS_USAGE`.
5. Everything else defaults to `Theirs`.

The multipath-first order avoids mistakenly accepting multipath path members that may also appear to contain Stratis signatures.

## Dependencies

- `libudev` for context, enumerator, and device scanning.
- `DevicePath` and `UdevEngineDevice` from engine types.
- `StratisError` and `StratisResult` for error propagation and contextual wrapping.

## Correctness Notes

- `block_device_apply()` is linear in the number of block devices because it scans the udev database rather than directly constructing a device by devnode.
- `is_unclaimed()` treats the absence of ownership-related properties as the only safe unowned signal; `Theirs` is the conservative default.
- Property read errors are not swallowed for Stratis/LUKS/multipath checks, so undecodable udev entries prevent a confident ownership decision.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/udev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/writing.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/writing.rs

## Purpose

This file provides small write helpers for device/file sector wiping, with a `SyncAll` abstraction so production `File`, buffered writers, and test cursors can share the same sync contract.

## Main API

`SyncAll` extends `Write` with `sync_all()`.

Implementations:

- `File`: delegates to `File::sync_all()`.
- `Cursor<T>` in tests: no-op sync, because data is in memory.
- `BufWriter<T>` where `T: SyncAll`: flushes the buffer and then syncs the wrapped writer.

`wipe_sectors(path, offset, length)` writes zeroed sectors at the given sector offset for the specified sector count. It delegates to private `write_sectors()` with a zeroed sector buffer.

## Internal Flow

`write_sectors(path, offset, length, buf)`:

1. Opens the path write-only.
2. Wraps it in a `BufWriter` whose capacity is the smaller of `1 MiB` and the requested byte length.
3. Seeks to `offset.bytes()`.
4. Writes the provided one-sector buffer `length` times.
5. Flushes and syncs via `SyncAll`.
6. Returns `StratisResult<()>`.

## Dependencies

- `devicemapper::{Sectors, IEC, SECTOR_SIZE}` for block units.
- `StratisResult` for project error propagation.
- Standard `File`, `OpenOptions`, `BufWriter`, `Seek`, and `Write`.

## Correctness Notes

- The helper writes whole sectors only; callers must provide sector-granular offsets and lengths.
- It syncs once after all writes, not after each sector.
- Integer conversions use project conversion macros, so offset/capacity conversion failures propagate rather than silently truncating.
- The function is used by thin-pool initialization to zero fresh thin metadata headers before device-mapper adopts them.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/writing.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/structures/lock.rs -->
# File Research: sources/block-storage/stratisd/src/engine/structures/lock.rs

## Purpose

This file implements two locking abstractions used by the Stratis engine:

- `Lockable<Arc<RwLock<T>>>`: a small wrapper around Tokio owned read/write locks with tracing and blocking helpers.
- `AllOrSomeLock<U, T>`: a custom asynchronous lock over a `Table<U, T>` that supports locking either individual entries or all entries, with read/write modes and nonblocking “available subset” acquisition.

The file also defines guard types for shared/exclusive access and for all/some read/write access.

## Simple Lockable Wrapper

`SharedGuard<G>` and `ExclusiveGuard<G>` wrap lock guards, implement `Deref` and, for exclusive guards, `DerefMut`, and trace on drop.

`Lockable<Arc<RwLock<T>>>` provides:

- `new_shared(t)`
- async `read()` and `write()` returning owned Tokio guards wrapped as `SharedGuard`/`ExclusiveGuard`
- blocking versions using `futures::executor::block_on`

`Lockable<Arc<T>>` is cloneable by cloning the inner `Arc`.

## AllOrSomeLock Model

`AllOrSomeLock<U, T>` stores:

- `lock_record: Arc<Mutex<LockRecord<U>>>`
- `inner: Arc<Mutex<UnsafeCell<Table<U, T>>>>`

`U` must implement `AsUuid`, giving copyable UUID-like keys used by `Table`.

The lock supports:

- `read(key)` for one entry
- `write(key)` for one entry
- `read_all()` for all entries
- `write_all()` for all entries
- `read_all_available()` for currently readable non-conflicting entries
- `write_all_available()` for currently writable non-conflicting entries
- `modify_all()` for exclusive mutation of the whole `Table`
- `upgrade(read_guard)` from single read guard to single write guard
- `Default` via an empty table

## Lock State

`LockRecord<U>` tracks:

- `all_read_locked: u64`
- `all_write_locked: bool`
- `read_locked: HashMap<U, u64>`
- `write_locked: HashSet<U>`
- `waiting: VecDeque<Waiter<U>>`
- `woken: HashMap<u64, WaitType<U>>`
- `next_idx: u64`

`WaitType<U>` encodes `Upgrade(U)`, `SomeRead(U)`, `SomeWrite(U)`, `AllRead`, and `AllWrite`.

`Waiter<U>` stores a wait type, `Waker`, and unique future index.

## Conflict Rules

The lock allows concurrent reads when they do not conflict with writes or all-write. Key rules:

- `SomeRead(uuid)` conflicts with write on the same uuid and all-write.
- `SomeWrite(uuid)` conflicts with read/write on the same uuid, all-read, and all-write.
- `Upgrade(uuid)` waits until no other read exists for that uuid and no global conflicting locks exist.
- `AllRead` conflicts with any write or all-write.
- `AllWrite` conflicts with everything.
- Already-woken waiters are considered during conflict checks so newly arriving requests do not bypass compatible wake batches.

`wake()` drains the waiting queue and wakes every waiter that does not conflict with existing acquisitions or already-woken tasks.

`cancel(idx)` removes a future from both waiting and woken state when a future is dropped before completion.

## Futures And Guards

Each async acquisition is represented by a custom `Future`:

- `SomeRead`
- `SomeWrite`
- `AllRead`
- `AllWrite`
- `AllReadAvailable`
- `AllWriteAvailable`
- `AllModify`
- `Upgrade`

The futures lock both the record and inner table mutex, resolve key names/UUIDs, decide whether to wait, install waiters, and return guard objects containing raw pointers into the table.

Single-entry guards:

- `SomeLockReadGuard<U, T>`
- `SomeLockWriteGuard<U, T>`

All-entry guards:

- `AllLockReadGuard<U, T>`
- `AllLockReadAvailableGuard<U, T>`
- `AllLockWriteGuard<U, T>`
- `AllLockWriteAvailableGuard<U, T>`
- `AllLockModifyGuard<U, T>`

The read/write guards provide lookup and iteration helpers. Write guards expose mutable lookups/iteration. All guards release their recorded acquisitions on drop and call `wake()`.

Several guards support `into_dyn()` when `T: Pool`, converting typed pool guards into `dyn Pool` guards while suppressing duplicate drop accounting in the original guard.

`SomeLockWriteGuard::downgrade()` converts a single write guard into a read guard by moving the lock record from write-held to read-held for that UUID.

`Into<Vec<SomeLockReadGuard<...>>>` and `Into<Vec<SomeLockWriteGuard<...>>>` are implemented for all/all-available guards to split aggregate guards into per-entry guards while updating lock-record accounting.

## Unsafe Interior Mutability Contract

The file uses `UnsafeCell<Table<U, T>>` and raw pointers so guards can outlive the short mutex critical section. Safety relies on `LockRecord` enforcing aliasing rules:

- read guards may coexist only with compatible readers
- mutable guards are issued only when no conflicting readers/writers exist
- all-write/modify prevents all other access
- available-subset guards record locks only for the subset they expose
- drop paths release lock-record state and wake compatible waiters

The custom `Send` and `Sync` impls require corresponding bounds on `U` and `T`, but the core aliasing guarantee is manual and tied to correct lock-record bookkeeping.

## Integration Points

- Uses `Table<U, T>` for name/UUID storage.
- Uses `PoolIdentifier<U>` to resolve acquisition requests by name or UUID.
- Uses the engine `Pool` trait for dynamic pool guard conversion.
- Uses Tokio `RwLock` only for the simpler `Lockable`; `AllOrSomeLock` is fully custom.

## Test Coverage

The local unit test `test_cancelled_future()` constructs an empty `AllOrSomeLock`, holds `write_all()`, polls two pending `read_all()` futures, and verifies canceled futures do not leave stale waiters. This targets the cancellation cleanup path in `Drop` for acquisition futures.

## Correctness Notes

- The lock uses a wrapping `u64` index; comments state it supports up to `u64::MAX` futures before index reuse.
- `add_waiter()` guards against spurious wakeups and prioritizes futures that have already waited by pushing them to the front on repeated waits.
- `woken_or_new()` both validates and consumes a woken record for the acquiring future.
- `modify_all()` grants mutable access to the whole `Table`, not merely all current entries, so it is used when the container itself must change.
- The design is powerful but fragile: bugs in drop flags, `into_dyn()`, aggregate splitting, or available-subset accounting could produce stale locks or aliasing violations.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/structures/lock.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/structures/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/structures/mod.rs

## Purpose

This module file declares the `lock` and `table` submodules and re-exports their public engine data structures.

## Exports

From `lock`:

- `AllLockReadAvailableGuard`
- `AllLockReadGuard`
- `AllLockWriteAvailableGuard`
- `AllLockWriteGuard`
- `AllOrSomeLock`
- `ExclusiveGuard`
- `Lockable`
- `SharedGuard`
- `SomeLockReadGuard`
- `SomeLockWriteGuard`

From `table`:

- `Table`

## Role In The Codebase

This file is a public façade for engine structures. Other modules can import `crate::engine::structures::Table` or lock guard types without depending on the private file layout.

## Dependencies

It has no runtime logic and only depends on sibling modules `lock` and `table`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/structures/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/structures/table.rs -->
# File Research: sources/block-storage/stratisd/src/engine/structures/table.rs

## Purpose

This file implements `Table<U, T>`, a bidirectional name/UUID-indexed container used throughout the engine to store named objects while allowing O(1) lookup by either `Name` or UUID-like key.

Internally it keeps:

- `name_to_uuid: HashMap<Name, U>`
- `items: HashMap<U, (Name, T)>`

`U` must implement `AsUuid`, which provides the copy/hash/equality traits expected by the table.

## Public Types

- `Table<U, T>`: main container.
- `Iter<'a, U, T>`: immutable iterator yielding `(&Name, &U, &T)`.
- `IterMut<'a, U, T>`: mutable iterator yielding `(&Name, &U, &mut T)`.
- `IntoIter<U, T>`: owning iterator yielding `(Name, U, T)`.

`IntoIterator` is implemented for owned, shared, and mutable references to `Table`.

`FromIterator<(Name, U, T)>` builds a table by repeated insertion.

`Debug` renders as a debug map keyed by `(name_string, uuid)`.

## Main API

- `is_empty()`
- `len()`
- `iter()`
- `iter_mut()`
- `contains_name(name)`
- `contains_uuid(uuid)`
- `get_by_name(name) -> Option<(U, &T)>`
- `get_by_uuid(uuid) -> Option<(Name, &T)>`
- `get_mut_by_name(name) -> Option<(U, &mut T)>`
- `get_mut_by_uuid(uuid) -> Option<(Name, &mut T)>`
- `remove_by_name(name) -> Option<(U, T)>`
- `remove_by_uuid(uuid) -> Option<(Name, T)>`
- `insert(name, uuid, item) -> Option<Vec<(Name, U, T)>>`

Lookups by UUID clone the `Name` for return. Lookups by name return the UUID by copy.

## Insert Semantics

`insert()` keeps the two maps consistent while allowing replacement by name, UUID, or both.

It can displace:

- no item, when both name and UUID are new
- one item, when inserting the same name or same UUID
- one item, when replacing the same `(name, uuid)` pair
- two items, when the new item uses the name of one existing item and the UUID of another

When two items are displaced, the item displaced by matching name is returned first. The method contains assertions documenting invariants between both maps.

## Invariants

The intended invariant is:

- every `items` entry has a matching `name_to_uuid[name] == uuid`
- every `name_to_uuid` entry has a matching `items[uuid].0 == name`
- both maps have the same length
- there are no stale name or UUID entries after insertion/removal

The test helper `table_invariant()` checks exactly these relationships.

## Test Coverage

Tests cover:

- removing an existing item by UUID and verifying name lookup is also removed
- inserting the same `(name, uuid)` pair and receiving the old item
- inserting a new UUID under an existing name
- inserting a new name under an existing UUID
- inserting a pair that collides with one existing name and a different existing UUID, returning two displaced items in documented order

The tests use `PoolUuid` as the UUID type and a `TestThing` payload with random data to verify the correct item is retained or displaced.

## Integration Notes

`Table` is used by `ThinPool` to store filesystems by `FilesystemUuid` and `Name`, and by `AllOrSomeLock` to expose name/UUID-addressable pools. Its removal and displacement behavior is important for code that temporarily removes an object, mutates metadata, and reinserts it under a new name.

## Correctness Notes

- Operations are intended to be O(1), with name lookup requiring one extra map hop to the UUID-keyed map.
- Rename is intentionally modeled as remove and reinsert.
- `insert()` does not reject collisions; callers must inspect displaced items or validate uniqueness before calling when replacement is not acceptable.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/structures/table.rs -->