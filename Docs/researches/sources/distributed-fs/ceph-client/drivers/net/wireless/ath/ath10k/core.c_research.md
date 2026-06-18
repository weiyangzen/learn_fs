# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.c

## Purpose

`core.c` is the central lifecycle implementation for the Qualcomm Atheros ath10k 802.11ac driver. It binds bus-specific HIF implementations to common firmware loading, board/calibration selection, WMI/HTT/HTC bring-up, mac80211 registration, crash recovery, debugfs/coredump registration, and teardown. It also defines module parameters (`debug_mask`, `cryptmode`, `uart_print`, `skip_otp`, `frame_mode`, `coredump_mask`, `fw_diag_log`) that materially change boot, crypto, logging, datapath framing, and crash-dump behavior.

## Important APIs, Data, and Functions

The static `ath10k_hw_params_list[]` is the hardware capability table for supported devices and buses. Entries select firmware directories, board sizes, patch addresses, hardware ops, RX descriptor ops, cipher suite counts, target layout flags, peer/stat capabilities, diagnostic CE download support, raw-mode constraints, and restart behavior. `ath10k_init_hw_params()` resolves this table by bus, target version, and device id; a mismatch fails probing.

Firmware and board APIs are centered on `ath10k_fetch_fw_file()`, `ath10k_core_fetch_firmware_files()`, `ath10k_core_fetch_firmware_api_n()`, `ath10k_core_fetch_board_file()`, `ath10k_core_fetch_board_data_api_n()`, and `ath10k_core_fetch_board_data_api_1()`. Firmware API parsing validates `ATH10K-FW` magic, walks information elements, and stores pointers to firmware image, OTP image, code-swap data, WMI/HTT op versions, version string, and feature bits. Board API 2 parsing validates board magic and looks up generated board names with variant and fallback names; API 1 falls back to legacy board files.

Calibration and OTP flow uses `ath10k_download_cal_data()` and helpers for nvmem, firmware files, Device Tree properties, target EEPROM, and OTP. `ath10k_core_get_board_id_from_otp()` and `ath10k_core_get_ext_board_id_from_otp()` execute OTP payloads through BMI to discover board ids. `ath10k_core_check_smbios()` and `ath10k_core_check_dt()` populate BDF variants from SMBIOS or Device Tree.

The main lifecycle entry points exported to bus drivers and mac layers are `ath10k_core_create()`, `ath10k_core_register()`, `ath10k_core_start()`, `ath10k_core_stop()`, `ath10k_core_start_recovery()`, `ath10k_core_unregister()`, and `ath10k_core_destroy()`.

## Control Flow

Creation allocates the mac80211 object through `ath10k_mac_create()`, installs hardware register/value tables by `hw_rev`, initializes completions, locks, waitqueues, skb queues, work items, workqueues, NAPI dummy device, coredump storage, and debug storage. Registration is asynchronous: `ath10k_core_register()` stores bus parameters then queues `ath10k_core_register_work()`.

`ath10k_core_register_work()` enables peer stats, probes firmware, registers mac80211, coredump, debugfs, spectral, thermal, and LEDs, then marks `ATH10K_FLAG_CORE_REGISTERED`. Probe powers up HIF, gets target info through bus-specific BMI/HIF calls, initializes hardware parameters, fetches firmware and board data, initializes firmware feature-derived limits, starts firmware once to discover capabilities, prints boot information, stops firmware, and powers down.

`ath10k_core_start()` is the real boot path. For BMI firmware it starts BMI, optionally enables PLL, configures host-interest fields, downloads calibration/board data, handles skip-clock-init, downloads firmware, configures UART and SDIO target flags, then initializes HTC. It completes BMI, attaches WMI and HTT, allocates HTT TX/RX resources, starts HIF, waits for HTC, connects HTT/WMI, starts HTC, waits for WMI service/unified readiness, applies compatibility service bits, sets base MAC, optionally performs dummy-vdev RX-filter reset, refills RX ring, initializes vdev map/list state, sets up HTT, starts debug, target logging, and LEDs.

Stop reverses active runtime pieces: debug stop, optional target suspend, HIF stop, HTT TX stop/RX free, WMI detach, and BMI id invalidation. Unregister cancels register work, unregisters LEDs/thermal/spectral/mac80211/testmode, releases firmware and board files, and unregisters debugfs. Destroy frees workqueues, netdev, debug, coredump, HTT TX, WMI host memory, and mac object.

Recovery is workqueue-based. `ath10k_core_start_recovery()` queues `recovery_check_work` on an auxiliary queue. The check work guards against repeated failures, waits for overlapping recovery if needed, increments pending recovery, then queues `restart_work`. `ath10k_core_restart()` wakes/flushes waiters, drains TX, cancels coverage work, moves ON devices to RESTARTING, halts, finishes scan, asks mac80211 to restart hardware, and submits a devcoredump after unlocking.

## State and Persistence

Runtime state lives in `struct ath10k`: firmware components, `running_fw`, hardware params, WMI/HTT/HTC subobjects, locks, completions, workqueues, calibration mode, board ids, feature flags, vdev maps, peer state, debug state, coredump state, and counters. Persistent user-visible inputs are kernel module parameters, firmware files under linux-firmware paths, optional board/calibration files, nvmem cells, Device Tree properties, and SMBIOS BDF extension records. The file stores no disk data itself; it obtains firmware blobs through the kernel firmware API and releases them explicitly.

Concurrency contracts are strict: many exported lifecycle functions assert `conf_mutex` is held; crash dump storage uses `dump_mutex`; fast peer/stat structures use `data_lock`. Completions are used to break blocked scan, key, vdev, thermal, survey, and peer waiters during recovery.

## Dependencies and Integration Points

The file depends on HIF/BMI/HTC/WMI/HTT layers, mac80211, firmware loader, DMI, Device Tree, nvmem, PM QoS, LEDs, thermal, spectral, testmode, coredump, and debug modules. Firmware feature bits are consumed by WMI/HTT setup, raw mode, crypto mode, BT coexistence, IRAM recovery, service compatibility, and resource limits. Board/calibration decisions affect firmware boot correctness and regulatory/RF behavior.

## Risks

Boot logic has many fallback paths where a subtle ordering change can select the wrong board file or calibration source. API parsers must preserve alignment and length validation to avoid overreads on malformed firmware or board blobs. Recovery must avoid deadlocks with `conf_mutex`, work cancellation, and mac80211 restart callbacks. Module parameters such as software crypto/raw mode and coredump mask can change performance, memory footprint, and debug exposure. Error unwinding in `ath10k_core_start()` is asymmetric: some resources are freed in later stop/destroy paths, so changing a goto target can leak or double-free.

## Test Signals

Useful signals include successful firmware probe and mac80211 registration, printed hardware/firmware/board/boot info, expected board API selection, correct calibration mode, service-ready/unified-ready events, HTT connect and RX refill success, NAPI enable/disable behavior, simulated recovery via debugfs `simulate_fw_crash`, coredump submission on restart, and absence of lockdep warnings around `conf_mutex`, work cancellation, and NAPI synchronization.
