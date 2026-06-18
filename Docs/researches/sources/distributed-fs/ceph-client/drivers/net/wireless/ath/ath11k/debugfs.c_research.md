# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.c

## Purpose

This file implements the ath11k debugfs control and inspection surface for a device/SOC and each PDEV. It creates debugfs directories, exposes firmware and datapath statistics, lets privileged users toggle diagnostic modes such as extended TX/RX statistics and packet logging, provides test hooks for firmware crash/radar/TWT behavior, and maintains an optional direct-buffer-ring debug trace.

The code is compiled only through the debugfs-enabled ath11k build path declared in `debugfs.h`. It is not datapath-critical in the normal packet path, but several controls reconfigure monitor status filters, send WMI/HTT commands, or queue reset work, so writes can affect live device behavior.

## Important APIs, Types, and Functions

- `ath11k_debugfs_soc_create()` and `ath11k_debugfs_soc_destroy()` create/remove `/sys/kernel/debug/ath11k/<bus-dev>` SOC roots. The parent `ath11k` directory is intentionally left behind.
- `ath11k_debugfs_pdev_create()` and `ath11k_debugfs_pdev_destroy()` add SOC-level files: `simulate_fw_crash`, `soc_dp_stats`, and optional `sram`.
- `ath11k_debugfs_register()` creates per-radio `macN` debugfs directories, a symlink under the mac80211 wiphy debugfs tree, HTT and firmware stats files, packet logging and extended stats controls, DFS controls, DBR debug enablement, and power-save tracking toggles.
- `ath11k_debugfs_unregister()` frees any direct-buffer debug allocations associated with a radio.
- `ath11k_debugfs_fw_stats_init()` creates `fw_stats/{pdev_stats,vdev_stats,beacon_stats}`. The corresponding open handlers allocate `ATH11K_FW_STATS_BUF_SIZE`, request WMI firmware stats, fill text with `ath11k_wmi_fw_stats_fill()`, and serve it through `simple_read_from_buffer()`.
- `ath11k_debugfs_fw_stats_process()` consumes beacon stats replies and completes `ar->fw_stats_done` when all started VDEVs have supplied beacon stats.
- `ath11k_write_extd_rx_stats()` and `ath11k_write_pktlog_filter()` reconfigure monitor status-ring TLV filters through `ath11k_dp_tx_htt_rx_filter_setup()`.
- `ath11k_write_fw_dbglog()` parses debug-log configuration and sends it through `ath11k_wmi_fw_dbglog_cfg()`.
- `ath11k_debugfs_add_dbring_entry()` appends RX/replenish snapshots into a circular DBR debug buffer under a spinlock.
- TWT debugfs file operations (`ath11k_write_twt_add_dialog()`, `ath11k_write_twt_del_dialog()`, `ath11k_write_twt_pause_dialog()`, `ath11k_write_twt_resume_dialog()`) parse user commands and invoke WMI TWT commands for AP or supported STA interfaces.

## Control Flow

Device setup flows from SOC creation to PDEV creation and then per-radio registration. `ath11k_debugfs_soc_create()` finds or creates the global `ath11k` debugfs directory, creates a bus/device-named child, and stores it in `ab->debugfs_soc`. `ath11k_debugfs_pdev_create()` adds SOC-wide files unless the device has already been registered. `ath11k_debugfs_register()` creates the `macN` child and populates all per-radio controls, including calls into `ath11k_debugfs_htt_stats_init()` and `ath11k_debugfs_fw_stats_init()`.

Read-only stats files commonly use an open/read/release pattern: on open they lock `ar->conf_mutex`, verify `ATH11K_STATE_ON`, allocate a vmalloc buffer, request or snapshot data, attach the buffer to `file->private_data`, and release the mutex. Reads then copy the prepared text or binary SRAM dump. Release frees the buffer.

Write controls parse a bounded user buffer or use `kstrto*_from_user()`, validate state and input, then update `ar->debug` fields or call WMI/HTT/DP helpers. Packet logging first toggles firmware pktlog, clears any previous monitor filter, chooses lite/full/default TLV masks, updates all RXDMA monitor status rings, and persists `pktlog_filter`/`pktlog_mode`. Extended RX stats similarly applies either a diagnostic TLV mask or the default monitor status filter unless monitor mode is already active.

DBR debug control creates a per-module child directory (`spectral` or `CFR`) and allocates a fixed 512-entry circular buffer. Runtime producers call `ath11k_debugfs_add_dbring_entry()` only if the module debug state exists and is enabled; readers dump the table while holding the DBR spinlock.

Power-save tracking controls use WMI pdev parameters to enable peer PS state change events. Disabling resets per-station cached PS state and duration through `ieee80211_iterate_stations_atomic()`. TWT per-vif controls are installed by `ath11k_debugfs_op_vif_add()` for AP VIFs and STA VIFs with STA_TWT firmware service support.

## State and Persistence

Most state is in-memory and lifetime-bound to `struct ath11k`, `struct ath11k_base`, debugfs dentries, or open file handles. Persistent knobs include `ar->debug.extd_tx_stats`, `ar->debug.extd_rx_stats`, `ar->debug.rx_filter`, `ar->debug.pktlog_filter`, `ar->debug.pktlog_mode`, `ar->debug.module_id_bitmap`, `ar->ps_state_enable`, and `ar->ps_timekeeper_enable`; these survive across debugfs reads/writes while the driver instance is alive, but not across device removal.

Per-open statistics buffers are transient and freed by release handlers. Firmware stats lists are maintained under `ar->fw_stats`; beacon stats are explicitly freed after a multi-VDEV beacon stats request is formatted. DBR debug buffers persist until disabled or unregister, and behave as ring buffers indexed by `dbr_debug_idx`.

Concurrency is managed with `ar->conf_mutex` around live state/configuration changes, `ab->base_lock` for SOC backpressure stats reads, `ar->data_lock` for station PS state/duration updates and beacon-list cleanup, and per-DBR spinlocks for debug ring snapshots.

## Dependencies and Integration Points

The file integrates with Linux debugfs, vmalloc/kzalloc, simple read/write helpers, mac80211 VIF/station iteration, WMI firmware commands, HTT/DP monitor-ring configuration, HIF memory reads, and ath11k core state. Important local dependencies include `debugfs_htt_stats.h`, `wmi.h`, `dp_tx.h`, `hal_rx.h`, `peer.h`, `hif.h`, and structures rooted at `struct ath11k`, `struct ath11k_base`, `struct ath11k_vif`, and `struct ath11k_sta`.

The debugfs controls are privileged operational hooks. They cross into firmware via `ath11k_mac_fw_stats_request()`, `ath11k_wmi_force_fw_hang_cmd()`, `ath11k_wmi_fw_dbglog_cfg()`, `ath11k_wmi_pdev_pktlog_enable()/disable()`, `ath11k_wmi_simulate_radar()`, TWT WMI commands, and `ath11k_wmi_pdev_set_param()`. They also directly affect datapath monitor filter setup through `ath11k_dp_tx_htt_rx_filter_setup()`.

## Risks and Edge Cases

- Debugfs writes can intentionally crash firmware, queue hardware restart, simulate radar, or reconfigure monitor filters, so misuse can disrupt active traffic.
- Several formatter paths rely on fixed-size buffers and repeated `scnprintf()` accounting. Most guard length, but truncation is expected when firmware emits more data than the buffer can hold.
- DBR initialization has partial-allocation failure paths where a debugfs directory or parent object can exist before later allocation fails; unregister/disable cleanup is important for leak avoidance.
- Some write paths parse with `sscanf()` after bounded copies. Input validation is strict for field count but does not deeply validate semantic ranges beyond selected IDs and booleans.
- Packet logging and extended RX stats both manipulate monitor status filter state; interactions with monitor mode are guarded in the extended RX path but still require careful sequencing in tests.
- `simulate_fw_crash` chooses the first radio in ON state; multi-radio behavior depends on that scan.

## Test Signals

Useful test signals include debugfs file presence under both `/sys/kernel/debug/ath11k/<soc>/macN` and the wiphy symlink, successful open/read/release of firmware stats while `ATH11K_STATE_ON`, `-ENETDOWN` while down, correct `-EINVAL`/`-EPERM` responses for malformed writes, observable WMI/HTT command calls for toggles, monitor filter changes for pktlog/extended RX stats, DBR circular-buffer wrap behavior, and cleanup after debugfs unregister. Runtime integration tests should verify that toggling pktlog and extended RX stats restores defaults and does not leave monitor status rings with stale filters.
