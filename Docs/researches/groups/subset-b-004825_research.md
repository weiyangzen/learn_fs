# subset-b-004825 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/rs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/rs.c

## Purpose
Provides firmware rate-scaling formatting and lookup helpers. It translates firmware legacy rate indexes to PLCP values, exposes rate/MCS descriptive strings, formats `rate_n_flags` values for diagnostics, and detects HE short guard interval encodings.

## Important APIs, Types, and Functions
Tables include `fw_rate_idx_to_plcp`, `rate_mcs`, `ant_name`, and `pretty_bw`. Exported functions are `iwl_fw_rate_idx_to_plcp`, `iwl_rate_mcs`, `iwl_rs_pretty_ant`, `iwl_rs_pretty_bw`, `rs_pretty_print_rate`, and `iwl_he_is_sgi`.

## Control Flow
The lookup helpers index static arrays. `rs_pretty_print_rate()` decodes antenna, channel width, modulation type, MCS, NSS, SGI/NGI, STBC, LDPC, DCM, and beamforming. Legacy OFDM/CCK rates return early with Mbps text; HT/VHT/HE/EHT use unified formatting.

## State and Persistence Behavior
The file stores only immutable tables. Its output is diagnostic text and does not persist state or modify firmware behavior.

## Dependencies and Integration Points
Depends on mac80211 types, `fw/api/rs.h`, and rate constants from iwlwifi firmware APIs. It is used by debugfs/logging paths in MVM and firmware tracing.

## Risks
Inputs are assumed to be valid indexes in `iwl_fw_rate_idx_to_plcp()` and `iwl_rate_mcs()`, so callers must validate firmware indexes. `rs_pretty_print_rate()` must track new `RATE_MCS_*` encodings, especially EHT/320 MHz additions.

## Test Signals
Unit-style coverage for every legacy rate index, invalid antenna/bandwidth display, CCK/OFDM/HT/VHT/HE/EHT formatting, HE GI/LTF combinations, and buffer-size truncation behavior would catch most regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/runtime.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/runtime.h

## Purpose
Declares the central firmware runtime object shared by iwlwifi opmodes. It binds a transport, parsed firmware image, paging state, shared-memory layout, dump workers, UEFI/BIOS regulatory caches, timestamp/debug state, and runtime operations.

## Important APIs, Types, and Functions
Important types are `iwl_fw_runtime_ops`, `iwl_fwrt_shared_mem_cfg`, `iwl_fwrt_dump_data`, `iwl_fwrt_wk_data`, `iwl_txf_iter_data`, and `iwl_fw_runtime`. Public lifecycle/control functions include `iwl_fw_runtime_init`, `iwl_fw_runtime_free`, `iwl_fw_runtime_suspend`, `iwl_fw_runtime_resume`, `iwl_fw_set_current_image`, `iwl_init_paging`, `iwl_free_fw_paging`, `iwl_get_shared_mem_conf`, `iwl_set_soc_latency`, and `iwl_configure_rxq`.

## Control Flow
The header describes runtime state; implementation code initializes it before firmware interaction, updates `cur_fw_img` as images change, queries shared memory after alive, allocates paging, and frees timers/workers during teardown. `iwl_fw_runtime_free()` cancels dump workers and debug timers.

## State and Persistence Behavior
Most fields are in-memory caches derived from firmware, UEFI/ACPI, or module configuration. Paging DMA blocks, shared-memory FIFO sizes, DSM values, SAR/GEO/PPAG tables, and debug worker state persist for the lifetime of the active firmware runtime.

## Dependencies and Integration Points
Depends on `iwl-config.h`, `iwl-trans.h`, firmware image/debug/paging/power APIs, NVM utilities, ACPI helpers, and regulatory contracts. It is consumed by MVM/MLD runtime, debug collection, paging, RX queue setup, and regulatory command code.

## Risks
Teardown ordering is sensitive: delayed dump workers and periodic debug timers must be stopped before transport memory disappears. Many cached arrays mirror firmware/BIOS maxima, so table parsers must respect the declared bounds.

## Test Signals
Firmware runtime init/free across normal load, failed load, suspend/resume, D3 debug, paging allocation/free, shared-memory command parsing, debug dump worker cancellation, EFI/ACPI regulatory table population, and no-EFI builds are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/runtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/smem.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/smem.c

## Purpose
Queries firmware for shared-memory configuration and caches FIFO sizes and internal TX FIFO information in `iwl_fw_runtime`.

## Important APIs, Types, and Functions
The exported API is `iwl_get_shared_mem_conf()`. Internal parsers are `iwl_parse_shared_mem_22000()` for 22000/newer multi-LMAC formats and `iwl_parse_shared_mem()` for older shared-memory notifications.

## Control Flow
`iwl_get_shared_mem_conf()` selects `WIDE_ID(SYSTEM_GROUP, SHARED_MEM_CFG_CMD)` when extended shared-memory capability exists, otherwise the legacy `SHARED_MEM_CFG`. It sends a synchronous command with `CMD_WANT_SKB`, dispatches to the parser based on device family, logs success, and frees the response.

## State and Persistence Behavior
The command response fills `fwrt->smem_cfg`: LMAC count, TX FIFO entries, per-LMAC TX/RX FIFO sizes, RX FIFO 2 size, optional RX FIFO 2 control size, and internal TX FIFO address/sizes. The cache lasts for the firmware runtime and drives debug/TX FIFO iteration.

## Dependencies and Integration Points
Depends on `iwl_trans_send_cmd`, response SKB ownership, firmware notification version lookup, capability checks, and shared-memory structures from `fw/api/commands.h`.

## Risks
Bad firmware lengths or advertised LMAC counts must not overflow `MAX_NUM_LMAC`. The 22000 parser only reads `rxfifo2_control_size` when notification version and payload length allow it. RF-kill failures are tolerated without warning.

## Test Signals
Legacy and extended command IDs, 22000 multi-LMAC parsing, payload-short warning, invalid LMAC count, RF-kill command failure, internal TX FIFO capability presence/absence, and response freeing are the main test points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/smem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/uefi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/uefi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/uefi.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/uefi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-agn-hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-agn-hw.h

## Purpose
Defines legacy AGN hardware constants: RTC instruction/data memory bounds, RSSI offset, retry defaults, transmit-power range, EEPROM/OTP image sizing, and queue count.

## Important APIs, Types, and Functions
Important macros include `IWLAGN_RTC_INST_*`, `IWLAGN_RTC_DATA_*`, `IWL60_RTC_*`, `IWLAGN_RSSI_OFFSET`, retry limits, `IWLAGN_TX_POWER_TARGET_POWER_MIN/MAX`, OTP high/low limits, and `IWLAGN_NUM_QUEUES`.

## Control Flow
No executable flow. Firmware loading and legacy DVM code use these constants to place and size firmware sections and configure old-device retry/power defaults.

## State and Persistence Behavior
All values are compile-time hardware ABI constants. They influence firmware image placement and hardware queue sizing but do not store runtime state.

## Dependencies and Integration Points
Included by `iwl-drv.c` for legacy firmware section offsets and by older AGN/DVM code.

## Risks
Changing addresses or sizes can make firmware uploads land outside RTC memory on legacy devices. Retry/power constants affect behavior across old hardware families.

## Test Signals
DVM firmware load on 5000/6000-era devices, section-size validation, EEPROM/OTP reads, queue setup, and RSSI/power calculations are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-agn-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-config.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-config.h

## Purpose
Declares device-family, MAC, RF, firmware API, antenna, NVM, thermal, EEPROM, and device-ID configuration contracts used to bind PCI hardware to firmware and opmode behavior.

## Important APIs, Types, and Functions
Important enums include `iwl_device_family`, `iwl_led_mode`, `iwl_nvm_type`, and `iwl_mac_cfg_ltr_delay`. Core structs are `iwl_family_base_params`, `iwl_ht_params`, `iwl_tt_params`, `iwl_eeprom_params`, `iwl_pwr_tx_backoff`, `iwl_mac_cfg`, `iwl_rf_cfg`, and `iwl_dev_info`. Helpers/macros include antenna masks, `num_of_ant()`, firmware filename macros, core/API version conversions, MAC/RF type constants, subdevice extractors, and `iwl_pci_find_dev_info()`.

## Control Flow
The header itself is declarative. Probe code selects a `iwl_dev_info` and config pointers, firmware loading combines MAC/RF API ranges, and opmodes use the flags to size queues, choose NVM parsing, enable capabilities, and apply workarounds.

## State and Persistence Behavior
Config structures are static immutable driver data. They determine runtime allocations, feature flags, firmware filename selection, thermal behavior, and hardware workarounds for each device lifetime.

## Dependencies and Integration Points
Depends on Linux networking, PCI modalias types, `iwl-csr.h`, and `iwl-drv.h`. It is central to PCI ID matching, firmware loading, MVM/DVM/MLD selection, NVM parsing, transport setup, and feature gating.

## Risks
Incorrect API ranges or firmware prefixes cause firmware load failures. Wrong antenna, NVM, queue, or memory limits can break radio capability reporting or DMA sizing. Device match masks must be precise enough to avoid binding a device to an incompatible RF config.

## Test Signals
PCI ID matching, generated firmware filenames, core/API fallback, old and new device families, CDB/bandwidth/subdevice matching, NVM parsing modes, antenna counts, Wi-Fi 7 MLD selection, and KUnit coverage of device info tables are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-csr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-csr.h

## Purpose
Defines control/status register addresses, bit masks, hardware revision extractors, interrupt causes, reset/power bits, mailbox bits, internal HBUS access registers, MSI-X registers, and MAC address CSR offsets for iwlwifi hardware.

## Important APIs, Types, and Functions
Key macro groups cover CSR base registers, `CSR_HW_REV`, `CSR_HW_RF_ID`, EEPROM/OTP, `CSR_GP_CNTRL`, reset, interrupt masks, LTR, IPC sleep/reset, BZ doorbell/status bits, HBUS memory/periphery access, host interrupt timeout, DTS diode fields, MSI-X causes, and MAC address CSR access. Extractors include `CSR_HW_REV_TYPE`, `CSR_HW_RFID_TYPE`, `CSR_HW_RFID_STEP`, `CSR_HW_RFID_IS_CDB`, and silicon-step enums.

## Control Flow
No direct execution. Transport and PCI code use these constants to reset devices, arbitrate MAC access, read identity, handle interrupts, configure MSI-X, access OTP/EEPROM, write memory/periphery windows, and detect RF-kill or power state.

## State and Persistence Behavior
The file maps hardware-visible registers and bitfields. Register contents are live device state, while the macros are static ABI.

## Dependencies and Integration Points
Used by `iwl-io.c`, PCI transport, interrupt handlers, firmware loader, NVM readers, power management, and firmware filename selection.

## Risks
Register definitions are hardware ABI. Wrong bits can corrupt reset/power sequencing, interrupt acknowledgement, bus mastering, or RF identification. Some registers are accessible while MAC is asleep and others require NIC access, so consumers must obey access rules documented here.

## Test Signals
Probe identity reads, reset and stop-master flows, RF-kill interrupts, MSI-X and legacy interrupt paths, EEPROM/OTP reads, BZ MAC access, LTR programming, MAC address reads, and suspend/resume IPC transitions are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-dbg-tlv.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-dbg-tlv.c

## Purpose
Implements the INI debug TLV framework: parsing debug TLVs from firmware or external debug binaries, allocating monitor buffers, activating triggers by time point, applying debug configuration, sending debug host commands, and scheduling periodic debug collections.

## Important APIs, Types, and Functions
Public functions are `iwl_dbg_tlv_alloc`, `iwl_dbg_tlv_load_bin`, `iwl_dbg_tlv_init`, `iwl_dbg_tlv_free`, `iwl_dbg_tlv_del_timers`, `iwl_dbg_tlv_init_cfg`, and `_iwl_dbg_tlv_time_point`. Internal logic covers version validation, debug-info/buffer/hcmd/region/trigger/config TLV allocation, DRAM fragment allocation/application/update, active-trigger generation/override, periodic timer setup, and trigger-time collection.

## Control Flow
Firmware parse calls `iwl_dbg_tlv_alloc()` for internal TLVs and optional `iwl-debug-yoyo.bin` data. Initialization creates lists per time point. `iwl_dbg_tlv_init_cfg()` generates active trigger lists and allocates/clears DRAM buffers. `_iwl_dbg_tlv_time_point()` reacts to early, after-alive, periodic, firmware response, missed beacon, DHC notification, and default points by sending host commands, applying config, enabling timers, or collecting dumps.

## State and Persistence Behavior
State is kept under `trans->dbg`: TLV lists, active regions, monitor allocation configs, DRAM fragments, periodic timers, active triggers, domains bitmap, unsupported-region mask, reset/restart flags, and INI destination. DMA buffers persist until `iwl_dbg_tlv_free()`.

## Dependencies and Integration Points
Depends on firmware TLV ABI, transport command/register/memory APIs, DMA coherent allocation, timers, debug dump collection (`iwl_fw_dbg_ini_collect`), module parameter `enable_ini`, and firmware capabilities such as DRAM fragment support.

## Risks
This code is memory- and lifecycle-sensitive. TLV lengths, versions, domains, allocation IDs, trigger occurrences, and region IDs must be validated. Timer shutdown must happen before freeing TLVs. DRAM allocation partial failure must disable dependent regions. Config writes can touch CSR, PRPH, and device memory, so malformed debug configs are high impact.

## Test Signals
Internal/external TLV parse success and corruption, domain filtering, duplicate region override, DRAM allocation fallback and cleanup, unsupported allocation-region masking, after-alive buffer application, periodic trigger minimum interval and shutdown, FW packet trigger matching, reset policy decisions, and module unload with timers active are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-dbg-tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-dbg-tlv.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-dbg-tlv.h

## Purpose
Declares the public interface and list-node types for iwlwifi INI debug TLVs.

## Important APIs, Types, and Functions
Defines `IWL_DBG_TLV_MAX_PRESET`, `ENABLE_INI`, `iwl_dbg_tlv_node`, `iwl_dbg_tlv_tp_data`, and `iwl_dbg_tlv_time_point_data`. Declares load, alloc, init, free, timer deletion, configuration initialization, and synchronous/asynchronous time-point helpers.

## Control Flow
Inline wrappers call `_iwl_dbg_tlv_time_point()` with `sync=false` or `sync=true`; all other control flow is in `iwl-dbg-tlv.c`.

## State and Persistence Behavior
The header defines list containers for copied TLVs and active triggers. Actual ownership is in `trans->dbg`.

## Dependencies and Integration Points
Depends on firmware file/TLV definitions and debug TLV API structs. It is consumed by firmware parsing, runtime teardown, and debug time-point callers across opmodes.

## Risks
The flexible `iwl_ucode_tlv` node layout depends on allocations sized by TLV length. Time-point list initialization must match the arrays in transport debug state.

## Test Signals
Compile coverage with INI enabled/disabled, time-point wrapper calls, timer deletion during runtime free, and firmware parse invoking `iwl_dbg_tlv_alloc()` are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-dbg-tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.c

## Purpose
Implements iwlwifi logging wrappers that route warning/info/critical/error/debug messages to the kernel device log and iwlwifi tracepoints.

## Important APIs, Types, and Functions
Exports `__iwl_warn`, `__iwl_info`, `__iwl_crit`, `__iwl_err`, and conditionally `__iwl_dbg`. `__iwl_err()` supports regular, RFKILL-prefixed, trace-only, and ratelimited modes. `__iwl_dbg()` checks debug masks and trace support.

## Control Flow
Variadic wrappers package messages in `struct va_format`. Errors optionally print to `dev_err()` depending on mode and ratelimit, then always emit the tracepoint. Debug prints go to `dev_printk(KERN_DEBUG)` only when `CONFIG_IWLWIFI_DEBUG` and level match, then emit debug tracepoint.

## State and Persistence Behavior
No persistent state except reading `iwlwifi_mod_params.debug_level` indirectly. Output persists in kernel logs or tracing buffers.

## Dependencies and Integration Points
Depends on Linux device logging, `net_ratelimit()`, exported symbol namespace helpers, and tracepoints from `iwl-devtrace.h`.

## Risks
Varargs are consumed twice in error paths using `va_copy`; mistakes here would corrupt log output. Trace-only errors intentionally skip device log output but still trace.

## Test Signals
Regular/RFKILL/ratelimited/trace-only errors, debug enabled/disabled builds, device tracing enabled/disabled builds, newline macro enforcement at call sites, and tracepoint message capture are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.h

## Purpose
Defines the iwlwifi logging/debug macro surface and debug-level bit taxonomy.

## Important APIs, Types, and Functions
Important pieces are `iwl_have_debug_level()`, `enum iwl_err_mode`, low-level declarations, `CHECK_FOR_NEWLINE`, `IWL_ERR`, `IWL_WARN`, `IWL_INFO`, `IWL_CRIT`, `IWL_DEBUG*`, hex dump helpers, and debug masks from `IWL_DL_INFO` through `IWL_DL_TX_QUEUES`.

## Control Flow
Macros validate literal format strings end in newline, resolve a module/transport object to `dev`, and dispatch to low-level implementations. Debug macros compile to no-op device printing when debug support is disabled, while tracing can still keep `__iwl_dbg()` available.

## State and Persistence Behavior
Debug-level state is the module parameter `debug_level`. Logs and trace events are external outputs.

## Dependencies and Integration Points
Depends on `iwl-modparams.h`, device logging implementation in `iwl-debug.c`, and trace definitions. Used by almost every iwlwifi file.

## Risks
The macros assume the first argument has a `dev` member unless using `_DEV` variants. `CHECK_FOR_NEWLINE` requires compile-time string literals. Debug bit additions must avoid collisions.

## Test Signals
Builds with/without `CONFIG_IWLWIFI_DEBUG` and device tracing, call-site compile failures for missing newline, ratelimited debug macros, and sysfs/debugfs debug-level toggling are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-data.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-data.h

## Purpose
Declares trace events that capture TX transfer-buffer payload data and RX payload data for iwlwifi device tracing.

## Important APIs, Types, and Functions
Trace events are `iwlwifi_dev_tx_tb` and `iwlwifi_dev_rx_data`. They use `DEV_ENTRY`, `DEV_ASSIGN`, `iwl_trace_data()`, and dynamic trace arrays.

## Control Flow
TX data is copied only when `iwl_trace_data(skb)` allows it, avoiding selected important/control frames. RX data copies bytes after the supplied start offset if `start < len`.

## State and Persistence Behavior
No driver state is mutated. Captured bytes persist only in tracing buffers.

## Dependencies and Integration Points
Included by `iwl-devtrace.h` and compiled through Linux tracepoint infrastructure.

## Risks
Trace data can expose packet payloads, so filtering is important. Incorrect lengths or offsets could over-copy into trace buffers.

## Test Signals
Trace enabled/disabled builds, TX payload filtering for EAPOL/status-request frames, RX data with `start == len` and `start < len`, and trace output decoding are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-io.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-io.h

## Purpose
Declares trace events for iwlwifi MMIO/PRPH IO, IRQ, MSI-X, and ICT reads.

## Important APIs, Types, and Functions
Events include `iwlwifi_dev_ioread32`, `iwlwifi_dev_iowrite8`, `iwlwifi_dev_iowrite32`, `iwlwifi_dev_iowrite64`, `iwlwifi_dev_iowrite_prph32`, `iwlwifi_dev_iowrite_prph64`, `iwlwifi_dev_ioread_prph32`, `iwlwifi_dev_irq`, `iwlwifi_dev_irq_msix`, and `iwlwifi_dev_ict_read`.

## Control Flow
The header is declarative tracepoint code. IO wrappers and interrupt handlers call these tracepoints when device tracing is enabled.

## State and Persistence Behavior
No driver state is changed; register offsets, values, IRQ vector metadata, and interrupt cause snapshots are recorded in tracing buffers.

## Dependencies and Integration Points
Depends on Linux tracepoints and PCI `msix_entry`. Included through `iwl-devtrace.h`.

## Risks
High-volume IO tracing can be expensive. Format strings must match field widths, and interrupt tracepoints must not add heavy work in hot paths.

## Test Signals
MMIO read/write traces, PRPH read/write traces, legacy IRQ trace, MSI-X cause trace, ICT read trace, and disabled-tracing no-op builds are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-iwlwifi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-iwlwifi.h

## Purpose
Declares primary iwlwifi device trace events for host commands, RX packets, TX frames, and firmware event-log entries.

## Important APIs, Types, and Functions
Trace events include `iwlwifi_dev_hcmd`, `iwlwifi_dev_rx`, `iwlwifi_dev_tx`, and `iwlwifi_dev_ucode_event`. They use host command payload arrays, RX trace lengths, TX TFD/buffer snapshots, and firmware event fields.

## Control Flow
Callers supply command or packet metadata; trace fast-assign handlers copy relevant bytes into dynamic arrays. Host command tracing handles wide and legacy headers, and TX tracing filters payload through `iwl_trace_data()`.

## State and Persistence Behavior
Only trace buffers are populated. No device state is modified.

## Dependencies and Integration Points
Included by `iwl-devtrace.h`, used by transport TX/RX/host-command paths and firmware event log dumping.

## Risks
Dynamic-array lengths must match copied bytes. TX/RX tracing can expose frame data if filtering is wrong. Host-command tracing sits on hot paths and should remain lightweight when disabled.

## Test Signals
Wide and non-wide host command traces, multi-buffer command payloads, RX MPDU header-only tracing, TX data filtering, firmware event-log trace, and disabled tracepoint stubs are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-iwlwifi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-msg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-msg.h

## Purpose
Declares tracepoints for iwlwifi formatted log messages.

## Important APIs, Types, and Functions
Defines event class `iwlwifi_msg_event` and events `iwlwifi_err`, `iwlwifi_warn`, `iwlwifi_info`, `iwlwifi_crit`, plus `iwlwifi_dbg` with debug level and function name.

## Control Flow
Logging wrappers pass `struct va_format` to the tracepoints. The trace event stores formatted text using `__vstring`/`__assign_vstr`.

## State and Persistence Behavior
Messages persist only in trace buffers. No driver state changes.

## Dependencies and Integration Points
Used by `iwl-debug.c` and included through `iwl-devtrace.h`.

## Risks
Varargs formatting must happen while the `va_list` remains valid. Trace volume can be high with broad debug masks.

## Test Signals
Error/warn/info/crit/debug trace capture, debug function-name capture, long message truncation behavior through trace infrastructure, and tracing-disabled builds are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-ucode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-ucode.h

## Purpose
Declares trace events for continued and wrapped firmware event-log output.

## Important APIs, Types, and Functions
Events are `iwlwifi_dev_ucode_cont_event` and `iwlwifi_dev_ucode_wrap_event`, capturing device name, event time/data/id, and wrap counters/entry positions.

## Control Flow
Firmware event-log dump paths call these events while iterating event logs and detecting wrap boundaries.

## State and Persistence Behavior
No driver state is mutated; event-log snapshots persist in trace buffers.

## Dependencies and Integration Points
Included by `iwl-devtrace.h`; tracepoints are exported by `iwl-devtrace.c`.

## Risks
Event log trace volume can be high during firmware failures. Field widths must match firmware event data.

## Test Signals
Continuous event log tracing, wrap tracing, exported tracepoint availability for modules, and disabled tracing builds are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-ucode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.c

## Purpose
Instantiates iwlwifi tracepoints and implements conditional RX tracing that splits RX packet header tracing from payload tracing.

## Important APIs, Types, and Functions
Defines `CREATE_TRACE_POINTS`, exports ucode tracepoint symbols, and implements `__trace_iwlwifi_dev_rx()`.

## Control Flow
`__trace_iwlwifi_dev_rx()` computes a trace length and header offset using `iwl_rx_trace_len()`, emits `trace_iwlwifi_dev_rx()`, and emits `trace_iwlwifi_dev_rx_data()` only when payload bytes were omitted from the first event.

## State and Persistence Behavior
No persistent driver state. It writes trace records.

## Dependencies and Integration Points
Depends on `iwl-devtrace.h`, `iwl-trans.h`, Linux module tracepoint export, and sparse/`__CHECKER__` guards.

## Risks
RX length calculation must avoid reading beyond packets. Tracepoint symbol export is needed for split modules; missing exports break consumers.

## Test Signals
Device tracing enabled, sparse builds, RX MPDU data/header split, non-MPDU full RX tracing, and module consumers of exported ucode tracepoints are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.h

## Purpose
Top-level device tracing header for iwlwifi. It provides packet-data filtering helpers, RX trace-length calculation, tracepoint stubs for disabled builds, shared device-field macros, and includes all trace event families.

## Important APIs, Types, and Functions
Key helpers are `iwl_trace_data()`, `iwl_rx_trace_len()`, `maybe_trace_iwlwifi_dev_rx()`, and `__trace_iwlwifi_dev_rx()`. It includes IO, ucode, message, data, and iwlwifi trace headers.

## Control Flow
`iwl_trace_data()` suppresses payload tracing for non-data frames, frames requesting TX status, and likely EAPOL frames. `iwl_rx_trace_len()` trims RX MPDU traces to headers for data frames. `maybe_trace_iwlwifi_dev_rx()` calls the heavy trace helper only if RX tracepoints are enabled.

## State and Persistence Behavior
No state changes. It controls what packet bytes are copied into trace buffers.

## Dependencies and Integration Points
Depends on skb/mac80211/cfg80211 types and `iwl-trans.h`. Used throughout transport RX/TX/IO/debug logging paths.

## Risks
Packet header offset assumptions must match 802.11 header forms and firmware RX command header size. Filtering is privacy-sensitive and can affect trace usefulness.

## Test Signals
QoS/A4/EAPOL TX filtering, RX MPDU header trimming, non-data RX full tracing, disabled tracepoint stub compilation, and tracepoint-enabled gating are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.c

## Purpose
Implements the bus-agnostic iwlwifi driver core: firmware filename selection, asynchronous firmware request and fallback, firmware TLV parsing, firmware image allocation, debug TLV ingestion, opmode selection/start/stop, module parameters, and module init/exit around PCI registration.

## Important APIs, Types, and Functions
Main public APIs are `iwl_drv_start`, `iwl_drv_stop`, `iwl_opmode_register`, `iwl_opmode_deregister`, `iwl_drv_get_fwname_pre`, `iwl_drv_is_wifi7_supported`, and exported `iwlwifi_mod_params`. Important internals include `iwl_request_firmware`, `iwl_req_fw_callback`, `iwl_parse_v1_v2_firmware`, `iwl_parse_tlv_firmware`, `iwl_alloc_ucode`, `validate_sec_sizes`, `_iwl_op_mode_start`, `_iwl_op_mode_stop`, and firmware/debug cleanup helpers.

## Control Flow
`iwl_drv_start()` allocates `iwl_drv`, initializes debugfs/domains, and requests the newest supported firmware asynchronously. The callback parses legacy or TLV firmware, validates API/core range, copies firmware sections into VM allocations, imports debug TLVs and PNVM data, loads optional external debug TLVs, selects DVM/MVM/MLD opmode, starts it if registered, or requests its module. On firmware miss or incompatible image it decrements API and retries. Stop waits for callback completion, stops opmode, frees firmware/debug state, removes debugfs, and frees the driver.

## State and Persistence Behavior
Persistent runtime state lives in `struct iwl_drv`: parsed `iwl_fw`, opmode pointer, transport pointer, firmware index/name, completion, list node, and debugfs dentries. Firmware sections are copied from request-firmware buffers into owned VM memory. Module parameters persist globally and shape debug, restart, crypto, power, coexistence, and capability behavior.

## Dependencies and Integration Points
Depends on Linux firmware loader, module/debugfs/vmalloc/completion APIs, PCI registration (`iwl_pci_register_driver`), transport, opmode interface, config tables, firmware image/TLV ABIs, debug TLV framework, and MVM/DVM/MLD modules.

## Risks
The firmware callback is complex and asynchronous: failure paths must release firmware buffers, avoid double-freeing `pieces`, and unbind safely. TLV length validation is critical for untrusted firmware files. Opmode table locking protects start/stop/register races. Firmware API range and filename logic must match linux-firmware naming, including core-number encoding.

## Test Signals
Firmware load success, missing firmware fallback across API range, incompatible core/API rejection, malformed TLV lengths, old v1/v2 firmware, DVM section size validation, PNVM/debug TLV allocation, opmode absent then registered, opmode start retry on timeout, stop during firmware request, debugfs cleanup, module parameter parsing, and Wi-Fi 7 MLD selection are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.h

## Purpose
Declares the public bus-agnostic iwlwifi driver interface, RF config bit extractors, export-symbol policy, KUnit visibility policy, init retry count, and firmware-prefix helper.

## Important APIs, Types, and Functions
Defines `DRV_NAME`, NVM and extended-NVM RF bitfield extractors, `iwl_drv_start`, `iwl_drv_stop`, `iwl_drv_is_wifi7_supported`, `IWL_EXPORT_SYMBOL`, `EXPORT_SYMBOL_IF_IWLWIFI_KUNIT`, `VISIBLE_IF_IWLWIFI_KUNIT`, `IWL_MAX_INIT_RETRY`, `FW_NAME_PRE_BUFSIZE`, and `iwl_drv_get_fwname_pre`.

## Control Flow
The header documents the high-level init flow from bus probe to async firmware fetch and opmode start. Runtime control flow is implemented in `iwl-drv.c`.

## State and Persistence Behavior
No state is stored here. The macros influence symbol visibility depending on modular opmode and KUnit configuration.

## Dependencies and Integration Points
Included by most iwlwifi modules. It bridges PCI/transport code to the common driver core and controls namespace exports for split opmode modules.

## Risks
RF bit extractors must match NVM layout. Export policy changes can break modular builds. `iwl_drv_start()` documentation says NULL on error, while implementation returns `ERR_PTR`, so callers must follow implementation behavior.

## Test Signals
Modular and built-in builds, KUnit builds, bus probe/remove calls, RF config parsing, firmware prefix helper users, and caller handling of `ERR_PTR` failures are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-drv.h -->
