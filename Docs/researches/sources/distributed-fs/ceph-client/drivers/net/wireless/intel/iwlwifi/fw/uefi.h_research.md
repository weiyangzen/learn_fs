# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/uefi.h

## Purpose
Defines UEFI variable names, expected revisions, packed table layouts, size formulas, and EFI/no-EFI function contracts for iwlwifi platform data.

## Important APIs, Types, and Functions
Important names include PNVM, reduced power, SGOM, STEP, UATS/UNEB, WRDS/EWRD/WGDS, PPAG, WTAS, SPLC, WRDD, ECKV, DSM, WBEM, puncturing, DSBR, and WPFC. Packed layouts include `pnvm_sku_package`, `uefi_cnv_var_wrds`, `uefi_cnv_var_ewrd`, `uefi_cnv_var_wgds`, `uefi_cnv_var_ppag`, `uefi_cnv_var_wtas`, `uefi_cnv_var_general_cfg`, `uefi_cnv_wlan_dsbr_data`, and `uefi_cnv_wpfc_data`.

## Control Flow
The header has no runtime logic beyond `CONFIG_EFI` stubs. With EFI enabled it declares real functions implemented by `uefi.c`; without EFI it returns `-EOPNOTSUPP`, `-ENOENT`, zero/default values, or no-op table getters so callers can compile and fallback cleanly.

## State and Persistence Behavior
The packed structs describe persistent UEFI variable ABI. Size macros are part of validation and must remain synchronized with firmware/BIOS layout revisions.

## Dependencies and Integration Points
Includes `fw/regulatory.h` for shared table bounds and DSM enums. It is consumed by UEFI parsing, PNVM handling, firmware runtime regulatory setup, and integrated CNV platform configuration.

## Risks
Packed layout and revision constants are ABI-sensitive. Any mismatch can parse table bytes incorrectly. Stub return codes influence fallback behavior, so changing them can break non-EFI platforms or ACPI fallback.

## Test Signals
Builds with `CONFIG_EFI=y/n`, static layout/size checks, each variable revision, no-EFI fallback paths, and consistency between size macros and parser exact-size checks are useful signals.
