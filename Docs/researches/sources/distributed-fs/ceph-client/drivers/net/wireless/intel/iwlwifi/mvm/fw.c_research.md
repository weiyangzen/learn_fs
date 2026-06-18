# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw.c

## Purpose

`fw.c` owns MVM firmware bring-up, init/runtime/WoWLAN firmware loading, alive notification handling, NVM/PNVM setup, PHY calibration, regulatory/platform power configuration, debug/recovery setup, and the high-level `iwl_mvm_up()` sequence that makes the device usable after transport start. It is the central bridge between transport firmware lifecycle and higher-level mac80211 operation.

## Important APIs, Types, And Functions

- `struct iwl_mvm_alive_data` carries SKU ID values and alive validity from `UCODE_ALIVE_NTFY`.
- `iwl_mvm_load_ucode_wait_alive()` sets the current firmware image, starts firmware, waits for alive, records error table addresses and firmware versions, loads PNVM, initializes queue bookkeeping, marks firmware running, and flushes stale BSS data for legacy APIs.
- `iwl_run_init_mvm_ucode()` runs legacy INIT firmware calibration and NVM acquisition.
- `iwl_run_unified_mvm_ucode()` runs unified firmware init/NVM/PHY setup within the regular image.
- `iwl_mvm_load_rt_fw()` selects unified or split INIT+REGULAR flow and initializes paging.
- `iwl_mvm_up()` performs full runtime firmware startup and post-alive configuration.
- `iwl_mvm_load_d3_fw()` starts WoWLAN firmware and minimum D3 setup.
- Regulatory/power helpers include `iwl_mvm_sar_select_profile()`, `iwl_mvm_get_sar_geo_profile()`, `iwl_mvm_sar_geo_init()`, `iwl_mvm_ppag_send_cmd()`, `iwl_mvm_tas_init()`, `iwl_mvm_lari_cfg()`, `iwl_mvm_uats_init()`, and `iwl_mvm_sgom_init()`.
- Recovery/diagnostic entry points include `iwl_mvm_send_recovery_cmd()`, `iwl_mvm_mfu_assert_dump_notif()`, and `iwl_mvm_rx_mfuart_notif()`.

## Control Flow

Firmware load begins by starting transport hardware, selecting an image, registering notification waits, and calling `iwl_trans_start_fw()`. `iwl_alive_fn()` parses multiple alive-notification versions, extracts UMAC/LMAC debug pointers, SKU ID, IMR metadata, version data, and alive status. On timeout or invalid alive, the code prints security boot, power-domain, and program-counter diagnostics and may trigger firmware debug collection.

Legacy init uses INIT firmware first, reads or uploads NVM, handles RF-kill shortcuts, sends TX antenna and PHY configuration, waits for calibration/PHY DB notifications, stops the device, restarts hardware, and loads regular firmware. Unified init uses the regular image, sends `INIT_EXTENDED_CFG_CMD`, performs optional external NVM load, sends `NVM_ACCESS_COMPLETE`, sends PHY config, waits for init completion, and reads NVM once.

`iwl_mvm_up()` chains post-load configuration: shared memory, Smart FIFO, debug config, antenna and PHY DB, Bluetooth coexistence, SoC latency, LARI, RX queues/RSS, station mapping reset, DQA, auxiliary station, thermal/CTDP, LTR, power, MCC, scan config, recovery DB restore, time sync, PTP, PPAG, SAR/geographic SAR, SGOM, TAS, LED sync, UATS, RFI, and MEI state. Any fatal error jumps to `iwl_mvm_stop_device()`.

## State And Persistence

The file mutates `mvm->status`, `mvm->fwrt`, `mvm->nvm_data`, queue maps, firmware-to-mac station arrays, thermal/power state, debug state, regulatory runtime tables, error recovery buffers, and init flags. Persistent platform inputs come from ACPI/UEFI/BIOS tables, PNVM, NVM files, MEI, and firmware TLVs; the driver stores parsed results in runtime structures and sends them to firmware on each bring-up rather than writing persistent storage itself.

## Dependencies And Integration Points

It integrates with the transport layer (`iwl_trans_*`), firmware runtime/debug (`iwl_fwrt`, debug TLVs, PNVM), NVM parsing/loading, ACPI/UEFI regulatory and power tables, MEI, mac80211/cfg80211, RX queue configuration, scan, Bluetooth coexistence, thermal cooling, RFI, PTP, time sync, LED sync, and MVM station/PHY context helpers. Firmware command layout is heavily version- and capability-dependent.

## Risks And Edge Cases

- Startup sequencing is strict; moving NVM, PNVM, PHY config, calibration, paging, RX queue, or regulatory commands can break specific hardware families.
- Error paths must remove notification waits and restore the previous firmware image, otherwise later waits or state checks can see stale state.
- Many BIOS/ACPI tables are optional; unavailable data is often non-fatal, while inconsistent data such as WGDS without WRDS is logged.
- Command-version handling for SAR, geographic SAR, PPAG, TAS, LARI, and PHY config is dense and hardware dependent.
- RF-kill and CT-kill paths intentionally skip parts of setup; regressions may only occur under hardware switch, thermal, or restart conditions.
- Recovery command buffer ownership is transferred/freed in `iwl_mvm_send_recovery_cmd()`, so callers must not reuse it after sending.

## Test Signals

Key signals are clean boot on split and unified firmware families, RF-kill init/resume, WoWLAN firmware load, firmware restart recovery, valid NVM/PNVM loading, PHY calibration completion, RX queue/RSS setup, regulatory MCC/LARI/SAR/PPAG/TAS command logs, no alive timeout debug triggers, no station-map stale pointers after restart, and hardware-specific validation on AX210 and newer devices where product reset, IMR, UATS, and newer power tables apply.
