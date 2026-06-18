# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/common.c

## Purpose

`common.c` implements the shared runtime services for the Intel `iwlegacy` 3945/4965 wireless drivers. It is the common layer between mac80211/chip-specific driver files and the legacy firmware/register interface. It owns register access wrappers, host command enqueue/sync/async completion, LED class integration, EEPROM loading and regulatory channel mapping, power-save command construction, hardware scan lifecycle, station table management, link-quality command submission, RX/TX DMA queue allocation and pointer updates, RX decrypt status interpretation, RXON/HT/channel helper logic, firmware error/reset handling, APM start/stop, Tx power/Bluetooth/statistics commands, mac80211 callbacks, watchdog reset policy, beacon time arithmetic, PM hooks, QoS updates, BSS changes, ISR top half, and TX RTS/CTS protection flag setup.

The file is not fully chip-independent: it delegates hardware-specific details through `il->ops`, `il->cfg`, and `il->hw_params`, and it expects 3945/4965-specific files to implement RXON commit, scan construction, Tx power, queue hardware setup, LED command dispatch, EEPROM semaphore handling, and diagnostic dumps.

## Important APIs and Functions

Register and memory access exports include `_il_poll_bit()`, `il_poll_bit()`, `il_set_bit()`, `il_clear_bit()`, `_il_grab_nic_access()`, `il_rd_prph()`, `il_wr_prph()`, `il_read_targ_mem()`, and `il_write_targ_mem()`. These synchronize through `reg_lock` when needed, request MAC access before peripheral/SRAM access, and handle clock/sleep wakeup issues.

Host command APIs are `il_get_cmd_string()`, `il_send_cmd_sync()`, `il_send_cmd()`, `il_send_cmd_pdu()`, `il_send_cmd_pdu_async()`, `il_enqueue_hcmd()`, and `il_tx_cmd_complete()`. They implement the command queue protocol, synchronous waiter state (`S_HCMD_ACTIVE`), async callbacks, `CMD_WANT_SKB` reply-page transfer, DMA mapping, huge command selection, queue-full reset scheduling, and command completion reclamation.

EEPROM/regulatory APIs are `il_eeprom_init()`, `il_eeprom_free()`, `il_eeprom_query_addr()`, `il_eeprom_query16()`, `il_init_channel_map()`, `il_free_channel_map()`, `il_get_channel_info()`, `il_init_geos()`, and `il_free_geos()`. They read NVM through CSR registers, build `struct il_channel_info` arrays from fixed EEPROM band maps, apply HT40 extension-channel data, and expose mac80211 supported bands/rates/channels.

Power and radio configuration APIs include `il_power_update_mode()`, `il_power_initialize()`, `il_set_tx_power()`, `il_send_bt_config()`, `il_send_stats_request()`, `il_set_rxon_hwcrypto()`, `il_check_rxon_cmd()`, `il_full_rxon_required()`, `il_set_rxon_ht()`, `il_set_rxon_channel()`, `il_set_flags_for_band()`, `il_connection_init_rx_config()`, `il_set_rate()`, `il_send_rxon_timing()`, `il_chswitch_done()`, and `il_hdl_csa()`.

Scan APIs include `il_scan_cancel()`, `il_scan_cancel_timeout()`, `il_force_scan_end()`, `il_setup_rx_scan_handlers()`, `il_get_active_dwell_time()`, `il_get_passive_dwell_time()`, `il_init_scan_params()`, `il_mac_hw_scan()`, `il_fill_probe_req()`, `il_setup_scan_deferred_work()`, and `il_cancel_scan_deferred_work()`. Internal scan handlers service `C_SCAN`, `N_SCAN_START`, `N_SCAN_RESULTS`, and `N_SCAN_COMPLETE`.

Station and rate-control APIs include `il_send_add_sta()`, `il_prep_station()`, `il_add_station_common()`, `il_remove_station()`, `il_clear_ucode_stations()`, `il_restore_stations()`, `il_get_free_ucode_key_idx()`, `il_dealloc_bcast_stations()`, `il_send_lq_cmd()`, and `il_mac_sta_remove()`.

Queue and DMA APIs include `il_rx_queue_space()`, `il_rx_queue_update_write_ptr()`, `il_rx_queue_alloc()`, `il_txq_update_write_ptr()`, `il_tx_queue_unmap()`, `il_tx_queue_free()`, `il_cmd_queue_unmap()`, `il_cmd_queue_free()`, `il_queue_space()`, `il_tx_queue_init()`, `il_tx_queue_reset()`, `il_alloc_txq_mem()`, and `il_free_txq_mem()`.

mac80211-facing exports include `il_mac_conf_tx()`, `il_mac_tx_last_beacon()`, `il_mac_add_interface()`, `il_mac_remove_interface()`, `il_mac_change_interface()`, `il_mac_flush()`, `il_mac_config()`, `il_mac_reset_tsf()`, `il_mac_bss_info_changed()`, and `il_tx_cmd_protection()`. Interrupt/error/maintenance exports include `il_irq_handle_error()`, `il_apm_stop()`, `_il_apm_stop()`, `il_apm_init()`, `il_force_reset()`, `il_bg_watchdog()`, `il_setup_watchdog()`, `il_isr()`, `il_usecs_to_beacons()`, and `il_add_beacon_time()`.

## Control Flow

Command submission begins with a caller holding `il->mutex` for synchronous commands. `il_send_cmd_sync()` sets `S_HCMD_ACTIVE`, enqueues through `il_enqueue_hcmd()`, waits up to `HOST_COMPLETE_TIMEOUT`, handles RF-kill/firmware-error/reply-page failures, and clears or frees reply state on error. Async commands require `CMD_ASYNC`, cannot request an SKB reply, and get a generic callback if none is supplied.

`il_enqueue_hcmd()` computes the chip-specific command size, checks huge-command and max-size constraints, rejects RF/CT kill, locks `hcmd_lock`, checks command queue space, selects a normal or huge command buffer index, copies payload, fills `struct il_cmd_header`, maps the command for DMA, lets chip ops attach the buffer to a TFD and update byte counts, advances the queue write pointer, and writes the hardware pointer. `il_tx_cmd_complete()` later decodes the completion sequence, validates the command queue, unmaps DMA, transfers reply pages or invokes callbacks, reclaims command queue entries, clears `S_HCMD_ACTIVE` for sync commands, wakes waiters, and clears metadata flags.

EEPROM initialization powers the device enough for NVM access, verifies signature, acquires the EEPROM semaphore via chip ops, reads 16-bit entries through `CSR_EEPROM_REG` polling, releases the semaphore, then stops APM to save power until firmware load. Channel map creation walks five base regulatory bands and optional HT40 bands, creating `il_channel_info` entries and extension-channel permissions. Geography initialization turns those channel entries plus rate tables and HT capabilities into mac80211 `ieee80211_supported_band` state.

Power-save configuration builds a `C_POWER_TBL` command from PCIe ASPM state, mac80211 power-save flags, DTIM period, and fixed sleep interval vectors. Power updates are deferred during scans unless forced, and successful updates may set `S_POWER_PMI` and ask chip ops to update RX chain flags after chain-noise calibration permits it.

Hardware scan flow starts in `il_mac_hw_scan()`, which stores mac80211 scan state and calls `il_scan_initiate()`. The chip-specific `request_scan` op builds and sends the actual command. Notifications update `S_SCAN_HW`, `scan_start_tsf`, and queue deferred completion work. Completion clears scan state, notifies mac80211, then commits deferred power and Tx power settings and calls `post_scan`. Abort uses `C_SCAN_ABORT` when possible and falls back to `il_force_scan_end()` when firmware does not respond.

Station add flow reserves a station slot under `sta_lock` with `il_prep_station()`, sets driver-active and uCode-in-progress bits, copies a command snapshot, sends `C_ADD_STA`, and processes the response to mark uCode-active or roll back driver-active state. Removal clears driver-active, optionally frees local LQ state, decrements `num_stations`, sends `C_REM_STA`, and clears the entry only after firmware confirms removal. Restore flow resends all driver-active but uCode-inactive stations after RXON/reset and optionally replays saved link-quality commands.

RX/TX queue setup allocates coherent RBD/TFD rings, software SKB/command/meta arrays, initializes circular queue watermarks, and calls chip ops to program queue hardware. Pointer update helpers respect power-save by waking the NIC if `CSR_UCODE_DRV_GP1_BIT_MAC_SLEEP` is set instead of writing stale pointers while firmware SRAM/queues are unavailable.

mac80211 config flow updates SMPS/RX chains, validates requested channels, updates HT width/protection/channel flags, refreshes rate masks, handles power-save and Tx power changes, then commits RXON only when ready and not scanning. BSS changes update QoS, beacon enablement, BSSID, preamble/CTS flags, HT protection, association state, AP/IBSS configuration, and RXON_ASSOC deltas while associated.

Interrupt flow in `il_isr()` disables interrupts, reads CSR/FH interrupt status, ignores shared/spurious interrupts, detects hardware-disappeared sentinel values, masks scheduler interrupts from top-half processing, and schedules `irq_tasklet` for actual service. Firmware/hardware errors set `S_FW_ERROR`, clear active host command state, dump diagnostics, wake waiters, clear ready state, and queue restart work if configured.

## State and Persistence Behavior

Long-lived state lives primarily in `struct il_priv`: status bits (`S_READY`, `S_HCMD_ACTIVE`, `S_RFKILL`, `S_FW_ERROR`, `S_SCANNING`, `S_SCAN_HW`, `S_SCAN_ABORTING`, `S_POWER_PMI`, `S_GEO_CONFIGURED`, `S_CHANNEL_SWITCH_PENDING`, `S_EXIT_PENDING`), EEPROM bytes, channel map, mac80211 bands/rates, active/staging RXON, timing command, HT configuration, power data, Tx power limits and deferred value, scan request/vif/band/start state, station table and key bitmap, queues, ISR stats, watchdog/reset counters, beacon state, QoS command state, and module parameters (`led_mode`, `bt_coex_active`, `il_debug_level`).

Persistent device/firmware state is updated through host commands and registers: RXON channel/filter/association state, station table and link-quality table, Tx power table, power-save sleep policy, Bluetooth coexistence policy, QoS EDCA parameters, scan engine state, firmware statistics clearing, sensitivity/calibration tables through related handlers in companion files, hardware DMA queue addresses/pointers, APM power state, PCIe ASPM workaround bits, interrupt masks, and RF-kill state.

The file uses `il->mutex` for high-level mac80211/config/command sequencing, `reg_lock` for register access, `hcmd_lock` for command queue metadata, `sta_lock` for station state, queue locks for RX write-pointer updates, and `il->lock` for shared radio/QoS/ISR state. Workqueues and timers (`abort_scan`, `scan_completed`, `scan_check`, `restart`, watchdog) persist asynchronous transitions beyond the initiating callback.

## Dependencies and Integration Points

Direct dependencies include Linux kernel networking, PCI, DMA, timers, workqueues, LED class, cfg80211/mac80211 APIs, endian/bit helpers, and device memory allocation. The file includes `common.h`, which brings in `commands.h`, CSR/prph register definitions, driver structs, status bits, queue helpers, and chip operation tables.

Chip-specific integration is through `il->ops`: APM init, EEPROM semaphore acquire/release, command size calculation, TFD attach/free, queue hardware init, byte-count table update, RXON chain update, add-station command building, LED command sending, scan request/post-scan, post-association, Tx power command, broadcast station update, AP config, IBSS station management, NIC error/FH dump, and RXON commit/send helpers declared inline in `common.h` but implemented by 3945/4965 files.

mac80211 integration is broad: scan callbacks, channel/rate registration, HT capability advertisement, interface add/remove/change, config and BSS callbacks, station removal, beacon retrieval, QoS queue config, RF-kill notification, TX protection flags, TX flush, scan completion, channel-switch completion, and supported-band setup.

Firmware ABI integration is defined by `commands.h`: all host commands and notification handlers use the packed command/response structures, command IDs, status masks, and sequence encoding from that header.

## Risks and Edge Cases

Synchronous command submission assumes the caller holds `il->mutex` and that firmware completes within `HZ / 2`. Timeout cleanup clears `CMD_WANT_SKB` in queue metadata, but late firmware completions remain a race-sensitive path.

`_il_grab_nic_access()` returns false on timeout after forcing an NMI, but `il_rd_prph()` and `il_read_targ_mem()` do not check the return before reading. This matches legacy behavior but means timeout paths may still read invalid values.

RX/TX pointer update helpers intentionally skip pointer writes and request NIC wakeup when power-save sleep is detected. Callers must expect progress to resume via later interrupts; otherwise queue stalls can appear during aggressive power management.

Station bookkeeping is split between driver-active, uCode-in-progress, and uCode-active bits. Add/remove/restore paths rely on correct lock ordering and response handling. Failed restore can clear driver-active entries, and duplicate adds return `-EEXIST` even though the existing station may be usable.

`il_remove_station()` decrements `num_stations` before firmware removal succeeds; if `C_REM_STA` fails, driver and firmware state can diverge until reset or explicit recovery.

Scan state has several asynchronous paths. Abort, scan watchdog, firmware completion, interface teardown, and BSSID changes can race; the code uses `S_SCAN_*` bits and deferred work, but tests should cover double-completion and abort-while-completing behavior.

RXON handling is fragile because full RXON clears firmware station/Tx-power state. Callers must validate RXON, decide full versus assoc-only correctly, and replay stations/power where chip-specific commit code requires it.

`il_mac_flush()` waits on queue pointers without explicit sleeping progress notification and ignores its `queues` and `drop` arguments; it is a bounded best-effort wait rather than a full hardware flush.

The watchdog can force firmware reset when queue timestamps stop advancing. False positives are possible if queue pointers fail to update due to power-save, lost interrupts, or command queue accounting bugs.

## Test Signals

Build coverage should include 3945 and 4965 variants, `CONFIG_PM_SLEEP`, `CONFIG_IWLEGACY_DEBUG`, debugfs-related configs, sparse/endian checks, and module parameter builds.

Command-path tests should observe successful sync and async command completion, `CMD_WANT_SKB` reply transfer, huge scan command use, command queue full restart scheduling, RF/CT kill rejection, timeout cleanup, and late completion behavior.

Device lifecycle tests should cover EEPROM read, channel map/geography setup, APM init/stop, firmware alive/error paths, restart work scheduling, RF-kill resume state, and watchdog-triggered reset.

mac80211 tests should cover interface add/remove/change, station add/remove/restore, association/disassociation RXON flows, HT20/HT40 and SMPS transitions, QoS updates, Tx power changes during and after scan, hardware scan completion/abort/watchdog, passive channel restrictions, IBSS beacon updates, channel switch notifications, and RF-kill handling.

Queue/DMA tests should cover RX queue allocation and write-pointer updates, command/TX queue allocation/reset/free/unmap, DMA mapping failure injection in command enqueue, stuck queue detection, and clean teardown with pending commands.

RX/TX data tests should validate decrypt status mapping for WEP/TKIP/CCMP, RTS/CTS protection flag generation for management and data frames, compressed BA and Tx completion routing in chip-specific handlers, and no leaks of reply pages, command buffers, station LQ data, LEDs, channels, or rates across unload/reload.
