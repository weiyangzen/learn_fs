# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/uefi.c

## Purpose
Implements EFI/UEFI variable access for Intel wireless platform data. It retrieves PNVM/reduced-power blobs and parses UEFI regulatory/configuration tables into transport and firmware-runtime state.

## Important APIs, Types, and Functions
Core helpers are `iwl_uefi_get_variable()`, `iwl_uefi_get_verified_variable_guid()`, and `iwl_uefi_get_verified_variable()`. Public APIs include `iwl_uefi_get_pnvm`, `iwl_uefi_get_reduced_power`, `iwl_uefi_reduce_power_parse`, `iwl_uefi_handle_tlv_mem_desc`, `iwl_uefi_get_step_table`, `iwl_uefi_get_sgom_table`, `iwl_uefi_get_uats_table`, `iwl_uefi_get_uneb_table`, SAR/GEO/PPAG/TAS getters, `iwl_uefi_get_dsm`, `iwl_uefi_get_puncturing`, `iwl_uefi_get_dsbr`, and `iwl_uefi_get_phy_filters`.

## Control Flow
Variable retrieval first probes EFI size, allocates a buffer, then reads the value. Most table getters validate minimum size and exact revision/size before copying into `fwrt`. Reduced-power parsing scans TLVs for matching SKU, then collects MEM_DESC chunks until the next SKU marker. Regulatory paths parse WRDS/EWRD SAR, WGDS geo offsets, PPAG gains, WTAS TAS options, MCC, power limit, DSM function values, puncturing bits, DSBR flags, and WPFC chain filters.

## State and Persistence Behavior
UEFI values are persistent platform firmware variables. The driver copies or caches their contents in `trans->conf`, `fwrt->sar_profiles`, `geo_profiles`, `ppag_chains`, `tas_data`, `dsm_values`, `ap_type_cmd`, `sgom_table`, `phy_filters`, and PNVM buffers. Allocated UEFI buffers are freed after parsing except returned PNVM/reduced-power blobs, whose ownership passes to callers.

## Dependencies and Integration Points
Depends on Linux EFI runtime services, `fw/uefi.h` packed layouts, PNVM TLV definitions, firmware runtime regulatory state, and debug logging. It integrates with firmware boot, regulatory initialization, reduced-power PNVM selection, and integrated-platform STEP/DSBR setup.

## Risks
This code trusts platform firmware but must defend against malformed sizes, unsupported revisions, and out-of-range counts. PNVM TLV parsing uses caller-owned blob pointers, so lifetime must outlive firmware upload. Regulatory mistakes can alter legal transmit power or channel availability. DSM caching uses zero as "not loaded", so failed UEFI DSM deliberately allows ACPI fallback.

## Test Signals
No EFI support, EFI service unavailable, missing variables, short variables, wrong revisions, WRDS/EWRD rev 2/3, WGDS rev 3/4 profile limits, PPAG rev 4/5 fallback, WTAS block-list overflow, SKU-matched and unmatched reduced-power blobs, DSM function bitmap caching, China-only WRDD, DSBR bits, WPFC chains, and memory leak checks are important.
