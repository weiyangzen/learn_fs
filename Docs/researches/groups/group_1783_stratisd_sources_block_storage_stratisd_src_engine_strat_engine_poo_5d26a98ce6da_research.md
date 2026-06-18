# Group Research: group_1783_stratisd_sources_block_storage_stratisd_src_engine_strat_engine_poo_5d26a98ce6da

Scope verified against `Docs/research_subset_a.md`: `sources/block-storage/stratisd` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/v2.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/v2.rs

## Purpose
Implements the v2 Stratis pool object, `StratPool`, which is the main orchestration layer between the backstore, thin pool, filesystems, metadata persistence, encryption operations, cache/data device management, and engine-facing `Pool` trait behavior.

## Main Components
- `next_index()` computes total flex-device allocation length from metadata segments.
- `check_metadata()` validates internal consistency between `PoolSave.flex_devs`, cap-device allocation, and data-tier allocation before setup.
- `StratPool` owns:
  - `backstore: Backstore`
  - `thin_pool: ThinPool<Backstore>`
  - `action_avail: ActionAvailability`
  - cached `metadata_size`
  - `last_reencrypt`
- `StratPool::initialize()` creates a new pool UUID, initializes the backstore, creates the thin pool, records metadata, and rolls back backstore metadata on setup failure where possible.
- `StratPool::setup()` reconstructs an existing pool from block devices and `PoolSave`, handles limited action availability, writes upgraded metadata when needed, and wipes removed cache devices.
- `impl Pool for StratPool` exposes the engine contract for device, filesystem, cache, encryption, metadata, and state operations.
- `StratPoolState` plus `StateDiff`/`DumpState` support pool-level diff reporting.

## Pool Lifecycle
Initialization performs key-description validation, backstore initialization, thin-pool sizing via `ThinPoolSizeParams::new()`, thin-pool creation, metadata-size caching, and metadata write. Failure during thin-pool parameter selection or thin-pool creation attempts `backstore.destroy(pool_uuid)` and returns a rollback-aware error if cleanup also fails.

Setup validates metadata first, reconstructs the backstore, records action availability, reconstructs the thin pool from saved thinpool/flex metadata, and conditionally rewrites metadata for migration fields such as `started`, `fs_limit`, and `feature_args`. If a pool is in limited availability, metadata write failures caused by disabled actions are warned about rather than fatal.

Stopping tears down thin-pool devices, writes metadata with `started = Some(false)`, tears down the backstore, and returns a `DeviceSet` for later setup. Destroy tears down thin-pool and backstore state and is intentionally not treated as a normal mutating action so broken metadata does not prevent destruction.

## Metadata Behavior
`record()` constructs `PoolSave` with pool name, backstore record, flex device record, thinpool record, `started: Some(true)`, feature flags, and `last_reencrypt`. Feature flags are derived from encryption state and presence of key descriptions or Clevis bindings.

`write_metadata()` serializes `PoolSave` as JSON and delegates persistence to `backstore.save_state()`. `current_metadata()` serializes current state, while `last_metadata()` loads saved bytes and validates UTF-8. `metadata_version()` returns `StratSigblockVersion::V2`.

The metadata consistency check enforces:
- cap allocation equals total flex-device consumption,
- summed flex-device segment lengths equal computed next index,
- data-tier allocation for the cap device is nonzero,
- cap usage does not exceed data-tier allocation.

## Device Management
`init_cache()` validates paths, rejects cache initialization on encrypted pools unless supported, partitions paths into current-pool/other-pool/unowned devices, detects stale metadata/device mismatches, verifies no data-tier devices are passed as cache devices, enforces sector-size compatibility, suspends the thin pool while initializing cache, resumes it, and writes metadata. If the pool already has cache, it treats requests idempotently through `init_cache_idempotent_or_err()`.

`add_blockdevs()` supports both cache and data tiers:
- Cache additions require an existing cache, reject data-tier devices, validate sector sizes against current cache devices, suspend/resume the thin pool around backstore cache modification, then write metadata.
- Data additions reject cache-tier devices, validate sector sizes against current data tier, add data devices without suspending DM devices, update thin-pool queue/out-of-meta state, and returns a `PoolDiff`.

`grow_physical()` asks the backstore to grow a physical device, updates thin-pool queue mode, writes metadata if needed, and returns a pool diff showing physical-size/out-of-space changes.

`set_blockdev_user_info()` updates block-device user metadata and persists on actual change.

## Filesystem Management
`create_filesystems()` enforces pool filesystem limit, validates size specs and names, checks conflicts with existing filesystems, enforces overprovisioning policy, creates missing filesystems through `ThinPool`, and returns created `(Name, FilesystemUuid, Sectors)` tuples.

`destroy_filesystems()`, `rename_filesystem()`, and `snapshot_filesystem()` mostly delegate to `ThinPool` after validation. Snapshots enforce filesystem limit, name validity, origin existence, and overprovisioning limits before creating a snapshot. Existing snapshot names yield identity.

`set_fs_limit()` and `set_overprov_mode()` delegate to `ThinPool`, writing metadata only when required. `set_fs_size_limit()` validates the requested limit relative to the filesystem and changes per-filesystem state. `set_fs_merge_scheduled()` toggles pending merge state through the thin pool.

`fs_event_on()` delegates filesystem checking to `ThinPool::check_fs()`. `event_on()` checks the thin pool on DM events, diffs cached vs dumped state, and writes metadata if the thin pool changed.

## Encryption and Token Management
This file implements pool-level operations for Clevis and keyring binding:
- `bind_clevis()`, `bind_keyring()` persist metadata on new token creation.
- `unbind_keyring()`, `unbind_clevis()` persist metadata on deletion.
- `rebind_keyring()` validates the old and new key descriptions exist in the kernel keyring before delegating to the backstore.
- `rebind_clevis()` delegates token regeneration.

Online encryption/decryption operations are split into start/do/finish phases:
- `start_encrypt_pool()` validates key descriptions, rejects already encrypted pools as identity, and prepares encryption using `DEFAULT_CRYPT_DATA_OFFSET_V2` with backwards offset movement.
- `do_encrypt_pool()` delegates static encryption work to `Backstore::do_encrypt()`.
- `finish_encrypt_pool()` finalizes backstore encryption and persists metadata.
- `start_reencrypt_pool()` validates current key descriptions and prepares reencrypt work.
- `do_reencrypt_pool()` performs reencrypt.
- `finish_reencrypt_pool()` records `last_reencrypt = Utc::now()` and persists metadata.
- `decrypt_pool_idem_check()`, `do_decrypt_pool()`, and `finish_decrypt_pool()` implement idempotent deletion, actual decrypt, forwards offset restoration, clearing `last_reencrypt`, and metadata write.

`free_token_slots()`, `volume_key_is_loaded()`, `load_volume_key()`, and `last_reencrypt()` expose encryption status helpers.

## State and JSON Output
`Into<Value> for &StratPool` merges JSON objects from `ThinPool` and `Backstore`, then adds `available_actions` and `fs_limit`.

`StratPoolState` tracks metadata size, out-of-allocation-space state, and total physical size. Its diff implementation produces `StratPoolDiff`, used by pool event handling and grow/add-device workflows.

## Tests in This File
The embedded test module covers:
- metadata invariants,
- adding cache devices and verifying existing filesystem data remains readable,
- adding data devices after cache initialization,
- recovering an out-of-space thin pool after adding data devices,
- rollback failures triggering reduced action availability,
- overprovisioning enabled/disabled behavior,
- physical device growth through loopback tests,
- multiple Clevis/keyring token slot workflows,
- stopping and restarting pools after cache removal,
- online encryption, reencryption, and decryption with Clevis/keyring support.

Tests use loopbacked and real-device harnesses plus kernel keyring helpers from sibling test modules.

## Dependencies and Interactions
This is a high-coupling engine layer. It coordinates:
- `Backstore` and `StratBlockDev` for physical storage,
- `ThinPool` and `StratFilesystem` for logical filesystems,
- serde save structs for metadata persistence,
- devicemapper types and DM event handling,
- keyring/Clevis encryption metadata,
- action-availability macros generated by `strat_pool_impl_gen`.

## Research Notes
This file is the primary behavior surface for v2 pools. Most policy decisions live here: idempotency rules, sector-size compatibility, overprovisioning enforcement, metadata migration writes, encryption operation staging, and when to suspend/resume thin-pool devices.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/v2.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/serde_structs.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/serde_structs.rs

## Purpose
Defines serde-friendly save structures for Stratis on-disk JSON metadata. These structures intentionally differ from richer in-memory engine objects so persistence remains stable and simple.

## Main Components
- `Recordable<T>` trait abstracts conversion from runtime objects into serializable save records.
- `PoolFeatures` enumerates optional pool features: `Raid`, `Integrity`, `Encryption`, `KeyDescriptionEnabled`, and `ClevisEnabled`.
- `impl From<Vec<PoolFeatures>> for Features` maps persisted feature flags to API-facing feature booleans.
- `PoolSave` is the top-level variable-length pool metadata record.
- `FilesystemSave` is per-filesystem metadata stored separately on the metadata volume.
- Supporting structs describe backstore, block devices, allocations, cap device, cache tier, flex devices, and thinpool metadata.

## Serialization Details
String metadata is capped at `MAXIMUM_STRING_SIZE` bytes. `safe_split_at()` truncates only at UTF-8 character boundaries, using `our_floor_char_boundary()` to avoid invalid string slices. This applies to pool/filesystem names and optional block-device `user_info`/`hardware_info`.

`last_reencrypt` is serialized as a Unix timestamp integer and deserialized back into `DateTime<Utc>`. The serializer expects the option to be `Some` when invoked, and the field uses `skip_serializing_if = "Option::is_none"`.

Several fields are optional for backward compatibility and have TODO comments indicating they should become required in Stratis 4.0:
- `PoolSave.started`
- `ThinPoolDevSave.feature_args`
- `ThinPoolDevSave.fs_limit`
- `ThinPoolDevSave.enable_overprov`

## Metadata Model
`PoolSave` contains:
- pool name,
- `BackstoreSave`,
- `FlexDevsSave`,
- `ThinPoolDevSave`,
- started flag,
- feature list,
- last reencryption timestamp.

`BackstoreSave` contains data tier, cap device, and optional cache tier. `DataTierSave` includes blockdev metadata plus optional integrity spec. `BlockDevSave` stores allocation lists and base device records. `CapSave` stores cap allocations and optional crypt metadata allocations.

`FilesystemSave` records filesystem name, UUID, thin ID, size, creation timestamp, optional size limit, optional origin UUID, and merge flag.

## Tests
A property test verifies `safe_split_at()` always returns a prefix, respects UTF-8 boundaries, and truncates within a bounded byte delta caused by multibyte characters.

## Research Notes
This file is central for metadata compatibility. Most structs are plain data carriers, but the UTF-8-safe truncation and optional-field defaults are important compatibility behavior for older metadata and user-controlled strings.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/serde_structs.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/shared.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/shared.rs

## Purpose
Provides small shared helpers used across strat-engine code.

## Main Components
- `merge(origin, snap)` constructs merged filesystem metadata when reverting an origin filesystem to a snapshot.
- `shift_allocation_offset()` maps an offset transformation over allocation-like items and collects `StratisResult<Vec<T>>`.

## Behavior
`merge()` preserves origin identity fields such as name, UUID, creation timestamp, origin reference, and merge flag, while taking the snapshot thin ID, size, and size limit. This models snapshot merge semantics where the original filesystem identity remains but its underlying thin device state is replaced by the snapshot state.

`shift_allocation_offset()` is generic over borrowed input values and a fallible mapper. It centralizes the pattern of converting a collection of allocation records after an offset adjustment.

## Research Notes
Although small, `merge()` encodes a key metadata invariant: snapshot reversion should not create a new user-visible filesystem identity.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/crypt.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/crypt.rs

## Purpose
Provides encryption-test helpers for creating, installing, changing, and cleaning up random keys in the kernel keyring.

## Main Components
- `generate_random_key()` fills secure memory from `/dev/urandom` and stores it through `StratKeyActions::set_no_fd()`.
- `set_up_key()` creates a `KeyDescription` and generates associated random key data.
- `insert_and_cleanup_key()` runs a test with one installed key description and always unsets it afterward, preserving panic behavior.
- `insert_and_remove_key()` runs a pre-test with the key installed, then removes the key and runs a post-test with the raw key memory.
- `insert_and_cleanup_two_keys()` installs two key descriptions for tests needing key rotation or multiple-key scenarios.
- `change_key()` regenerates key material for an existing key description.

## Behavior
Cleanup is protected with `catch_unwind()`/`resume_unwind()` so test panics do not skip key removal. Key unsetting uses a fresh `StratKeyActions` instance backed by an unbounded Tokio channel.

## Research Notes
These helpers isolate kernel-keyring setup from pool encryption tests. They are used by Clevis/keyring and online encryption/reencryption/decryption tests in `pool/v2.rs` and elsewhere.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/crypt.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/logger.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/logger.rs

## Purpose
Provides one-time logger initialization for tests.

## Main Components
- `LOGGER_INIT: Once`
- `init_logger()`

## Behavior
`init_logger()` wraps `env_logger::init` in `Once::call_once()` because multiple logger initialization attempts return errors. Test harnesses call this before running loopbacked or real-device tests.

## Research Notes
This is intentionally minimal infrastructure to avoid duplicate logger initialization across many tests.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/logger.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/loopbacked.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/loopbacked.rs

## Purpose
Implements the loop-device based test harness for strat-engine tests. It creates sparse backing files, attaches loop devices, runs tests under specified device-count/size constraints, and performs cleanup.

## Main Components
- `DeviceLimits` describes loopback test runs:
  - `Exactly(count, size)`
  - `Range(lower, upper, size)`
- `LoopTestDev` owns a `LoopDevice` and backing `File`.
- `LoopTestDev::new()` creates a sparse file, truncates it to the requested sector size, attaches it to a free loop device, and syncs the backing file.
- `LoopTestDev::grow()` doubles backing-file length and updates loop capacity.
- `Drop for LoopTestDev` detaches the loop device.
- `test_with_spec()` runs a test over all device-count cases.
- `test_device_grow_with_spec()` runs a pre-grow test, doubles the first loop device, then runs a post-grow test.

## Behavior
The default loopback size is 1 GiB. For `Range`, the harness runs both lower and upper counts. Before each run it initializes logging, registers the Clevis token handler once, creates devices under `$HOME/.stratis_loopback`, calls shared cleanup, and catches test panics.

If `NO_TEST_CLEAN_UP=1`, loop devices are intentionally leaked via `forget()` and cleanup is skipped for debugging. Otherwise it removes Stratis DM devices, unmounts test filesystems, and deletes the temporary loopback directory.

## Research Notes
This harness enables destructive storage tests without external disks. It is the loopback counterpart to `tests/real.rs` and is used heavily by pool and thinpool tests.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/loopbacked.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/mod.rs

## Purpose
Defines the strat-engine test-support module layout.

## Main Components
Exports or declares:
- `pub mod crypt`
- private `logger`
- `pub mod loopbacked`
- `pub mod real`
- private `util`
- `pub use util::FailDevice`

## Behavior
The module exposes public harnesses for encryption, loopbacked tests, real-device tests, and the `FailDevice` test utility while keeping logger and general cleanup internals private.

## Research Notes
This is a module index only, but it determines which test utilities are available to sibling test modules.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/real.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/real.rs

## Purpose
Implements the real-block-device test harness for strat-engine tests. It consumes destructive-device configuration, optionally slices large devices into linear DM devices, runs tests, and wipes/cleans up devices.

## Main Components
- `RealTestDev` wraps either a direct device path or a generated `LinearDev`.
- `RealTestDev::new()` wipes the first MiB to clear metadata.
- `RealTestDev::teardown()` wipes again, settles udev, and tears down generated linear devices.
- `DeviceLimits` supports:
  - `Exactly(count, min_size, max_size)`
  - `AtLeast(count, min_size, max_size)`
  - `Range(lower, upper, min_size, max_size)`
- `get_device_runs()` selects or synthesizes device lists from configured device sizes.
- `make_linear_test_dev()` creates a DM linear target over a segment of a larger physical device.
- `test_with_spec()` reads `tests/test_config.json`, selects devices, runs the test, and performs cleanup.

## Behavior
The harness reads `ok_to_destroy_dev_array_key` from `tests/test_config.json`; devices listed there are considered safe to wipe. It measures block-device sizes, filters by minimum and maximum sizes, and can split oversized devices into multiple fixed-size linear devices when additional test devices are needed.

Before each run it calls cleanup, constructs `RealTestDev` wrappers, converts them to paths, catches panics, then optionally cleans up and tears down devices unless `NO_TEST_CLEAN_UP=1`.

## Research Notes
This harness is explicitly destructive. Its device-selection logic allows the same tests to run on varying real hardware availability while preserving minimum/maximum size requirements.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/real.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/util.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/util.rs

## Purpose
Provides shared cleanup and failure-injection utilities for strat-engine tests.

## Main Components
- `cleanup_errors` module defines test-cleanup `Error` and `Result`.
- `dm_stratis_devices_remove()` removes Stratis-related device-mapper devices.
- `stratis_filesystems_unmount()` unmounts mount points containing `stratis`.
- `clean_up()` combines unmount and DM-device cleanup.
- `FailDevice` creates a controllable DM device that can switch part of its table between linear and error targets.

## Cleanup Behavior
`dm_stratis_devices_remove()` settles udev, initializes DM, lists DM devices, and repeatedly attempts removal while progress is made. It targets names starting with:
- `stratis-1`
- `stratis_fail_device`
- `stratis_test_device`

Removal retries each device several times. Remaining devices produce a chained cleanup error.

`stratis_filesystems_unmount()` scans `/proc/self/mountinfo` and lazily unmounts mount points whose path contains `stratis`.

## Failure Device Behavior
`FailDevice::new()` creates a DM linear mapping over a backing device. `start_failing(num_sectors_after_start)` reloads the table with an initial `error` target region followed by a linear region. `stop_failing()` restores a fully linear table. `Drop` resumes the device if suspended and removes it.

## Research Notes
This file is critical for test isolation. It handles the messy state left by failed storage tests and provides deterministic device errors for negative-path testing.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/tests/util.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/dm_structs.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/dm_structs.rs

## Purpose
Contains helper types and functions for interpreting device-mapper thin-pool status and constructing DM target tables.

## Main Components
- `ThinPoolStatusDigest` is a simplified equality-friendly digest of `ThinPoolStatus`.
- `impl From<&ThinPoolStatus> for ThinPoolStatusDigest` maps device-mapper status to stable categories.
- `thin_pool_status_parser::meta_lowater()` extracts metadata low-water mark from working status.
- `thin_pool_status_parser::used()` extracts used data and metadata blocks from working status.
- `thin_table::get_feature_args()` exposes thin-pool feature args from a target table.
- `linear_table::segs_to_table()` converts physical segments into linear target table lines.

## Behavior
`ThinPoolStatusDigest` collapses detailed status into:
- `Fail`
- `Error`
- `Good`
- `ReadOnly`
- `OutOfSpace`

The digest string names intentionally match kernel thin-pool state strings via `strum` serialization attributes.

`linear_table::segs_to_table()` accumulates logical offsets starting at zero while preserving each segment’s backing-device start offset and length.

## Research Notes
This file is a thin adapter around `devicemapper` crate types. It isolates low-level parsing/table-construction details from higher-level thinpool code.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/dm_structs.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/filesystem.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/filesystem.rs

## Purpose
Implements `StratFilesystem`, the runtime representation of a Stratis filesystem backed by a device-mapper thin device and formatted as XFS.

## Main Components
- `StratFilesystem` stores:
  - `thin_dev: ThinDev`
  - creation timestamp,
  - cached used bytes,
  - optional size limit,
  - optional origin filesystem UUID,
  - merge-scheduled flag.
- `initialize()` creates a new thin device, formats it with XFS, assigns a Stratis filesystem UUID, and cleans up the thin device on format failure.
- `setup()` reconstructs an existing filesystem from `FilesystemSave`.
- `snapshot()` creates a thin snapshot and repairs duplicate XFS UUID issues.
- `visit_values()` decides whether a mounted filesystem should be visited and grown.
- `handle_fs_changes()` extends the thin device and runs `xfs_growfs`, rolling back the DM table if growfs fails.
- `record()` converts runtime state to `FilesystemSave`.
- `Filesystem` trait implementation exposes engine-facing filesystem properties.
- `StratFilesystemState` supports diffing size and used space.

## Filesystem Creation and Setup
`initialize()` validates that an optional size limit is not below the requested size, creates a new filesystem UUID, formats the thin device with `create_fs()`, and returns both UUID and runtime filesystem object. If formatting fails, it retries thin-device destruction and logs if cleanup leaves a dangling DM device.

`setup()` rebuilds the DM thin device using saved size and thin ID, converts the saved creation timestamp, and restores size limit, origin, and merge state.

## Snapshot Behavior
`snapshot()` creates a thin snapshot. If the origin is mounted, it temporarily mounts the snapshot with `nouuid` to force XFS log replay, unmounts it, then calls `set_uuid()` so the snapshot has a unique filesystem UUID. Snapshots inherit the origin size limit and record the origin UUID.

## Growth and Usage
`visit_values()` checks thin-device status and current mount points. Mounted filesystems are considered for growth when used bytes exceed half of total bytes. Growth size is computed by `extend_size()`, bounded by pool no-overprovision remaining size and filesystem size limit when applicable.

`handle_fs_changes()` updates the thin-device table length before running `xfs_growfs()`. If XFS growth fails and restoring the old table also fails, it returns a rollback error at `ActionAvailability::NoPoolChanges`.

`fs_usage()` reads statvfs data and returns total and used bytes.

## Metadata and API Surface
`record()` stores name, UUID, thin ID, size, creation timestamp, size limit, origin, and merge flag. `set_size_limit()` rejects limits smaller than current thin-device size and returns whether state changed. `set_merge_scheduled()` requires an origin when scheduling a merge.

`Into<Value>` produces a JSON object with size, used, size limit, and origin strings for reporting.

## Research Notes
This file bridges thin provisioning, XFS behavior, procfs mount discovery, udev naming, and engine-level filesystem state. Snapshot UUID handling and grow rollback are the most important correctness paths.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/filesystem.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mdv.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mdv.rs

## Purpose
Manages the metadata volume, a linear device formatted as XFS and mounted privately to store per-filesystem JSON metadata records.

## Main Components
- `MetadataVol` owns:
  - `dev: LinearDev`
  - `mount_pt: PathBuf`
- `initialize()` formats the linear device and calls setup.
- `setup()` mounts the metadata volume and ensures the `filesystems` directory exists.
- `save_fs()` atomically writes or updates a filesystem JSON record.
- `rm_fs()` removes a filesystem JSON record durably.
- `filesystems()` loads all saved filesystem records.
- `teardown()` unmounts, removes the mount point, and removes the DM device.
- `Drop` attempts to unmount if explicit teardown was not called.
- `remove_temp_files()` removes stale temporary files from interrupted saves.

## Mount and Directory Behavior
The mount point is under `NS_TMPFS_LOCATION` and named with the pool UUID. `setup()` creates the mount directory, mounts XFS, treats `EBUSY` as already mounted, creates the `filesystems` subdirectory, and removes stale `.temp` files.

## Persistence Behavior
`save_fs()` serializes `FilesystemSave` to JSON, writes it to a `.temp` file, calls `sync_all()` on the temp file, renames it to `<uuid>.json`, then fsyncs the containing directory. This avoids truncated metadata files after interrupted writes and makes the rename durable.

`rm_fs()` removes `<uuid>.json`; missing files are treated as idempotent success. When a file is actually removed, it fsyncs the directory so the unlink is durable.

`filesystems()` iterates metadata records, ignores `.temp` entries, reads each file completely, and deserializes JSON.

## Teardown and Drop
`teardown()` checks whether the mount point is actually a mount by comparing `stat()` device IDs with the parent directory. If mounted, it retries unmount. It then attempts to remove the mount directory and removes the associated DM device by name.

`Drop` uses similar mount detection and retry unmount logic, warning instead of returning errors.

## Limits
`max_fs_limit()` estimates the maximum number of filesystem records by dividing metadata-volume total sectors by `XFS_MIN_FILE_ALLOC_SIZE`, set to 8 sectors or 4 KiB.

## Research Notes
This file is the durability core for per-filesystem metadata. The write-temp/rename/fsync pattern is deliberate crash-safety behavior and should be preserved.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mdv.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mod.rs

## Purpose
Defines the thinpool module structure and public re-exports.

## Main Components
Declares modules:
- `dm_structs`
- `filesystem`
- `mdv`
- `thinids`
- `thinpool`

Publicly re-exports:
- `StratFilesystem`
- `ThinPool`
- `ThinPoolSizeParams`
- `DATA_BLOCK_SIZE`

Conditionally re-exports `ThinPoolStatusDigest` for tests.

## Research Notes
This is the module boundary for thinpool internals. External strat-engine code imports the main thinpool and filesystem types through this file rather than directly from submodules.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinids.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinids.rs

## Purpose
Provides `ThinDevIdPool`, a simple allocator for device-mapper thin device IDs.

## Main Components
- `ThinDevIdPool { next_id: u32 }`
- `new_from_ids(ids)` initializes the next ID to one greater than the maximum existing thin ID, or zero if no IDs exist.
- `new_id()` converts `next_id` into a `ThinDevId`, increments `next_id`, and returns the allocated ID.

## Behavior
The allocator does not verify duplicate input IDs. It is monotonic from the maximum existing ID and relies on `ThinDevId::new_u64()` for validity checking. A TODO notes that failure handling could be improved to guarantee failure only after all 24-bit IDs are exhausted.

## Research Notes
This is intentionally small allocation state used during thin filesystem creation/setup. Its main invariant is avoiding reuse of known existing IDs by starting above the maximum saved ID.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinids.rs -->