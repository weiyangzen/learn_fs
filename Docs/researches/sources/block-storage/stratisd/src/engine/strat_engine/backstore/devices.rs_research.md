# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/devices.rs

Read status: complete, 1594 lines.

## Purpose

`devices.rs` is the Stratis backstore device discovery and initialization gate. It converts user-provided paths into verified device records, separates already-owned Stratis devices from unowned devices, initializes new Stratis metadata, and wipes initialized block devices during rollback or disown operations.

The file supports both legacy v1 encrypted block devices and newer v2 block devices.

## Main Types

- `BlockSizes`: physical and logical sector sizes read from a block device.
- `DeviceInfo`: device number, canonical path, optional `ID_WWN`, size, and block sizes.
- `StratisDevices`: map of Stratis-owned devices grouped by `PoolUuid` and `DevUuid`.
- `ProcessedPathInfos`: result of path processing, split into Stratis-owned and unclaimed devices.
- `UnownedDevices`: verified devices suitable for Stratis initialization.

## Discovery And Validation Flow

`ProcessedPathInfos::try_from(&[&Path])` is the main entry point for path processing.

It:

1. Canonicalizes inputs through `DevicePath::new`.
2. Deduplicates paths.
3. Calls `dev_info`.
4. Enforces the minimum device size of 1 GiB through `check_dev`.
5. Rejects duplicate device numbers.
6. Splits devices into:
   - `stratis_devices`, keyed by pool/device UUID from Stratis metadata.
   - `unclaimed_devices`, with no Stratis identifiers.

`dev_info` combines udev and blkid:

- `udev_info` reads ownership, device number, and optional `ID_WWN`.
- Devices identified as `Luks`, `MultipathMember`, or `Theirs` are rejected.
- Devices identified as `Stratis` or `Unowned` are additionally checked with blkid.
- `verify_device_with_blkid` enables superblock and partition probing, then rejects devices with partitions or unrelated superblocks.
- `device_identifiers` reads Stratis BDA metadata and must agree with udev if udev reported Stratis ownership.

## Public Helpers

- `get_devno_from_path`: uses `stat` and converts `st_rdev` into a devicemapper `Device`.
- `find_stratis_devs_by_uuid`: scans libblkid cache for Stratis devices matching a pool UUID and a target device UUID list. This is explicitly a workaround for cases where udev events cannot be processed due to internal stratisd locking.
- `get_logical_sector_size`: queries blkid topology for logical sector size.
- `wipe_blockdevs`: best-effort disown over `InternalBlockDev` instances, collecting failures into `BestEffortError`.

## Initialization Behavior

`initialize_devices_legacy` initializes v1 block devices. It supports encryption through `CryptHandle::initialize`.

For encrypted v1 devices:

- A LUKS2 device is initialized.
- Logical encrypted device size is read.
- Stratis BDA metadata is written to the activated metadata path.
- Hardware ID is discarded because encrypted devices are represented by devicemapper nodes.
- Failure after LUKS initialization triggers `CryptHandle::wipe`.

For unencrypted v1 devices:

- BDA metadata is written directly to the physical path.
- Failure triggers `disown_device`.

`initialize_devices` initializes v2 block devices. It writes v2 BDA metadata directly to device paths and constructs `v2::StratBlockDev`; encryption is not part of this function.

Both initialization paths use the global `BLOCKDEVS_IN_PROGRESS` mutex-protected set to reject concurrent initialization attempts involving the same paths.

## Rollback Semantics

Initialization is transactional at the batch level as far as practical:

- If one device fails to initialize, previously initialized devices in the batch are passed to `wipe_blockdevs`.
- Cleanup failures are logged and wrapped as rollback errors where applicable.
- The in-progress path set is always cleaned after initialization returns.

## Tests

The tests cover:

- Nonexistent paths produce errors rather than panics.
- Duplicate devnodes are deduplicated.
- v1 ownership behavior with and without encryption.
- v1 cleanup after failure, including LUKS metadata cleanup.
- v2 ownership behavior.
- v2 cleanup after failure.
- Loopback and real-device variants are used for many cases.
- Crypt tests depend on key insertion helpers and real/loopback device harnesses.

## Notable Dependencies

- udev ownership helpers from `strat_engine::udev`.
- blkid probing through `libblkid_rs`.
- device sizing and sector size helpers from `strat_engine::device`.
- metadata initialization and disowning from `strat_engine::metadata`.
- v1 encryption through `crypt::handle::v1::CryptHandle`.

## Important Invariants

- Device paths in `ProcessedPathInfos` are unique.
- Device numbers in `ProcessedPathInfos` are unique.
- Device sizes must be at least 1 GiB.
- Devices with partitions or non-Stratis superblocks are not considered unowned.
- Duplicate Stratis identifiers across paths are rejected.
