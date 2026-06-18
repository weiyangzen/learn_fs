# Research: subset-b-004972

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/main.c

## Purpose
`main.c` is the central wlcore mac80211/platform integration layer for TI WiLink wl12xx/wl18xx-class WLAN devices. It owns the common `ieee80211_ops` implementation, firmware boot and recovery orchestration, runtime PM/ELP transitions, IRQ processing, interface and station lifecycle, key installation, scan and remain-on-channel control, channel context handling, AP/STA BSS state updates, hardware registration, and final platform probe/remove glue. Bus-specific files provide `wl1271_if_operations`, while chip-family drivers provide `wl->ops`; this file coordinates both with mac80211/cfg80211 and firmware command helpers.

## Important APIs, Types, and Functions
The exported API surface includes `wlcore_alloc_hw()`, `wlcore_free_hw()`, `wlcore_probe()`, `wlcore_remove()`, `wlcore_set_key()`, `wlcore_regdomain_config()`, `wl1271_plt_start()`, `wl1271_plt_stop()`, `wl1271_recalc_rx_streaming()`, `wl1271_tx_dummy_packet()`, `wl12xx_queue_recovery_work()`, `wlcore_update_inconn_sta()`, `wl1271_free_sta()`, `wlcore_rate_to_idx()`, and the module parameter/exported `wl12xx_debug_level`. Internally, `wl1271_ops` maps mac80211 callbacks to `wl1271_op_*` and `wlcore_op_*` functions. Key state lives in `struct wl1271` and per-vif `struct wl12xx_vif`; per-station private state is `struct wl1271_station` in mac80211 `sta->drv_priv`.

## Control Flow
The normal device path is `wlcore_probe()` -> asynchronous NVS request -> `wlcore_nvs_cb()` -> chip setup, power-on, hardware identification, IRQ registration, `wl1271_init_ieee80211()`, `wl1271_register_hw()`, and sysfs creation. `wl1271_op_start()` intentionally defers firmware boot until the first interface is added, because the firmware needs a MAC address before initialization. `wl1271_op_add_interface()` initializes vif data, allocates hw queues and rate/template resources, boots firmware if off, enables a firmware role, initializes role-specific state, and links the vif into `wl->wlvif_list`. Removal disables roles, aborts scan/ROC if needed, resets TX state, frees resources, and may trigger firmware switching between single-role and multi-role firmware through intended recovery.

IRQ handling enters `wlcore_irq()`, completes ELP wakeups if needed, defers during suspend, then calls `wlcore_irq_locked()` under `wl->mutex`. The locked handler reads firmware status, processes watchdog interrupts as recovery triggers, handles RX via `wlcore_rx()`, services TX immediate/delayed completions, optionally runs TX work inline to avoid starvation, and dispatches firmware event handlers. Recovery enters `wl1271_recovery_work()`, disables interrupts, optionally reads panic fwlog, tears down all vifs through `__wl1271_op_remove_interface()`, stops the core, and calls `ieee80211_restart_hw()`.

## State and Persistence Behavior
State is highly in-memory and firmware-coupled. `wl->state` moves among OFF, ON, and RESTARTING; `wl->flags` tracks suspended, pending IRQ work, recovery, ELP, TX pending/busy, and intended recovery. TX/RX counters are persisted only in RAM and reconciled from firmware status; per-link `total_freed_pkts` and PN-derived counters are saved into `struct wl1271_station` across recovery/suspend to preserve security sequence continuity. NVS and firmware blobs are copied into kernel allocations. AP keys may be recorded before AP start and replayed when the AP role begins. Runtime PM state is driven by autosuspend; ELP sleep is entered only when sleep authorization and vif power-save state allow it.

## Dependencies and Integration Points
This file depends on Linux mac80211/cfg80211, runtime PM, wake IRQ support, firmware loading, threaded IRQs, skb queues, timers, workqueues, and the wlcore helper layers: `cmd`, `acx`, `tx`, `rx`, `ps`, `scan`, `init`, `event`, `debugfs`, `vendor_cmd`, `sysfs`, and chip-specific `hw_ops`. It integrates with bus glue through `wl->if_ops`, with chip-specific implementations through `wl->ops`, and with sysfs/debugfs/testmode/vendor command surfaces at registration time.

## Risks and Edge Cases
The main risks are concurrency and state-machine drift. Many callbacks drop and reacquire `wl->mutex` around cancel/sync operations to avoid deadlocks, while TX queue counters use `wl_lock`; changes must preserve lock ordering. IRQ paths can race with suspend, ELP wakeup, recovery, and queue refilling. Firmware status counters wrap and are manually corrected. AP key recording and replay before AP start is sensitive to duplicate key IDs and shutdown ordering. Firmware switching through recovery depends on accurate vif counts. Several callbacks return success even when internal errors occurred to satisfy mac80211 downgrade/removal semantics.

## Test Signals
Useful validation signals include successful `ieee80211_register_hw()` and sysfs/debugfs initialization, interface add/remove across STA/AP/P2P/mesh modes, firmware boot with normal and PLT firmware, scan start/cancel/completion, suspend/resume with WoWLAN patterns, TX watchdog/recovery behavior, channel switch/ROC operations, AP station add/remove/auth flows, key add/remove for WEP/TKIP/CCMP/GEM/IGTK, RX/TX queue drain under load, and runtime PM ELP wakeup timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.c

## Purpose
`ps.c` implements wlcore power-save helpers for STA firmware power-save mode and AP-side station power-save accounting. It translates mac80211/driver power-save state into firmware ACX/CMD calls and keeps mac80211 informed when connected AP clients enter or leave sleep.

## Important APIs, Types, and Functions
`wl1271_ps_set_mode()` is the STA-side entry point. It accepts `STATION_AUTO_PS_MODE`, `STATION_POWER_SAVE_MODE`, or `STATION_ACTIVE_MODE`, programs wake-up conditions with `wl1271_acx_wake_up_conditions()`, sends `wl1271_cmd_ps_mode()`, toggles `WLVIF_FLAG_IN_PS`, and enables/disables beacon early termination for 2.4 GHz low-basic-rate links. `wl12xx_ps_link_start()` and `wl12xx_ps_link_end()` are AP-side helpers that use an HLID and `wlvif->ap.sta_hlid_map` to notify mac80211 of station sleep transitions through `ieee80211_sta_ps_transition_ni()`. The private `wl1271_ps_filter_frames()` marks queued frames for a sleeping station as `IEEE80211_TX_STAT_TX_FILTERED` and returns them to mac80211.

## Control Flow
STA power-save entry first configures wake conditions and then asks firmware to enter auto/forced PSM. Active mode reverses beacon early termination before leaving firmware PSM. AP station sleep starts only for AP vifs with an allocated station HLID and no existing bit in `wl->ap_ps_map`; after mac80211 notification it optionally drains the per-link low-level TX queues. Power-save end clears `wl->ap_ps_map` and notifies mac80211 that the station is awake.

## State and Persistence Behavior
The file updates in-memory flags only: `WLVIF_FLAG_IN_PS`, `wl->ap_ps_map`, global `wl->tx_queue_count[]`, and per-vif `tx_queue_count[]`. It does not persist data across reloads. Queue filtering returns ownership of queued SKBs to mac80211 and updates watermarks via `wl1271_handle_tx_low_watermark()`.

## Dependencies and Integration Points
Dependencies include `ps.h`, `io.h`, `tx.h`, `debug.h`, ACX/CMD helpers declared through wlcore headers, skb queues, RCU station lookup, and mac80211 station power-save notifications. `main.c` calls these helpers from BSS power-save changes and AP firmware-status regulation.

## Risks and Test Signals
Primary risks are stale HLID/station mappings, queue count underflow if filtering diverges from enqueue accounting, and RCU lookup failures during station removal. Tests should exercise STA PS on/off, AP client sleep/wake transitions, sleeping-client frame filtering, low-watermark wakeup, and 2.4 GHz beacon early termination gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.h

## Purpose
`ps.h` declares the wlcore power-save helper interface used by the core driver and related modules. It keeps STA power-save mode programming and AP station sleep notifications available without exposing the implementation details in `ps.c`.

## Important APIs, Types, and Constants
The header includes `wlcore.h` and `acx.h`, then declares `wl1271_ps_set_mode()`, `wl12xx_ps_link_start()`, and `wl12xx_ps_link_end()`. `WL1271_PS_COMPLETE_TIMEOUT` is defined as 500 ms and documents the expected completion wait budget for power-save transitions elsewhere in the driver family.

## Control Flow and Integration
There is no executable control flow. Callers use the declarations to enter/exit STA firmware PSM and to synchronize firmware-reported AP client sleep state with mac80211. The header is consumed by `main.c` and `ps.c`.

## State, Risks, and Test Signals
The header owns no state. Compatibility risks are signature or enum changes that would break callers relying on `enum wl1271_cmd_ps_mode` from ACX command definitions. Compile coverage and power-save transition tests are sufficient signals for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.c

## Purpose
`rx.c` implements firmware RX aggregation parsing and delivery into mac80211. It reads RX packet descriptors listed in firmware status, pulls packet data from device memory into the aggregation buffer, creates SKBs, fills `ieee80211_rx_status`, handles firmware logger packets, and maintains active-link information used by RX streaming.

## Important APIs, Types, and Functions
`wlcore_rx()` is the top-level RX drain routine called from the IRQ handler. `wl1271_rx_handle_data()` validates one aggregated packet, handles descriptor class `WL12XX_RX_CLASS_LOGGER`, allocates and fills an SKB, and queues it on `wl->deferred_rx_queue`. `wl1271_rx_status()` converts firmware descriptor metadata to mac80211 status fields: band, rate index via `wlcore_rate_to_idx()`, HT encoding, RSSI/SNR-derived noise, antenna, frequency, encryption/decryption flags, MIC errors, beacon/probe timestamps, and pending regulatory channel updates. Under `CONFIG_PM`, `wl1271_rx_filter_enable()` and `wl1271_rx_filter_clear_all()` control firmware RX filters used for WoWLAN.

## Control Flow
`wlcore_rx()` compares firmware and driver RX counters modulo `wl->num_rx_desc`, batches descriptors until the configured aggregation buffer would overflow, calls chip-specific `wlcore_hw_prepare_read()`, reads `REG_SLV_MEM_DATA`, and splits the aggregate by descriptor-derived aligned lengths. Data frames mark their HLID in a local active bitmap; after all packets are processed, older hardware may receive an end-of-transaction driver counter write. The active bitmap is passed to `wl12xx_rearm_rx_streaming()`.

## State and Persistence Behavior
RX state is in-memory: `wl->rx_counter`, `wl->aggr_buf`, `wl->noise`, per-link `fw_rate_mbps`, `wl->deferred_rx_queue`, and `wl->rx_filter_enabled`. RX SKBs are deferred to `main.c` netstack work rather than submitted directly from the IRQ loop. Firmware logger data is appended to the fwlog buffer through `wl12xx_copy_fwlog()`.

## Dependencies and Integration Points
The file depends on `rx.h`, `wlcore.h`, `acx.h`, `tx.h`, `io.h`, `hw_ops.h`, mac80211 RX status definitions, skb allocation, and the wl12xx register definition for older end-of-transaction hardware. It integrates tightly with `main.c` IRQ handling and sysfs fwlog exposure.

## Risks and Test Signals
Risks include malformed descriptor lengths, aggregation-buffer bounds, alignment handling (`UNALIGNED` vs `PADDED`), dropping frames during PLT mode, and correct counter wrap handling. Tests should observe RX data delivery, beacon/probe timestamping, encrypted packet flags/MIC failure reporting, firmware log extraction, RX filter enable/clear for suspend, and no aggregation buffer overrun under multiple RX descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.h

## Purpose
`rx.h` defines wlcore RX descriptor formats, descriptor bit masks, RX alignment modes, packet classes, RSSI bounds, and public RX helper prototypes. It is the shared contract between RX parsing code, hardware-specific status conversion, and firmware command/filter code.

## Important APIs, Types, and Constants
The central type is packed `struct wl1271_rx_descriptor`, matching firmware-provided RX metadata: length, status, flags, rate, channel, RSSI/SNR, timestamp, packet class, HLID, and padding length. Constants define band/encryption/status masks, MIC/decrypt failures, RX buffer size encodings, alignment flags (`RX_BUF_UNALIGNED_PAYLOAD`, `RX_BUF_PADDED_PAYLOAD`), and `enum wl_rx_buf_align`. Public prototypes include `wlcore_rx()`, `wlcore_rate_to_idx()` via implementation naming mismatch in the header's legacy `wl1271_rate_to_idx()`, and PM RX filter helpers.

## Control Flow and Integration
The header has no execution flow, but its definitions drive `rx.c` parsing and hardware-specific descriptor interpretation. Packet classes distinguish management/data/beacon/EAPOL/BA/AMSDU/logger frames. Alignment constants tell `rx.c` how to reserve or pull bytes before passing SKBs up.

## State, Risks, and Test Signals
No state is stored in the header. ABI risk is high because struct packing and bit positions must match firmware exactly. Compile tests, RX descriptor decoding tests on both aligned and blocksize-aligned hardware, and encrypted/MIC-failure packet tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.c

## Purpose
`scan.c` provides common scan bookkeeping and channel/SSID preparation for wlcore. Chip-specific operations still perform the actual firmware scan start/stop, while this file translates cfg80211 scan requests into wlcore channel structures, schedules completion timeout handling, and exposes scheduled-scan helper routines.

## Important APIs, Types, and Functions
`wlcore_scan()` starts a regular hardware scan after validating state, copying an optional SSID, setting `wl->scan_wlvif`/`wl->scan.req`, assuming failure until completion, scheduling `scan_complete_work`, and calling `wl->ops->scan_start()`. `wl1271_scan_complete_work()` is the timeout/completion worker that idles scan state, restores AP probe request templates for associated STA mode, queues recovery on failed scans, refreshes regdomain config, and calls `ieee80211_scan_completed()`. `wlcore_set_scan_chan_params()` and private `wlcore_scan_get_channels()` build active/passive/DFS channel arrays and dwell times for search or scheduled scan. `wlcore_scan_sched_scan_ssid_list()` emits the firmware SSID filter command for scheduled scan. `wlcore_scan_sched_scan_results()` notifies mac80211 of periodic scan results.

## Control Flow
Channel preparation runs in ordered passes: 2.4 GHz passive, 2.4 GHz active, 5 GHz passive, 5 GHz DFS, 5 GHz active, with 802.11j currently disabled. Passive-active channels 12-14 can be treated as DFS-like entries when no forced passive scan is required. Dwell times differ for foreground search scans versus periodic scans and are converted from microseconds to milliseconds for firmware structures.

## State and Persistence Behavior
Scan state is in `wl->scan`: state enum, requested SSID, scanned channel bitmask, failure flag, and cfg80211 request pointer. `wl->scan_wlvif` tracks the owning vif. Scheduled scan owner is handled in `main.c` through `wl->sched_vif`. No state persists across module reload; scan completion clears transient fields.

## Dependencies and Integration Points
Dependencies include Linux `ieee80211_channel`, cfg80211 scan/sched-scan requests, runtime PM in completion work, `cmd.h`, `acx.h`, `tx.h`, and chip-specific `wl->ops` scan callbacks. `main.c` wraps these helpers in mac80211 callbacks and handles cancel paths.

## Risks and Test Signals
Risks include stale `scan_wlvif` if an interface is removed mid-scan, timeout-driven recovery after firmware scan failure, dwell-time conversion mistakes, off-by-one channel packing for passive/DFS channels, and strict SSID filter validation for scheduled scan hidden SSIDs. Tests should cover normal scan, cancel scan, timeout failure, associated STA scan template restoration, scheduled scan with match sets, hidden SSIDs, passive-only scans, DFS channel inclusion, and regulatory refresh after scan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.h

## Purpose
`scan.h` declares common wlcore scan interfaces and defines the firmware-facing structures/constants used for regular and scheduled scans.

## Important APIs, Types, and Constants
The header declares regular scan entry points (`wlcore_scan()`, `wl1271_scan_build_probe_req()`, `wl1271_scan_stm()`, `wl1271_scan_complete_work()`), scheduled scan configuration/start/results helpers, channel parameter construction through `wlcore_set_scan_chan_params()`, and SSID-list programming through `wlcore_scan_sched_scan_ssid_list()`. It defines scan state constants, scan options, timeout (`WL1271_SCAN_TIMEOUT` 30000 ms), maximum channel arrays, SSID filter types, BSS types, scan channel flags, packed `struct conn_scan_ch_params`, packed `struct wl1271_cmd_sched_scan_ssid_list`, `struct wlcore_scan_channels`, and scan type enum values.

## Control Flow and Integration
There is no executable logic in the header. Its structures are filled by `scan.c` and consumed by chip-specific scan implementations and firmware command routines. `scan_complete_work` is shared with `main.c` allocation and cancellation paths.

## State, Risks, and Test Signals
The header stores no state. The packed command structures must match firmware ABI; max array sizes must remain compatible with wl12xx and wl18xx channel limits. Compile coverage plus scheduled scan command validation and channel packing tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sdio.c

## Purpose
`sdio.c` is the SDIO bus glue for wlcore devices. It translates wlcore raw read/write/power/block-size operations to Linux MMC/SDIO calls, parses device tree data, and creates a child platform device (`wl12xx` or `wl18xx`) that the common core driver probes.

## Important APIs, Types, and Functions
`struct wl12xx_sdio_glue` stores the SDIO device and child platform device. `sdio_ops` implements `struct wl1271_if_operations` with `wl12xx_sdio_raw_read()`, `wl12xx_sdio_raw_write()`, `wl12xx_sdio_set_power()`, and `wl1271_sdio_set_block_size()`. Raw access uses CMD52 (`sdio_f0_readb/writeb`) for `HW_ACCESS_ELP_CTRL_REG` and CMD53 (`sdio_readsb/writesb` or `sdio_memcpy_fromio/toio`) for regular fixed/incrementing transfers. `wl1271_probe()` validates SDIO function 2, sets quirks, parses OF compatible data and IRQs, detects wl18xx by SDIO revision 3.00, and registers the platform child. Suspend sets `MMC_PM_KEEP_POWER` when WoWLAN is enabled and supported.

## Control Flow
The SDIO driver matches TI SDIO IDs, probes only function 0x02, prepares platform data containing `if_ops` and family metadata, maps IRQ/wakeirq from OF, and allocates a child platform device named according to detected chip family. The child receives IRQ resources and platform data, then common wlcore probe handles firmware and mac80211 registration. Remove unregisters the child and balances runtime PM.

## State and Persistence Behavior
State is per-device glue allocated with devm. Power state is delegated to MMC runtime PM and SDIO function enable/disable. `pwr_in_suspend` is stored in platform data based on host `MMC_PM_KEEP_POWER`. The module-level `dump` parameter controls hex dumps of SDIO transfers.

## Dependencies and Integration Points
Dependencies include Linux SDIO/MMC APIs, OF IRQ parsing, runtime PM, platform devices, `wlcore.h`, `wl12xx_80211.h`, and `io.h`. The file integrates with the common core exclusively through platform data and `wl1271_if_operations`.

## Risks and Test Signals
Risks include wrong function-number matching, failed IRQ parsing, SDIO revision misclassification, PM imbalance around `pm_runtime_put_noidle()`/remove, failure to keep power for WoWLAN, and transfer-mode differences for fixed vs incrementing addresses. Test signals include SDIO probe/remove, register reads/writes including ELP CMD52, firmware boot after `mmc_hw_reset()`, block size setup, suspend with and without host keep-power support, and optional transfer dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/spi.c

## Purpose
`spi.c` is the SPI/WSPI bus glue for wlcore devices. It implements raw command/data transfers, WSPI reset/init sequencing, regulator-based power control, OF family selection, and child platform-device creation for the common wlcore driver.

## Important APIs, Types, and Functions
`struct wl12xx_spi_glue` stores the SPI device, child platform device, and `vwlan` regulator. `spi_ops` provides `read`, `write`, `reset`, `init`, `power`, and a no-op `set_block_size`. `wl12xx_spi_reset()` clocks an all-ones reset sequence. `wl12xx_spi_init()` sends the WSPI init command with CRC7 and extra inverted-chip-select clocks. `wl12xx_spi_raw_read()` and `__wl12xx_spi_raw_write()` build WSPI command words and split transfers into chunks of at most 4092 bytes. `wl12xx_spi_read_busy()` polls busy words until data is ready. `wl12xx_spi_set_power()` toggles the `vwlan` regulator. `wlcore_probe_of()` reads compatible family and clock properties.

## Control Flow
Probe allocates platform data and glue, sets `bits_per_word = 32`, acquires the regulator, parses OF metadata, calls `spi_setup()`, allocates a child platform device named for the family, attaches the SPI IRQ as an IRQ resource, copies platform data, and registers the child. The common wlcore platform probe then uses `spi_ops` for device access. Remove unregisters the child.

## State and Persistence Behavior
The SPI glue keeps only devm-managed pointers and regulator state. Transfer scratch buffers are mostly in `struct wl1271` (`buffer_cmd`, `buffer_busyword`) except dynamically allocated write transfer arrays. No persistent on-disk state exists.

## Dependencies and Integration Points
Dependencies include Linux SPI, regulator, OF matching, platform devices, CRC7, byte swapping, IRQ trigger helpers, and wlcore headers. It integrates with main wlcore via `struct wl1271_if_operations` and with device tree compatibles for wl127x/wl128x/wl18xx.

## Risks and Test Signals
Risks include WSPI command bitfield/endianness errors, busy-word timeout handling, chunking over `SPI_AGGR_BUFFER_SIZE`, ignoring `spi_sync()` return codes in several paths, regulator failures, and ELP wakeup write latency requiring a duplicate write. Test signals include WSPI init/reset success, large read/write chunking, busy timeout behavior, regulator enable/disable, firmware boot over SPI, IRQ delivery, and OF compatible/clock parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.c

## Purpose
`sysfs.c` exposes a small sysfs control/status surface for wlcore devices: Bluetooth coexistence state, hardware PG version, and a binary firmware log stream.

## Important APIs, Types, and Functions
`bt_coex_state_show()` and `bt_coex_state_store()` back a read/write device attribute. Store parses a boolean, updates `wl->sg_enabled`, and if the chip is on resumes runtime PM and calls `wl1271_acx_sg_enable()`. `hw_pg_ver_show()` exposes `wl->hw_pg_ver` or `n/a`. `wl1271_sysfs_read_fwlog()` backs the binary `fwlog` attribute, consuming bytes from `wl->fwlog` and compacting the buffer. `wlcore_sysfs_init()` creates the two text attributes and binary file with cleanup on partial failure; `wlcore_sysfs_free()` removes them.

## Control Flow
Initialization is called after hardware registration in `main.c` probe completion. Attribute accesses lock `wl->mutex` around shared driver state. FW log reads may use interruptible locking and return zero once `wl->fwlog_size` is negative during teardown.

## State and Persistence Behavior
Sysfs state is live driver state only. `sg_enabled` persists only for the lifetime of `struct wl1271`; fwlog is a one-page in-memory FIFO-like buffer consumed destructively by reads. The `pos` argument is ignored because historical log data is not retained.

## Dependencies and Integration Points
Dependencies include Linux device attributes, binary sysfs attributes, runtime PM, `acx.h`, `wlcore.h`, `debug.h`, and `sysfs.h`. FW log data is produced by RX/logger and recovery paths in other files.

## Risks and Test Signals
Risks include returning `count` even on invalid store values, ignoring ACX return in bt coex store, fwlog readers racing with teardown, and destructive reads surprising tooling. Tests should create/remove sysfs files, toggle bt coexistence while off and on, read valid and `n/a` PG versions, read fwlog in partial chunks, and verify teardown unblocks readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.h

## Purpose
`sysfs.h` declares the sysfs lifecycle hooks for wlcore.

## Important APIs
It declares `wlcore_sysfs_init(struct wl1271 *wl)` and `wlcore_sysfs_free(struct wl1271 *wl)`. The header relies on callers already having a visible `struct wl1271` declaration through surrounding includes.

## Control Flow, State, and Integration
No logic or state exists in the header. `main.c` calls init after registering mac80211 hardware and calls free from `wlcore_free_hw()`. The header keeps sysfs implementation details out of the core file.

## Risks and Test Signals
Risks are limited to lifecycle mismatch: every successful init must be paired with free, and callers need appropriate include ordering for `struct wl1271`. Compile coverage plus probe/remove sysfs tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.c

## Purpose
`testmode.c` implements cfg80211 testmode commands for factory/diagnostic access to wlcore firmware. It allows privileged userspace to send raw test commands, interrogate/configure firmware IEs, switch PLT modes, run FEM detection, and read fuse-derived MAC addresses while in PLT.

## Important APIs, Types, and Functions
The public entry point is `wl1271_tm_cmd()`, registered through `CFG80211_TESTMODE_CMD` in `main.c`. Internal command IDs include TEST, INTERROGATE, CONFIGURE, SET_PLT_MODE, and GET_MAC, with legacy unused IDs retained for ABI compatibility. `wl1271_tm_policy` validates netlink attributes. `wl1271_tm_cmd_test()` sends raw test command buffers through `wl1271_cmd_test()` and optionally returns the answer. `wl1271_tm_cmd_interrogate()` allocates a `struct wl1271_command`, calls `wl1271_cmd_interrogate()`, and replies with command data. `wl1271_tm_cmd_configure()` sends `wl1271_cmd_configure()`. `wl1271_tm_cmd_set_plt_mode()` dispatches to `wl1271_plt_start()`/`wl1271_plt_stop()`; FEM detect always stops PLT afterward. `wl12xx_tm_cmd_get_mac()` returns fuse OUI/NIC as an Ethernet address when in PLT.

## Control Flow
`wl1271_tm_cmd()` parses netlink attributes, requires a command ID, blocks all commands except SET_PLT_MODE while in `PLT_CHIP_AWAKE`, and dispatches. Most firmware-touching commands lock `wl->mutex`, verify `WLCORE_STATE_ON` where needed, resume runtime PM, call command helpers, create a cfg80211 testmode reply SKB if data is returned, and put runtime PM.

## State and Persistence Behavior
The file changes PLT state through `main.c` helpers and reads fuse MAC fields from `struct wl1271`. It does not persist data. It may expose firmware command results or calibration status to userspace through netlink replies.

## Dependencies and Integration Points
Dependencies include cfg80211 testmode/genetlink, runtime PM, slab allocation, `wlcore.h`, `debug.h`, `acx.h`, `io.h`, and firmware command helpers. It integrates with PLT lifecycle in `main.c` and factory tools using cfg80211 testmode ABI.

## Risks and Test Signals
Risks include ABI breakage of command/attribute IDs, raw command misuse, insufficient state gating for configure versus test/interrogate, reply buffer sizing, and PLT mode transitions leaving the device unavailable for normal mac80211. Tests should cover each command ID, missing/oversized attributes, PLT_ON/OFF/CHIP_AWAKE/FEM_DETECT transitions, get-mac failure outside PLT, and answer payload delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.h

## Purpose
`testmode.h` declares the wlcore cfg80211 testmode command entry point.

## Important APIs
The only declaration is `wl1271_tm_cmd(struct ieee80211_hw *hw, struct ieee80211_vif *vif, void *data, int len)`. It includes `<net/mac80211.h>` for the mac80211 types required by the callback signature.

## Control Flow, State, and Integration
No state or logic exists in the header. `main.c` includes it to register `wl1271_tm_cmd` in `wl1271_ops` through `CFG80211_TESTMODE_CMD()`, while `testmode.c` provides the implementation.

## Risks and Test Signals
Risks are limited to callback signature drift relative to cfg80211/mac80211 testmode expectations. Compile coverage and a cfg80211 testmode command smoke test validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.h -->
