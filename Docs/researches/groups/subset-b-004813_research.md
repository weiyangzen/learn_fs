# Research: subset-b-004813

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-mac.c

## Purpose
`3945-mac.c` is the top-level Linux PCI/mac80211 driver file for Intel PRO/Wireless 3945ABG/BG devices. It owns module metadata and parameters, PCI probe/remove, mac80211 registration, firmware loading, runtime bring-up and teardown, interrupt dispatch, RX queue replenishment, TX command construction, hardware scan command construction, RF-kill polling, sysfs controls, and the 3945-specific `ieee80211_ops` table. It connects the generic iwlegacy common layer to 3945 hardware operations implemented in `3945.c` through `il3945_ops`.

## Important APIs, Types, And Functions
The file defines the global `struct il_mod_params il3945_mod_params`, defaulting to software crypto, firmware restart, and disabled hardware scan. `il3945_get_antenna_flags()` converts module antenna selection and EEPROM antenna-switch wiring into RXON antenna flags. Key programming is routed through `il3945_mac_set_key()`: CCMP dynamic keys are supported by `il3945_set_ccmp_dynamic_key_info()`, while TKIP, WEP dynamic keys, and static keys return unsupported or invalid errors.

TX is centered on `il3945_mac_tx()` and `il3945_tx_skb()`. `il3945_tx_skb()` validates RF-kill and rate availability, resolves the station id, prepares a `struct il3945_tx_cmd`, maps the command/header and payload for DMA, attaches buffers to a TFD through `il->ops->txq_attach_buf_to_tfd`, advances the queue write pointer, updates stats, and stops mac80211 queues when low on descriptors. `il3945_build_tx_cmd_basic()`, `il3945_build_tx_cmd_hwcrypto()`, and `il3945_hw_build_tx_cmd_rate()` fill command flags, station id, sequence handling, protection, crypto, lifetime, retry, and rate fields.

RX ownership is handled by `il3945_rx_queue_reset()`, `il3945_rx_allocate()`, `il3945_rx_queue_restock()`, `il3945_rx_replenish()`, and `il3945_rx_handle()`. RX interrupt handling reads firmware write/read state from `rxq->rb_stts`, unmaps pages, dispatches the received command through `il->handlers[pkt->hdr.cmd]`, handles command reclamation with `il_tx_cmd_complete()`, and recycles pages back to `rx_free` or `rx_used`.

Firmware and bring-up are handled by `il3945_read_ucode()`, `il3945_verify_ucode()`, `il3945_set_ucode_ptrs()`, `il3945_init_alive_start()`, `il3945_alive_start()`, `__il3945_up()`, `__il3945_down()`, `il3945_mac_start()`, and `il3945_mac_stop()`. The file reads `iwlwifi-3945-<api>.ucode`, validates API and section sizes against 3945 SRAM limits, allocates coherent firmware descriptors, starts bootstrap/init/runtime firmware, waits for `S_READY`, and tears down DMA, queues, interrupts, and station state.

The interrupt path is `il3945_irq_tasklet()`. It acknowledges CSR and flow-handler interrupt bits, handles hardware/software errors, wakeups, RX, TX service-channel events, unhandled bits, and re-enables interrupts when appropriate. Notification handlers include `il3945_hdl_alive()`, `il3945_hdl_add_sta()`, `il3945_hdl_beacon()`, and `il3945_hdl_card_state()`, with the handler table initialized in `il3945_setup_handlers()`.

mac80211 integration uses `il3945_mac_ops`: start/stop/tx, common interface and config callbacks, filter configuration, key setting, hardware scan callback unless disabled, station add/remove, TX flush, and beacon reporting. PCI integration is through `il3945_pci_probe()`, `il3945_pci_remove()`, and `struct pci_driver il3945_driver`; module init registers the rate-control algorithm before registering the PCI driver.

## Control Flow
Probe allocates `ieee80211_hw`, enables PCI, maps BAR0, initializes locks, resets the NIC, reads EEPROM, sets hardware parameters, initializes channel maps/geography and tx power, requests IRQ/MSI, creates sysfs attributes, initializes workqueue/tasklet/timers, installs RX handlers, initializes power, registers mac80211, registers debugfs, and starts RF-kill polling. Start reads firmware if necessary, calls `__il3945_up()`, and waits for runtime ALIVE to set `S_READY`. Runtime ALIVE verifies firmware, detects RF-kill, sets `S_ALIVE`/`S_READY`, initializes power mode, commits RXON, and starts periodic tx-power recalibration.

For TX, mac80211 calls `il3945_mac_tx()`, which delegates to `il3945_tx_skb()` and frees the skb on failure. Firmware TX responses return via RX command handling and are reclaimed by hardware-specific code in `3945.c`. For RX, interrupts schedule `il3945_irq_tasklet()`, which calls `il3945_rx_handle()` for firmware notifications and received frames. Scan requests are built in `il3945_request_scan()` from `il->scan_request`, SSIDs, channel list, dwell times, antenna flags, probe request IEs, and scan-band-specific rates; completion reconciles deferred RXON changes through `il3945_post_scan()`.

## State And Persistence Behavior
Persistent runtime state is in `struct il_priv`: `status` bits (`S_INIT`, `S_ALIVE`, `S_READY`, `S_RFKILL`, `S_EXIT_PENDING`, `S_FW_ERROR`, scan bits), `active` and `staging` RXON configurations, firmware descriptors and backups, station table, TX/RX queues, `beacon_skb`, measurement status/report, retry rate, tx-power limits, workqueue and timers, IRQ tasklet, and 3945-private RF-kill and thermal work. Module parameters affect behavior for the lifetime of the module. Firmware images are loaded from the kernel firmware loader into DMA-safe buffers and retained until remove. No filesystem state is written by the driver; persistence comes from EEPROM content and module parameters.

## Dependencies And Integration Points
This file depends on Linux PCI, DMA mapping, firmware loading, sysfs, workqueue, timer, tasklet, rfkill, and mac80211 APIs. It depends heavily on `common.h`/`common.c` for station management, command submission, RXON validation, scan helpers, power management, queue helpers, LEDs, debugfs, and PM ops. It uses `commands.h` for firmware command layouts and `3945.h` for 3945 EEPROM, queue, frame, and firmware constants. It integrates with `3945.c` through `il3945_ops` and with `3945-rs.c` through `il3945_rate_control_register()` and station rate initialization.

## Risks And Edge Cases
The code has tight IRQ/tasklet/workqueue/mutex/spinlock interactions; regressions can deadlock or race with remove, restart, RF-kill, or scan cancellation. DMA mapping and queue ownership are high risk: `il3945_tx_skb()` maps the TX command before mapping payload, and failure after the first map must not leak DMA mappings or leave partially initialized descriptors. RX page recycling relies on handlers setting `rxb->page = NULL` when they consume a page. Firmware section validation, ALIVE timeouts, and RF-kill transitions are fragile because startup spans bootstrap, init, and runtime microcode. Hardware crypto is partial, with software crypto enabled by default; changing defaults risks unsupported cipher paths. Sysfs handlers can trigger RXON and tx-power changes while scans or association state transitions are active.

## Test Signals
Useful signals include successful module load/unload with required firmware, PCI probe/remove error-path testing, mac80211 registration and interface creation, RF-kill toggling before and after `mac_start`, scan with hardware scan enabled and disabled, association in station mode, IBSS beaconing, sustained TX/RX traffic under DMA API debug, firmware restart after forced error, sysfs reads/writes for antenna, flags, filter flags, retry rate, tx power, temperature, and measurement, suspend/resume if PM is configured, lockdep/IRQ debugging, and debugfs or kernel log checks for RX/TX queue reclaim and uCode error logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-rs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-rs.c

## Purpose
`3945-rs.c` implements the legacy mac80211 rate-control algorithm named `iwl-3945-rs` for Intel 3945 devices. It tracks per-station transmit success history, derives expected throughput for 802.11a/b/g and protected 2.4 GHz operation, chooses the next transmit rate, updates the firmware-visible fallback behavior indirectly through status feedback, and exposes per-station debugfs rate statistics when mac80211 debugfs is enabled.

## Important APIs, Types, And Functions
The main state is `struct il3945_rs_sta` from `3945.h`, embedded in each station's `drv_priv`. It contains a spinlock, backpointer to `struct il_priv`, expected-throughput table pointer, packet counters, timer state, protection flag, startup rate, last selected rate, and an array of `struct il3945_rate_scale_data` windows. Each window stores a 64-bit success bitmap, success and attempt counters, success ratio, average throughput, and timestamp.

Throughput tables are `il3945_expected_tpt_g`, `il3945_expected_tpt_g_prot`, `il3945_expected_tpt_a`, and `il3945_expected_tpt_b`. RSSI-to-starting-rate tables are `il3945_tpt_table_a` and `il3945_tpt_table_g`. `il3945_get_rate_idx_by_rssi()` selects the initial rate after association. `il3945_clear_win()`, `il3945_rate_scale_flush_wins()`, and `il3945_bg_rate_scale_flush()` age stale sample windows through a timer whose period adapts to packet rate.

`il3945_collect_tx_data()` updates a sliding window for each attempted rate. It shifts in successful or failed attempts, caps the window at `RATE_MAX_WINDOW`, recomputes success ratio, and computes average throughput once enough successes or failures exist. `il3945_rs_tx_status()` is the mac80211 TX-status callback; it uses retry counts from `info->status.rates[0]`, walks hardware fallback rates via `il3945_rs_next_rate()`, updates windows for failed intermediate rates, and updates the final rate with ACK status.

`il3945_rs_get_rate()` is the mac80211 get-rate callback. It starts from the station's last rate, applies supported-rate and user rate-mask constraints, optionally consumes a one-shot RSSI-derived `start_rate`, checks whether enough statistics exist, compares current/adjacent throughput and success ratio, and writes `info->control.rates[0]` with the selected mac80211 rate index and count. `il3945_get_adjacent_rate()` finds lower and higher usable rates, with special handling for 5 GHz OFDM-only ordering and 2.4 GHz/TGg fallback chains.

The mac80211 registration object is `rs_ops`, with callbacks for alloc/free, per-station allocation/free, tx status, get rate, a stub rate-init callback, and optional debugfs registration. `il3945_rate_control_register()` and `il3945_rate_control_unregister()` are called by module init/exit in `3945-mac.c`. Driver-side association initialization uses `il3945_rs_rate_init()` and `il3945_rate_scale_init()`.

## Control Flow
At module init, `rs_ops` is registered with mac80211. When a station is allocated, `il3945_rs_alloc_sta()` initializes the per-station spinlock and flush timer. When the driver adds a station, `il3945_rs_rate_init()` attaches the device pointer, clears all rate windows, picks the highest supported initial table index, and stores the station supported-rate mask in `il->_3945.sta_supp_rates`. After association, `il3945_rate_scale_init()` selects the expected throughput table based on the current band and protection flags, reads the last network RSSI from `il->_3945.last_rx_rssi`, and sets a one-shot start rate.

For every outgoing frame, mac80211 calls `il3945_rs_get_rate()`. The function chooses a rate from local station history and constraints, then `3945-mac.c` builds the TX command using the chosen rate. After firmware reports completion, `il3945_rs_tx_status()` receives the retry count and ACK flag, updates statistics, and may schedule the flush timer. The flush timer clears stale windows and adapts its next period based on recent packet throughput; when no unflushed windows remain, it stops rescheduling.

## State And Persistence Behavior
Rate-control state is per station and volatile. It is initialized on station add/allocation, reset by timer aging, and deleted with the station. It persists only while the station object lives. It also depends on global device state in `struct il_priv`: current band, RXON protection flags, last RX RSSI, retry-rate module/sysfs setting, and supported-rate mask. No persistent storage or firmware NVM is changed.

## Dependencies And Integration Points
This file depends on mac80211 rate-control APIs, station private data sizing configured in `3945-mac.c`, 3945 rate metadata exported by `3945.c`, and helper constants/macros from `common.h`, `commands.h`, and `3945.h`. TX status comes from the 3945 TX response handler in `3945.c`; rate selections are consumed by TX command construction in `3945-mac.c` and `3945.c`. Debugfs integration is through mac80211's per-station rate-control debugfs hook.

## Risks And Edge Cases
The algorithm assumes valid `rs_sta->il` before meaningful rate selection; it attempts to treat uninitialized state as missing, but `il3945_rs_get_rate()` still works with the `rs_sta` pointer and requires station data to be correctly initialized by the driver. Rate index translation differs between 5 GHz and 2.4 GHz, so off-by-`IL_FIRST_OFDM_RATE` errors can select invalid mac80211 table entries. Retry accounting depends on firmware and mac80211 status count semantics; incorrect counts distort success windows and rate decisions. Timer teardown must use `timer_delete_sync()` because callbacks hold station state. Throughput thresholds are fixed heuristics and can behave poorly with unusual rate masks, sparse traffic, or changing channel conditions.

## Test Signals
Test with station association on 2.4 GHz CCK-only, 2.4 GHz mixed G, protected/TGg, and 5 GHz networks. Confirm selected rates stay within supported and user rate masks, debugfs `rate_stats_table` counters update, rate windows age out after traffic stops, timers do not fire after station removal, and TX status retry counts produce expected lower-rate fallback. Stress traffic with variable RSSI or attenuation should show rate changes rather than invalid indices or stuck rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945.c

## Purpose
`3945.c` implements Intel 3945 hardware-specific operations behind the common iwlegacy driver. It defines 3945 rate metadata, TX response handling, RX frame translation, DMA queue programming, firmware bootstrap loading, EEPROM semaphore behavior, RXON commit logic, station/IBSS helpers, rate fallback table setup, LED command submission, tx-power calibration from EEPROM and temperature, and the 3945 PCI ID/configuration table. Its exported `const struct il_ops il3945_ops` is the main integration surface consumed by `3945-mac.c` and common iwlegacy code.

## Important APIs, Types, And Functions
`il3945_rates[]` maps each 3945 legacy rate to PLCP code, IEEE rate, adjacent software and hardware fallback indices, and firmware rate-table indices. `il3945_rs_next_rate()` returns a previous/fallback rate with band-specific corrections for 5 GHz OFDM and CCK-only 2.4 GHz stations. `il3945_init_hw_rate_table()` builds and sends two `C_RATE_SCALE` tables for control and data frames.

TX completion uses `il3945_hdl_tx()` and `il3945_tx_queue_reclaim()`. The handler validates queue/index, handles passive-channel TX failures by stopping queues, converts firmware PLCP rate to mac80211 rate index, fills `ieee80211_tx_info` ACK/retry status, logs failures, and reclaims completed queue entries. TFD management is implemented by `il3945_hw_txq_attach_buf_to_tfd()` and `il3945_hw_txq_free_tfd()`.

RX frame delivery uses `il3945_hdl_rx()` and `il3945_pass_packet_to_mac80211()`. The handler builds `ieee80211_rx_status` from 3945 RX stats/header/end structures, validates PHY count, CRC, and FIFO status, converts RSSI with `IL39_RSSI_OFFSET`, tracks beacon/TSF/RSSI for network packets, wakes queues stopped for passive-channel RX, sets decrypt status when hardware crypto is enabled, and either copies small frames into a new skb or attaches the RX page as a fragment.

Hardware initialization and DMA setup include `il3945_apm_init()`, `il3945_nic_config()`, `il3945_hw_nic_init()`, `il3945_rx_init()`, `il3945_tx_reset()`, `il3945_txq_ctx_reset()`, `il3945_hw_tx_queue_init()`, `il3945_hw_rxq_stop()`, `il3945_hw_txq_ctx_stop()`, and `il3945_hw_txq_ctx_free()`. `il3945_hw_set_hw_params()` allocates shared DMA memory and fills queue, station, RX, and beacon timing constants.

RXON and station integration is in `il3945_commit_rxon()`, `il3945_send_rxon_assoc()`, `il3945_build_addsta_hcmd()`, `il3945_add_bssid_station()`, and `il3945_manage_ibss_station()`. `il3945_commit_rxon()` validates staging RXON, selects antenna flags, uses RXON_ASSOC when possible, clears association before full tune when necessary, toggles hardware crypto, sends full `C_RXON`, restores stations, sets TX power, and refreshes the hardware rate table.

Tx-power handling is a major section. It initializes per-channel power from EEPROM calibration groups in `il3945_txpower_set_from_eeprom()`, maps channels to calibration groups with `il3945_hw_reg_get_ch_grp_idx()`, interpolates gain-table indices with `il3945_hw_reg_get_matched_power_idx()`, clamps via `il3945_hw_reg_fix_power_idx()`, compensates temperature through `il3945_hw_reg_adjust_power_by_temp()` and `il3945_hw_reg_comp_txpower_temp()`, sends `C_TX_PWR_TBL` with `il3945_send_tx_power()`, handles user tx-power limit changes with `il3945_hw_reg_set_txpower()`, and schedules periodic recalibration with `il3945_reg_txpower_periodic()`.

Firmware bootstrap support is implemented by `il3945_load_bsm()` and `il3945_verify_bsm()`. These program BSM DRAM pointers to initialization ucode, copy bootstrap ucode into BSM SRAM, verify it, trigger BSM copy into instruction SRAM, and enable future power-management reloads.

## Control Flow
During probe, `3945-mac.c` calls `il3945_hw_set_hw_params()` and later `il3945_hw_nic_init()`. NIC init powers and configures the device, allocates or resets RX queues, replenishes RX pages, initializes RX DMA registers, writes the RX write pointer, resets TX scheduler/DMA context, initializes all TX queues, and sets `S_INIT`. Firmware load then calls `il3945_load_bsm()` through `il->ops->load_ucode`.

At runtime, the handler table installed by `il3945_hw_handler_setup()` dispatches `C_TX` to TX completion and `N_3945_RX` to RX delivery. RXON changes flow from common/mac80211 state into `il3945_commit_rxon()`, which chooses between partial association update and full radio retune. Association/IBSS paths add BSSID stations, sync base rates, initialize rate scaling, and send beacons through the beacon command support in `3945-mac.c`.

## State And Persistence Behavior
State lives in `struct il_priv`, especially `_3945` private fields: shared DMA pointer/physical address, statistics, accumulated debug stats, clip groups, thermal periodic work, station supported rates, last beacon TSF/time/RSSI, and RF/thermal calibration state. Per-channel state in `il->channel_info` is populated from EEPROM and current temperature, then updated on user tx-power changes and periodic thermal recalibration. EEPROM data is read-only. Hardware registers and firmware state are programmed every bring-up and RXON transition.

## Dependencies And Integration Points
This file uses register definitions from `3945.h`, command definitions from `commands.h`, common station/queue/power/channel helpers from `common.h`, and Linux DMA/mac80211 APIs. It exports `il3945_ops`, `il3945_rates`, and `il3945_hw_card_ids` to the rest of the module. It consumes firmware command transport through `il_send_cmd*` helpers and consumes mac80211 status/RX APIs for TX completion and RX delivery.

## Risks And Edge Cases
The tx-power code depends on valid EEPROM calibration data; invalid saturation power, duplicate sample powers, or out-of-range temperatures can produce wrong gain-table indices. RX page ownership is subtle: large packets transfer the page into an skb fragment and must set `rxb->page = NULL` to prevent recycling. TX reclaim must validate firmware sequence indices to avoid freeing the wrong skb/TFD. RXON transitions can break association if station restore, tx-power send, or rate-table initialization fails after a full tune. BSM programming is hardware-specific and failures leave the device unable to start firmware. Passive-channel TX failures intentionally stop queues until a valid RX frame arrives, so tests need to cover queue wakeup.

## Test Signals
Signals include successful EEPROM parsing and channel map initialization, firmware BSM verification, RX/TX DMA under traffic, TX status ACK/retry reporting into rate control, queue stop/wake on passive-channel failures, RX RSSI/rate/band correctness, association and IBSS station creation/removal, RXON_ASSOC versus full RXON transitions, tx-power sysfs changes, thermal recalibration work, `C_TX_PWR_TBL` command success, and PCI ID matching for BG and ABG variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945.h

## Purpose
`3945.h` is the hardware contract header for Intel 3945 iwlegacy support. It defines firmware file/API bounds, 3945-specific station and rate-control state, frame and RX parsing helpers, EEPROM layout and calibration structures, queue and DMA constants, SRAM and flow-handler register offsets, TFD layouts, public prototypes shared between `3945-mac.c`, `3945.c`, `3945-rs.c`, debug code, and common iwlegacy code, and external exports for PCI IDs, operations, rates, and module parameters.

## Important APIs, Types, And Definitions
Firmware naming and compatibility are controlled by `IL3945_UCODE_API_MAX`, `IL3945_UCODE_API_MIN`, `IL3945_FW_PRE`, and `IL3945_MODULE_FIRMWARE()`. `IL_NOISE_MEAS_NOT_AVAILABLE` provides the legacy unavailable-noise sentinel. `extern struct il_mod_params il3945_mod_params`, `extern const struct il_ops il3945_ops`, and `extern const struct pci_device_id il3945_hw_card_ids[]` tie the module entry file to hardware implementation and PCI matching.

Rate control state is described by `struct il3945_rate_scale_data`, `struct il3945_rs_sta`, and `struct il3945_sta_priv`. `struct il3945_sta_priv` deliberately places `struct il_station_priv_common common` first so common 3945/4965 station handling can cast safely. `enum il3945_antenna` defines diversity/main/aux module parameter values.

Frame and RX parsing definitions include `struct il3945_frame`, `struct il3945_ibss_seq`, `IL_RX_HDR()`, `IL_RX_END()`, `IL_RX_STATS()`, and `IL_RX_DATA()`. The macros account for variable PHY stats length in firmware RX frames and are used by `3945.c` to find the MAC payload and trailer.

The header declares key cross-file functions: RX replenishment/reset, beacon filling, NIC event/error dumping, handler/work setup, DMA queue operations, temperature and tx-power operations, stats handlers, RXON commit, association/AP/scan hooks, antenna flag selection, rate table initialization, periodic tx-power recalibration, and rate-control helper `il3945_rs_next_rate()`.

EEPROM structures include `struct il3945_eeprom_txpower_sample`, `struct il3945_eeprom_txpower_group`, `struct il3945_eeprom_temperature_corr`, and the full packed `struct il3945_eeprom` map. The map records fixed offsets for device id, MAC address, board data, version, SKU, LED fields, regulatory channel bands, tx-power calibration groups, and temperature correction coefficients. `IL3945_EEPROM_IMG_SIZE` fixes the expected EEPROM image size at 1024 bytes.

Queue/register definitions include `IL39_NUM_QUEUES`, `IL39_CMD_QUEUE_NUM`, `NUM_TFD_CHUNKS`, TFD control macros, RTC instruction/data SRAM bounds, `il3945_hw_valid_rtc_data_addr()`, `struct il3945_shared`, flow-handler register offsets (`FH39_*`), RX/TX config bit masks, and packed `struct il3945_tfd_tb`/`struct il3945_tfd`.

## Control Flow Role
This header has no executable control flow aside from the inline RTC-data address validator. Its role is compile-time coordination: the MAC file owns module lifecycle and calls prototypes here; the hardware file implements most prototypes and uses the register/EEPROM definitions; the rate-control file uses station/rate state definitions; common iwlegacy code calls through `il3945_ops` and shared prototypes.

## State And Persistence Behavior
The header defines the shapes of persistent-in-memory state. EEPROM layout structures mirror on-device nonvolatile data and must remain packed and offset-compatible. Station private state persists for the life of a mac80211 station. Frame pools, TFDs, shared DMA memory, RX parsing views, and calibration tables are runtime only. Register constants encode hardware ABI and are effectively persistent contracts with the 3945 device/firmware.

## Dependencies And Integration Points
It includes Linux PCI/kernel types, radiotap/mac80211-adjacent definitions, and `common.h`. It is included by all 3945 implementation files and debug support. The packed EEPROM and TFD structures must match firmware/hardware expectations from `commands.h` and the device datasheet; any layout drift breaks DMA, EEPROM parsing, or firmware command construction.

## Risks And Edge Cases
Because this file defines binary hardware-facing layouts, padding, packing, endian annotations, and offsets are high-risk. Changing `struct il3945_eeprom`, `struct il3945_tfd`, `struct il3945_shared`, or RX macros can corrupt EEPROM interpretation, DMA descriptors, or RX frame parsing. The RX macros assume valid `phy_count` and packet layout; callers must validate bounds before trusting payload pointers. Queue constants must stay aligned with hardware queue count and command queue id. The declaration `il4965_get_temperature()` in a 3945 header reflects shared legacy naming and can confuse refactors.

## Test Signals
Build coverage is the first signal: all 3945 files should compile without layout or prototype mismatches. Runtime signals include correct firmware selection, EEPROM MAC/channel/tx-power parsing, valid RX payload lengths and RSSI conversion, stable TFD DMA operation under traffic, correct command queue id behavior, and successful debugfs/sysfs/error-log paths that rely on the declared structs and helper prototypes. Static checks should flag accidental padding or endian changes in packed hardware structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-calib.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-calib.c

## Purpose
`4965-calib.c` implements runtime calibration algorithms for Intel 4965-class iwlegacy devices. It adjusts receiver sensitivity from firmware statistics, performs CCK energy and OFDM auto-correlation tuning, detects disconnected antenna chains, computes differential gain corrections, sends calibration commands to firmware, updates chain flags, and resets runtime calibration state after association/startup. Although it sits in the same iwlegacy directory as 3945 support, it targets 4965 calibration data structures and firmware commands.

## Important APIs, Types, And Functions
`struct stats_general_data` is a local compact copy of beacon silence RSSI and beacon energy values used by CCK sensitivity logic after endian conversion under lock. The core sensitivity state is `struct il_sensitivity_data` in `il->sensitivity_data`, with ranges supplied by `il->hw_params.sens`.

`il4965_sens_energy_cck()` tunes CCK sensitivity. It derives false-alarm counts normalized against RX enabled time, tracks a 20-beacon silence RSSI history and a 10-beacon energy history, maintains consecutive low-false-alarm counts, updates energy threshold `nrg_th_cck`, and adjusts CCK auto-correlation values within hardware-provided min/max ranges. It uses states such as `IL_FA_TOO_MANY`, `IL_FA_TOO_FEW`, and `IL_FA_GOOD_RANGE` to decide whether to increase margin or sensitivity.

`il4965_sens_auto_corr_ofdm()` tunes OFDM auto-correlation thresholds. It compares normalized OFDM false alarms with min/max thresholds and adjusts OFDM x4/x1 and MRC variants up to reduce sensitivity or down to increase sensitivity.

`il4965_prepare_legacy_sensitivity_tbl()` converts `struct il_sensitivity_data` into the firmware sensitivity table indices, and `il4965_sensitivity_write()` sends an async `C_SENSITIVITY` command only when the new table differs from `il->sensitivity_tbl`. `il4965_init_sensitivity()` initializes all sensitivity fields from range defaults and writes the initial table. `il4965_sensitivity_calibration()` consumes periodic firmware statistics, validates association and interference-data availability, computes delta counters for false alarms and bad PLCP since the previous sample, runs OFDM and CCK tuning, and writes the table if changed.

Chain-noise calibration starts with `il4965_chain_noise_calibration()`. It accumulates beacon silence noise and signal per chain for `il->cfg->chain_noise_num_beacons` samples on the associated channel only. `il4965_find_disconn_antenna()` compares average signal by chain to detect disconnected antennas, masks active chains to valid RX antennas, and ensures at least one valid TX chain remains connected. `il4965_gain_computation()` computes per-chain differential gain codes from average silence noise, sends `C_PHY_CALIBRATION` with `IL_PHY_CALIBRATE_DIFF_GAIN_CMD` once, and marks calibration state. `il4965_find_first_chain()` selects a default chain from an antenna mask. `il4965_reset_run_time_calib()` clears sensitivity and chain-noise state, initializes delta gain codes, and requests fresh statistics.

## Control Flow
After runtime calibration reset, firmware statistics are requested asynchronously. Sensitivity is initialized from hardware range defaults by `il4965_init_sensitivity()`. When statistics notifications arrive, higher-level 4965 handlers call `il4965_sensitivity_calibration()` and `il4965_chain_noise_calibration()`. Sensitivity calibration runs repeatedly while associated, using monotonic firmware counters to compute deltas and sending `C_SENSITIVITY` only for changed tables. Chain-noise calibration runs only while `chain_noise_data.state == IL_CHAIN_NOISE_ACCUMULATE`; after the configured beacon count, it computes disconnected chains and differential gain, optionally calls `il->ops->update_chain_flags()`, sets state to done, and updates power mode.

## State And Persistence Behavior
All state is volatile in `struct il_priv`: `sensitivity_data`, `sensitivity_tbl`, `chain_noise_data`, disable flags (`disable_sens_cal`, `disable_chain_noise_cal`), hardware sensitivity ranges, antenna masks, chain counts, RXON staging channel/band, and config beacon count. The algorithms preserve short histories across beacon samples but reset through `il4965_reset_run_time_calib()`. Firmware receives sensitivity and differential-gain commands, but no persistent EEPROM/NVM data is written.

## Dependencies And Integration Points
The file depends on `common.h` for `struct il_priv`, stats structures, command submission, association checks, locks, and calibration constants, and on `4965.h` for 4965-specific declarations and antenna definitions. It uses mac80211 only indirectly through common driver state. Firmware integration is via async `C_SENSITIVITY`, `C_PHY_CALIBRATION`, and stats requests. RXON/chain integration is through `il->ops->update_chain_flags()` and `il_power_update_mode()`.

## Risks And Edge Cases
Statistics counters are monotonic but can wrap or reset; the code handles decreases by resetting baselines, but unusual firmware behavior can skew one calibration interval. Division by `rx_enable_time` is avoided by an explicit zero check; chain-noise averaging depends on nonzero `chain_noise_num_beacons`. Chain detection can fail when firmware reports zero signals; the code masks against valid RX antennas and forces a valid TX chain, but bad antenna masks in config can still produce poor chain selection. Sensitivity changes are bounded by range tables, so invalid `hw_params.sens` or missing ranges disable useful calibration. Locking is limited to copying stats and RXON channel state; calibration decisions run after releasing `il->lock`, so concurrent association/channel changes can cause stats to be ignored or calibration to apply after state transitions.

## Test Signals
Useful signals include calibration initialization after association, periodic stats notifications with `INTERFERENCE_DATA_AVAILABLE`, changing `C_SENSITIVITY` commands only when tables differ, stable behavior with zero RX enable time, false-alarm counter wrap/reset handling, chain-noise accumulation only on the associated channel/band, differential gain command sent once, active chain mask updates matching valid antenna masks, power-mode update after calibration completion, and disable flags preventing command emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-calib.c -->
