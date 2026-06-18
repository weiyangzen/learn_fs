# Group Research: group_280_devicemapper_rs_sources_block_storage_devicemapper_rs_src_cachedev_r_2ae94facd4f9

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/cachedev.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/cachedev.rs

## Purpose
Implements the `dm-cache` high-level wrapper: target parameters, single-line target table, status parsing, construction/setup, resizing of meta/cache/origin backing linear devices, and teardown.

## Key Types
`CacheTargetParams` serializes/deserializes `cache <meta> <cache> <origin> <block_size> <features> <policy> <policy_args>`. `CacheDevTargetTable` enforces exactly one target line. `CacheDevUsage`, `CacheDevPerformance`, `CacheDevMetadataMode`, `CacheDevWorkingStatus`, and `CacheDevStatus` model kernel status output.

## Behavior
`CacheDev::new` rejects existing names, generates a default writethrough/default-policy table, and creates a private DM device. `setup` is idempotent when the kernel table and uuid match. `set_origin_table`, `set_cache_table`, and `set_meta_table` reload relevant subdevices and then reload the cache table; cache/meta reloads deliberately reload unchanged cache table to avoid a documented smq issue. `equivalent_tables` ignores policy name but compares core identity fields and policy args.

## Dependencies
Builds on `LinearDev`, `DM`, `DmOptions`, `DmDevice`, `TargetTable`, shared parsing helpers, and sector/block unit wrappers. Uses `status!`, `to_raw_table_unique!`, and device/name/uuid/devnode macros from `shared_macros.rs`.

## Tests/Notes
Loopback tests create a minimal cache from two or three loop devices, verify parsed status, kernel table, metadata/cache/origin size changes, and suspend/resume. Parsing assumes enough fields after declared feature/policy counts; malformed count/length mismatches may panic by slice indexing rather than always returning `DmError`.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/cachedev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/consts.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/consts.rs

## Purpose
Defines IEC binary-size constants under `IEC`.

## Key Exports
`Ki`, `Mi`, `Gi`, `Ti`, `Pi`, `Ei` as `u64`, each derived by multiplying by 1024.

## Behavior
Simple constants used throughout tests and device setup for loopback backing-file sizes, metadata sizes, and cache block bounds.

## Notes
Module intentionally allows non-snake-case and non-upper-case globals to preserve familiar IEC unit spelling.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/consts.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/device.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/device.rs

## Purpose
Defines `Device`, the major/minor representation used by device-mapper APIs, plus conversions to/from Linux device encodings and block-device node discovery.

## Key APIs
`Device { major, minor }`, `Display` as `major:minor`, `FromStr`, `From<dev_t>`, `From<Device> for dev_t`, `from_kdev_t`, `to_kdev_t`, and `devnode_to_devno`.

## Behavior
Handles glibc/libc `dev_t` via `major`, `minor`, and `makedev`, with Android conversion differences. `from_kdev_t`/`to_kdev_t` implement kernel “huge” `kdev_t` encoding and reject values too large for 12-bit major/20-bit minor representation. `devnode_to_devno` returns `Ok(None)` for missing or non-block paths.

## Tests/Notes
Tests verify round-trip `dev_t` and `kdev_t` conversions. Metadata failures are wrapped as core `MetadataIo`.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/device.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/deviceinfo.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/deviceinfo.rs

## Purpose
Converts raw `dm_ioctl` headers into safe `DeviceInfo` values.

## Key APIs
`DeviceInfo::new`, `TryFrom<Struct_dm_ioctl>`, and getters for version, open count, event number, device, name, uuid, and flags.

## Behavior
Parses null-terminated `name` and `uuid` C arrays, converts empty strings to `None`, validates non-empty identifiers through `DmNameBuf`/`DmUuidBuf`, stores flags via `DmFlags::from_bits_truncate`, and converts `ioctl.dev` from kernel `kdev_t`.

## Notes
Fails with `InvalidArgument` if kernel name/uuid buffers lack NUL termination. `data_size` and `data_start` are retained but not exposed.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/deviceinfo.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/dm.rs

## Purpose
Implements the low-level device-mapper control context and all ioctl-facing operations.

## Key APIs
`DM::new`, `version`, `remove_all`, `list_devices`, `device_create`, `device_remove`, `device_rename`, `device_suspend`, `device_info`, `device_wait`, `table_load`, `table_clear`, `table_deps`, `table_status`, optional `list_versions`, `target_msg`, and `arm_poll`.

## Core Mechanics
`DM` opens `/dev/mapper/control` on Linux or `/dev/device-mapper` on Android. `DmOptions::to_ioctl_hdr` builds ioctl headers with filtered flags and udev flags encoded into `event_nr`. `do_ioctl` sets minimum ioctl interface versions, clears `event_nr` for commands that do not accept input there, starts udev synchronization when needed, serializes header/input data into a growable buffer, retries on `DM_BUFFER_FULL`, and parses the output into `DeviceInfo` plus data bytes.

## Table Handling
`table_load` serializes `dm_target_spec` records plus NUL-padded parameter strings aligned to `u64`. `parse_table_status` reconstructs `(start, length, target_type, params)` tuples and trims via NUL parsing. `table_deps` converts dependency devices from kernel `kdev_t`.

## Error/Retry Behavior
Ioctl failures include both input and output headers when parseable. `device_remove` retries `EBUSY` up to five attempts with 200 ms delay. Oversized ioctl responses return `IoctlResultTooLarge`.

## Tests/Notes
Sudo-style tests cover version, list/create/remove/rename/status/table/deps semantics, duplicate names/UUIDs, UUID setting behavior, and a no-udev lifecycle using an error target.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_flags.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/dm_flags.rs

## Purpose
Defines Rust `bitflags` wrappers for kernel device-mapper flags and udev-cookie flags.

## Key Types
`DmFlags` wraps ioctl flags such as read-only, suspend, persistent dev, status table, buffer full, noflush, query inactive table, uevent generated, uuid rename, secure data, data out, deferred remove, and internal suspend. `DmUdevFlags` wraps libdevmapper udev-rule flags.

## Behavior
Flags map directly to constants from `devicemapper_sys`. `DmOptions` filters user-provided flags by each ioctl’s valid set before calling the kernel.

## Notes
`DmUdevFlags` comments mirror libdevmapper semantics, including rule disabling and primary-source behavior.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_flags.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_ioctl.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/dm_ioctl.rs

## Purpose
Re-exports bindgen-generated `devicemapper_sys` structs/constants and records supported ioctl command version requirements.

## Key APIs
Re-exports `dm_ioctl`, `dm_name_list`, `dm_target_deps`, `dm_target_msg`, `dm_target_spec`, `dm_target_versions`, and constants. Provides `ioctl_to_version`, `ioctl_uses_udev_cookie`, and `ioctl_uses_event_number`.

## Behavior
`IOCTL_VERSIONS` maps commands to minimum `(major, minor, patch)` interface versions, conditionally including newer commands behind cfg flags. Udev cookies are used for remove, rename, and suspend/resume; `DM_DEV_WAIT` uses `event_nr` as an event number but not for udev sync.

## Notes
`DM_DEV_ARM_POLL` is intentionally gated at 4.37 despite libdevmapper documenting 4.36, because the command appeared after 4.36.0.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_ioctl.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_options.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/dm_options.rs

## Purpose
Encapsulates per-call device-mapper flags and udev behavior.

## Key APIs
`DmOptions::set_flags`, `set_udev_flags`, `flags`, `udev_flags`, and `private`.

## Behavior
Methods consume and return `DmOptions` for builder-style chaining. `private()` disables subsystem, disk, and other udev rules while leaving core DM rules enabled.

## Notes
`core/dm.rs` encodes `udev_flags` in the upper bits of `event_nr` when relevant.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_options.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_udev_sync.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/dm_udev_sync.rs

## Purpose
Implements device-mapper udev synchronization using SysV semaphores on non-Android platforms, and a no-op implementation on Android.

## Key APIs
`UdevSyncAction::{begin,end,cancel,is_active}` and exported `UdevSync`.

## Non-Android Behavior
Checks SysV semaphore support through `SEM_INFO`, warns on low semaphore limits, and detects udev via `/run/udev/control`. For remove/rename/resume ioctls, when udev is running and not suspending, it creates a random nonzero cookie, allocates a one-semaphore set, encodes `DM_UDEV_PRIMARY_SOURCE_FLAG`, increments initial state, waits for udev completion at end, and removes the semaphore. If no uevent was generated, it decrements locally to clear state.

## Failure Handling
Semaphore creation retries on key collision. Allocation/setup failures destroy partially-created semaphores. `cancel` destroys without waiting after ioctl failure.

## Tests/Notes
Tests cover invalid semaphore args, create/destroy, active/inactive sync, cancel, no-uevent end, and no-udev behavior. Android module ignores arguments and always reports inactive sync.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/dm_udev_sync.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/errors.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/errors.rs

## Purpose
Defines low-level core error variants for device-mapper operations.

## Key Variants
`ContextInit`, `InvalidArgument`, `Ioctl`, `IoctlResultTooLarge`, `MetadataIo`, `GeneralIo`, and `UdevSync`.

## Behavior
`Ioctl` carries ioctl number, optional input/output `DeviceInfo`, and underlying `nix::Error`. `Display` messages include operational context, including path metadata failures and maximum buffer size for oversized ioctl responses.

## Notes
`source()` exposes the underlying nix error only for ioctl failures.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/errors.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/mod.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/mod.rs

## Purpose
Defines the low-level core module tree and public re-exports.

## Exports
Exports `devnode_to_devno`, `Device`, `DeviceInfo`, `DM`, `DmFlags`, `DmUdevFlags`, `DmOptions`, `DevId`, `DmName`, `DmNameBuf`, `DmUuid`, and `DmUuidBuf`.

## Internal Modules
Includes device, deviceinfo, dm, flags, ioctl bindings, options, udev sync, errors, SysV semaphore bindings, typed IDs, and utilities.

## Notes
Only `errors` is public as a module; most implementation modules stay private behind selected re-exports.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/sysvsem.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/sysvsem.rs

## Purpose
Thin re-export module for SysV semaphore types/constants missing or awkward in `libc`.

## Exports
`seminfo`, `semun`, `GETVAL`, `SEM_INFO`, and `SETVAL` from `devicemapper_sys`.

## Usage
Consumed by `dm_udev_sync.rs` for `semctl` operations and SysV semaphore capability probing.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/sysvsem.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/types.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/types.rs

## Purpose
Defines safe typed identifiers for device-mapper names and UUIDs, plus `DevId`.

## Key Types
`DmName`/`DmNameBuf` and `DmUuid`/`DmUuidBuf` are generated by `str_id!` using kernel length limits. `DevId<'a>` selects either name or UUID for APIs accepting either.

## Behavior
Identifiers must be non-empty ASCII strings shorter than the kernel buffer length, leaving room for NUL termination. `DevId` displays the contained identifier.

## Dependencies
Uses `DM_NAME_LEN` and `DM_UUID_LEN` from ioctl bindings and returns core `InvalidArgument` through `DmError`.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/types.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/util.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/core/util.rs

## Purpose
Provides low-level alignment, C-string, and C-struct byte-slice helpers.

## Key APIs
`align_to`, `byte_slice_from_c_str`, `str_from_c_str`, `str_from_byte_slice`, `mut_slice_from_c_str`, `slice_from_c_struct`, and `c_struct_from_slice`.

## Behavior
`align_to` rounds up to a power-of-two boundary. String helpers scan to first NUL and require UTF-8. Struct helpers use unsafe pointer casts to expose raw bytes or typed references.

## Notes
Safety relies on callers passing valid in-memory C structs and correctly-sized kernel buffers.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/core/util.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/id_macros.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/id_macros.rs

## Purpose
Defines macros for restricted device-mapper string identifier types.

## Key Macros
`str_check!` validates ASCII, non-empty, maximum-length strings. `str_id!` generates borrowed unsized and owned identifier types with `new`, `as_bytes`, `ToOwned`, `Display`, `AsRef`, `Borrow`, and `Deref`.

## Behavior
Borrowed identifiers are created by unsafe transparent cast from `str` after validation. Owned identifiers validate at construction and deref by re-validating invariant-held inner strings.

## Tests/Notes
Tests cover empty and overlong rejection, bytes, ownership conversion, display, and deref behavior.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/id_macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/lib.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/lib.rs

## Purpose
Crate root for the devicemapper Rust library, documenting Linux device-mapper concepts and exposing the public API.

## Module Structure
Loads macros (`bitflags`, `nix`, `log`, range/id/shared macros), private modules for constants/core/cache/linear/result/shared/thin/thinpool/units, and test support under `cfg(test)`.

## Public API
Re-exports cache, core, linear/flakey, result, shared target traits/types, thin device, thin device ID, thin pool, and unit wrappers.

## Documentation
Explains DM lifecycle: create device, load inactive table, resume via suspend ioctl, active/inactive tables, and polling flow for DM minor version 37+.

## Notes
The crate surface is intentionally higher-level than raw ioctls while still exposing `DM` for direct control.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/lineardev.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/lineardev.rs

## Purpose
Implements `dm-linear` and `dm-flakey` target parameter types, multi-line linear target tables, and `LinearDev`.

## Key Types
`LinearTargetParams`, `Direction`, `FlakeyFeatureArg`, `FlakeyTargetParams`, `LinearDevTargetParams`, `LinearDevTargetTable`, and `LinearDev`.

## Behavior
Linear params parse `linear <device> <offset>`. Flakey params parse device, offset, up/down intervals, and optional features: `drop_writes`, `error_writes`, and `corrupt_bio_byte <offset> <r|w> <value> <flags>`. `LinearDev::setup` creates or validates an existing device; equality requires exact table match and segment order. `set_table` loads a new inactive table and updates local state. `set_name` renames via DM and refreshes `DeviceInfo`.

## Tests/Notes
Loopback tests cover empty table failures, rename, duplicate segments, several segments, same-name validation, same-segment different-name creation, suspend/resume, and flakey parsing. Warnings note overlapping segments are not rejected and have undefined behavior.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/lineardev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/range_macros.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/range_macros.rs

## Purpose
Generates strongly-typed numeric wrappers for storage units/ranges.

## Key Macros
`range_u64!`, `range_u128!`, `range!`, arithmetic macros for add/sub/mul/div/rem, `checked_add!`, `sum!`, `serde_macro!`, `display!`, `debug_macro!`, and `deref!`.

## Behavior
Generated types are tuple structs with default/order/hash/copy semantics, arithmetic with same-type and primitive RHS values, `Sum`, deref to inner numeric type, serde numeric serialization, and checked addition.

## Tests/Notes
Tests instantiate `Units` and verify derivations, display/debug, sum, arithmetic, checked overflow, and remainder/division behavior.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/range_macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/result.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/result.rs

## Purpose
Defines the crate-wide result and outer error type.

## Key Types
`ErrorEnum` with `Error`, `Invalid`, and `NotFound`; `DmError` with `Dm(ErrorEnum, String)` and `Core(core::errors::Error)`; `DmResult<T>` alias.

## Behavior
Core errors convert into `DmError::Core`. Display distinguishes “DM Core error” from higher-level “DM error”.

## Notes
`DmError` implements `std::error::Error` but does not forward `source()` to core errors here.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/result.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/shared.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/shared.rs

## Purpose
Defines common abstractions and helpers for all high-level DM target wrappers.

## Key Types/Traits
`TargetType`/`TargetTypeBuf`, `TargetParams`, `TargetLine<T>`, `TargetTable`, and `DmDevice<T>`.

## Shared Device Behavior
`DmDevice` supplies kernel-table reads, default resume/suspend, table loading, and required device/name/size/table/teardown/uuid hooks. `device_create` creates, loads table, resumes, and removes the device if table load fails. `device_match` compares kernel table and uuid against local expectations. `device_exists` searches `list_devices`.

## Parsing Helpers
`parse_device` accepts block-device path or `major:minor`. `parse_value` wraps `FromStr`. `get_status_line_fields`, `get_status`, and `make_unexpected_value_error` centralize status parsing errors.

## Notes
`device_match` has a typo in its error string (“uuuid”). `device_create` uses default options for create/table-load and caller-provided options only for resume.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/shared_macros.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/shared_macros.rs

## Purpose
Provides small implementation macros shared by DM device wrapper structs.

## Key Macros
`device!`, `name!`, `uuid!`, `devnode!`, `to_raw_table_unique!`, `table!`, and `status!`.

## Behavior
Macros delegate common methods to `dev_info` and `table`, build `/dev/dm-<minor>` paths, convert single-line target tables to raw tuples, and implement status retrieval via `DM::table_status` plus parser conversion.

## Notes
`name!` panics if `DeviceInfo` has no name, so wrapper structs assume named DM devices.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/shared_macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/logger.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/testing/logger.rs

## Purpose
Provides one-time logger initialization for tests.

## Key API
`init_logger()` calls `env_logger::init` behind a `Once`.

## Notes
Avoids repeated logger initialization failures across multiple tests.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/logger.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/loopbacked.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/testing/loopbacked.rs

## Purpose
Creates loopback-backed block devices for integration-style tests.

## Key APIs
`test_with_spec(count, test)`, internal `LoopTestDev`, `get_devices`, `write_sectors`, and `wipe_sectors`.

## Behavior
Creates sparse 1 GiB files in a tempdir, attaches loop devices, wipes the first MiB to remove leftover DM metadata, passes paths to the test closure, catches panics, runs cleanup, and detaches loop devices on drop.

## Notes
Uses `unwrap` heavily because it is test-only. `test_with_spec` unwraps the test result before cleanup result, so a panic plus cleanup failure reports the panic first.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/loopbacked.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/mod.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/testing/mod.rs

## Purpose
Testing module aggregator.

## Exports
Re-exports `test_with_spec`, block-device sizing, test name/uuid/string helpers, udev settle, XFS filesystem creation, and XFS UUID setting.

## Notes
Modules `logger`, `loopbacked`, and `test_lib` remain private behind curated test helpers.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/test_lib.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/testing/test_lib.rs

## Purpose
Provides integration-test utilities for DM cleanup, block-device sizing, XFS commands, udev settling, and test identifiers.

## Key APIs
`DM::list_test_devices`, `blkdev_size`, `xfs_create_fs`, `xfs_set_uuid`, `udev_settle`, `test_name`, `test_uuid`, `test_string`, and `clean_up`.

## Behavior
Uses `BLKGETSIZE64` ioctl for byte size. Maintains a lazily-created global `DM` context for cleanup. Test names append `_dm-rs_test_delme`. Cleanup unmounts mount points containing the suffix and repeatedly removes matching DM devices while progress is made.

## Error Handling
Command failures include stdout and stderr. Cleanup uses a local error enum with chained context for IO, procfs, nix, string, and DM failures.

## Notes
Requires host tools such as `mkfs.xfs`, `xfs_admin`, and `udevadm` for relevant tests.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/testing/test_lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/thindev.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/thindev.rs

## Purpose
Implements high-level `dm-thin` device wrapper, status parsing, snapshot creation, table changes, and destruction of thin IDs from a thin pool.

## Key Types
`ThinTargetParams`, `ThinDevTargetTable`, `ThinDev`, `ThinDevWorkingStatus`, and `ThinStatus`.

## Behavior
Target params parse `thin <pool> <thin_id> [external_origin]`. `ThinDev::new` sends `create_thin` to the pool, rejects pre-existing names, creates a one-line thin table, and activates it. `setup` validates or creates a device for an already-known thin ID. `snapshot` suspends source, sends `create_snap`, resumes source, and creates a new thin device with the snapshot ID. `destroy` removes the DM device and sends `delete <thin_id>` to the pool.

## Status
`ThinStatus` handles `Error`, `Fail`, or working status with mapped sector count and optional highest mapped sector; zero mapped sectors means no highest sector.

## Tests/Notes
Loopback/XFS tests cover zero-size failure, setup without prior pool ID failure, basic idempotency, udev symlinks, snapshots, filesystem writes increasing pool usage, snapshot copy-on-write usage, and destroy semantics.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/thindev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/thindevid.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/thindevid.rs

## Purpose
Defines `ThinDevId`, the 24-bit identifier used by dm-thin pools.

## Key APIs
`ThinDevId::new_u64`, `From<ThinDevId> for u32`, `Display`, `FromStr`, serde serialize/deserialize.

## Behavior
`new_u64` accepts values below `2^24` and rejects larger values with `DmError::Dm(ErrorEnum::Invalid, ...)`. Parsing uses shared `parse_value`.

## Notes
Serde deserialization currently wraps the deserialized `u32` directly and does not re-check the 24-bit limit.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/thindevid.rs -->