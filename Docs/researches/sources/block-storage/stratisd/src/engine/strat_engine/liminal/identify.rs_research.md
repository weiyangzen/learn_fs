# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/identify.rs

This file discovers and classifies block devices that may belong to Stratis.

Key responsibilities:
- Defines raw discovery structs: `StratisDevInfo`, `LuksInfo`, `StratisInfo`, and `DeviceInfo`.
- Converts existing V1/V2 blockdev objects into `DeviceInfo`.
- Reads Stratis BDA metadata from device nodes through `bda_wrapper()`.
- Processes udev-identified LUKS devices by loading Stratis LUKS metadata through `CryptHandle::load_metadata()`.
- Processes udev-identified Stratis devices by reading BDA metadata and device numbers.
- Enumerates all Stratis-owned LUKS devices and all Stratis filesystem-type devices using libudev filters.
- Identifies a single block device from a udev event.

Important behavior:
- Initial enumeration uses udev filesystem type filters: crypto/LUKS for Stratis-owned LUKS devices and Stratis fs type for Stratis metadata devices.
- Ownership is rechecked with `decide_ownership()` to avoid acting on multipath members or unrelated devices.
- Uninitialized udev entries are ignored.
- Errors during metadata reads are logged and cause the specific device to be ignored rather than aborting enumeration.
- Public `find_all()` returns two maps keyed by pool UUID: LUKS infos and Stratis infos.

Tests:
- Tests cover uninitialized/non-Stratis devices, initialized legacy encrypted devices, initialized legacy unencrypted devices, and initialized V2 devices across loopback and real-device harnesses.
