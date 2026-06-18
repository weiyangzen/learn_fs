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
