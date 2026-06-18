# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.c

Purpose: loads platform regulatory BIOS/UEFI data into firmware runtime state and sends SAR, geo SAR, SGOM, PPAG, LARI, AP type, and TAS commands to firmware.

Important APIs/functions: `iwl_mld_get_bios_tables()`, `iwl_mld_config_sar_profile()`, `iwl_mld_init_sar()`, `iwl_mld_init_sgom()`, `iwl_mld_init_ppag()`, `iwl_mld_configure_lari()`, `iwl_mld_init_ap_type_tables()`, and `iwl_mld_init_tas()`. Static helpers select geo SAR command version, send PPAG v7/v8 payloads, and derive LARI config bitmaps from DSM values.

Control flow: BIOS loading obtains GUID lock status, PPAG, WRDS/EWRD/WGDS, UEFI UATS/UNEB, and PHY filters, with WRDS absence suppressing geo SAR use. SAR init chooses default or user profiles, sends chain limits, and then geo tables if SAR is enabled. SGOM/PPAG are sent only when enabled/approved. LARI collects many DSM/WBEM feature bitmaps, masks them unless firmware accepts raw DSM, skips command if all fields are zero, and uses a shortened command for version 12. TAS requires firmware capability and BIOS table, then adjusts US/Canada block list unless DMI vendor is approved.

State and persistence: reads and populates `mld->fwrt` runtime regulatory fields such as table revisions/sources, SAR profiles, PPAG chains/flags, SGOM table, DSM metadata, AP type map, TAS data, and PHY filters. Persistent source is platform BIOS/UEFI; driver state is in memory.

Dependencies and integration: depends on `fw/regulatory.h`, ACPI, UEFI, DMI, host-command wrappers, firmware command-version lookup, and shared regulatory fill/approval helpers.

Risks and test signals: command versions 5/6, 7/8, 10/11, and LARI v12/newer have distinct layouts; table revision compatibility can silently skip PPAG send; positive SAR fill return means disabled profile and must not be treated as fatal. Tests should cover missing WRDS with WGDS present, unsupported command versions, raw DSM capability masking, TAS vendor block list growth, and command length selection.
