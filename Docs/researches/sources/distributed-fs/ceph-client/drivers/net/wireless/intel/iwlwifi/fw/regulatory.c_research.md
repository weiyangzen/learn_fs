<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.c

Purpose: BIOS/UEFI regulatory data retrieval and policy helpers for SAR, PPAG, TAS, puncturing, and RFI.

Important APIs/functions: macro-generated `iwl_bios_get_*()` functions prefer UEFI tables when unlocked and fall back to ACPI. Exported helpers include `iwl_sar_geo_support()`, `iwl_sar_geo_fill_table()`, `iwl_sar_fill_profile()`, `iwl_is_ppag_approved()`, `iwl_bios_print_ppag()`, `iwl_is_tas_approved()`, `iwl_parse_tas_selection()`, `iwl_add_mcc_to_tas_block_list()`, `iwl_bios_get_dsm()`, `iwl_puncturing_is_allowed_in_bios()`, and `iwl_rfi_is_enabled_in_bios()`.

Control flow: table loaders use UEFI if `fwrt->uefi_tables_lock_status` permits, else ACPI. SAR GEO support is inferred from firmware serial and specific hardware exceptions. SAR filling rejects disabled profile 0, out-of-range profile ids, disabled profiles, and oversized subband counts. PPAG/TAS approval checks DMI allowlists. Puncturing is restricted for US/Canada unless BIOS bits allow it. RFI reads DSM and accepts only valid enable/disable encodings.

State and persistence: reads BIOS/UEFI into `fwrt` fields through lower helpers and fills command buffers from `fwrt->sar_profiles`, `geo_profiles`, `ppag_*`, and TAS data. It may clear `fwrt->ppag_flags` on unapproved systems.

Dependencies/integration: depends on ACPI/UEFI helpers, DMI, runtime regulatory fields, firmware version macros, DSM enums, and command payload structs.

Risks/test signals: regulatory behavior is policy-sensitive. Test UEFI locked/unlocked fallback, DMI allowlist matches, SAR version exceptions, disabled SAR profiles, PPAG flag clearing, TAS table revisions, MCC block-list capacity, US/Canada puncturing bits, and invalid DSM RFI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.c -->
