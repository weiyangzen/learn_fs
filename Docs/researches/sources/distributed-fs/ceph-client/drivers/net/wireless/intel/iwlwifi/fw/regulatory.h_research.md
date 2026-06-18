# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.h

## Purpose
Defines iwlwifi firmware-runtime regulatory data contracts for BIOS/UEFI/ACPI power-limit tables: SAR, GEO, PPAG, TAS, DSM, puncturing, DSBR, RFI, and PHY filters. It is the shared header used by firmware runtime code and platform-table parsers to normalize platform regulatory policy before firmware commands are built.

## Important APIs, Types, and Functions
Important constants size platform tables, including `BIOS_SAR_MAX_PROFILE_NUM`, `BIOS_SAR_MAX_SUB_BANDS_NUM`, `BIOS_GEO_MAX_PROFILE_NUM`, and PPAG/TAS masks. Core data types are `iwl_sar_profile`, `iwl_geo_profile`, `iwl_ppag_chain`, `iwl_tas_data`, and `iwl_tas_selection_data`. Exported contracts include `iwl_bios_get_wrds_table`, `iwl_bios_get_ewrd_table`, `iwl_bios_get_wgds_table`, `iwl_bios_get_ppag_table`, `iwl_bios_get_tas_table`, `iwl_bios_get_dsm`, `iwl_sar_fill_profile`, `iwl_sar_geo_fill_table`, `iwl_bios_get_phy_filters`, and `iwl_bios_setup_step`.

## Control Flow
This header has no standalone runtime path. Consumers call the table getters during firmware/runtime initialization, then fill firmware command payloads from the normalized `iwl_fw_runtime` fields. `iwl_bios_get_ppag_flags()` gates old PPAG revisions to the supported bit subset. `iwl_bios_setup_step()` conditionally reads DSBR only for integrated BZ-or-newer devices and stores URM behavior in `trans->conf`.

## State and Persistence Behavior
The state described here is platform policy persisted in BIOS/UEFI/ACPI tables and cached into `struct iwl_fw_runtime`. DSM values are cached by function bitmap. SAR/GEO/PPAG/TAS data affects regulatory transmit power and channel behavior until runtime is reinitialized.

## Dependencies and Integration Points
Depends on firmware API headers, `iwl-trans.h`, and `struct iwl_fw_runtime`. It integrates with `fw/uefi.c`, ACPI regulatory code, MVM regulatory setup, and firmware power/config commands.

## Risks
Array bounds and revision handling are the main risks: a platform table with more profiles, chains, or subbands than expected must be rejected or clipped before firmware command construction. Regulatory masks are policy-sensitive, so accepting unsupported bits can enable forbidden channels or power behavior.

## Test Signals
Compile coverage with EFI and ACPI enabled/disabled, SAR WRDS/EWRD revisions, GEO WGDS profile bounds, PPAG revisions 1-5, TAS block-list limits, DSM function 5 rejection, China WRDD MCC handling, DSBR URM bits, puncturing masks, and firmware command payload validation are useful signals.
