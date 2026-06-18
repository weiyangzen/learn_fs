# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/fw.c

Purpose: Implements the MLD firmware bring-up, shutdown, and post-alive configuration path. It starts transport hardware, waits for UCODE_ALIVE_NTFY, loads PNVM, sends init PHY configuration, pushes runtime configuration commands, initializes MCC/regulatory state, and tears firmware down on error or stop.

Important APIs/types/functions: `iwl_mld_load_fw()`, `iwl_mld_start_fw()`, `iwl_mld_stop_fw()`, `iwl_mld_send_recovery_cmd()`, `iwl_mld_run_fw_init_sequence()`, `iwl_alive_fn()`, `iwl_mld_config_fw()`, `iwl_mld_send_tx_ant_cfg()`, RSS setup via `iwl_mld_send_rss_cfg_cmd()`, scan setup via `iwl_mld_config_scan()`, and alive timeout diagnostics in `iwl_mld_print_alive_notif_timeout()`.

Control flow: `iwl_mld_start_fw()` calls `iwl_mld_load_fw()`, which starts HW and runs the init sequence. The sequence registers an alive notification wait, starts regular ucode, validates alive response version and payload size, records SKU/error-table data, loads PNVM, sends `INIT_EXTENDED_CFG_CMD` and PHY config, and waits for `INIT_COMPLETE_NOTIF`. After loading, `iwl_mld_config_fw()` sends antenna, BT, SoC latency, LARI, thermal, RX queue, RSS, scan, power, LED, PPAG/SAR/SGOM/TAS/AP-type configuration, and recovery state if this is a hardware restart. Any post-load failure stops firmware before returning.

State/persistence: Maintains `mld->fw_status.running`, alive-derived firmware debug/error table addresses, transport debug IMR data, optional `mld->error_recovery_buf`, and firmware recovery DB exchange state. On stop it aborts notification waits, stops firmware debug collection, stops the device, cancels async notifications, and marks firmware not running.

Dependencies/integration: Uses transport start/stop, firmware runtime/debug TLVs, PNVM, PHY, power, MCC, LED, coexistence, regulatory, thermal, scan, RSS, and host command helpers. It assumes callers hold `wiphy->mtx` and relies on `iwl_mld_send_cmd_pdu()` from `hcmd.h`.

Risks: Alive payload version/length mismatches abort startup. RSS assumes more than one RX queue because queue 0 is skipped as fallback. Recovery command blob failures disconnect station interfaces. Many configuration steps are sequential, so one failed optional-looking subsystem can prevent driver start. Timeout handling reads low-level registers and triggers firmware debug collection.

Test signals: KUnit or integration tests should cover alive notification parsing versions 7/8, timeout/error paths, recovery buffer upload response handling, restart configuration, and startup failure cleanup. Runtime signals include successful `uCode started`, valid MCC initialization, LED configuration after firmware start, and absence of leaked notification waits after stop.
