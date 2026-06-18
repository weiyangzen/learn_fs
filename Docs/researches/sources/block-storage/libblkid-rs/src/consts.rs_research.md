# File Research: sources/block-storage/libblkid-rs/src/consts.rs

Purpose: Defines typed Rust enums and flag-set wrappers for libblkid integer constants.

Key APIs:
- Device cache flags: `BlkidDevFlag`, `BlkidDevFlags`
- Usage flags: `BlkidUsageFlag`, `BlkidUsageFlags`
- Superblock flags: `BlkidSublks`, `BlkidSublksFlags`
- Filter constants: `BlkidFltr`
- Probe return enums: `BlkidProbeRet`, `BlkidSafeprobeRet`, `BlkidFullprobeRet`
- Probe request flags: `BlkidProbreqFlag`, `BlkidProbreqFlags`

Implementation notes:
- Uses `consts_enum_conv!` and `flags!` macros from `macros.rs`.
- Constants are mostly direct casts from `libblkid_rs_sys`.

Notable risks:
- `BlkidSublks::Uuidraw` maps to `BLKID_SUBLKS_UUID`; it likely should map to `BLKID_SUBLKS_UUIDRAW`.
- Flag parsing depends on the `flags!` macro, whose `TryFrom` implementation appears to reject unset bits by trying to convert `0` repeatedly.
- Documentation for `BlkidUsageFlags` says it is a set of `BlkidDevFlag`, but it actually wraps `BlkidUsageFlag`.
