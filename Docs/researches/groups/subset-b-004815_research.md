# Research: subset-b-004815

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-rs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-rs.c

## Purpose

`4965-rs.c` implements the Intel 4965-specific mac80211 rate-control algorithm named `iwl-4965-rs`. It translates between mac80211 rates and 4965 firmware `rate_n_flags`, keeps per-station link-quality state, collects transmit success history, chooses fallback tables for firmware, searches among legacy, SISO, MIMO2, antenna, short-GI, HT40, greenfield, and aggregation modes, and exposes debugfs controls for fixed-rate and rate-stat inspection.

The file is the policy layer between mac80211 TX status/rate-control callbacks and the iwlegacy firmware command `C_TX_LINK_QUALITY_CMD` sent by `il_send_lq_cmd()`.

## Important APIs, Types, and Functions

Exported API:

- `il_rates[]` is the 4965 rate metadata table used by this file and other 4965 code. It maps rate indexes to legacy PLCP, SISO/MIMO PLCP, IEEE rate values, and adjacent rate indexes.
- `il4965_rs_rate_init()` initializes a station's `struct il_lq_sta` after station creation and sends the first synchronous link-quality command.
- `il4965_rate_control_register()` and `il4965_rate_control_unregister()` register and unregister the `rate_control_ops` instance with mac80211.

mac80211 rate-control callbacks:

- `il4965_rs_tx_status()` consumes TX status, validates that the reported first rate matches the current firmware LQ table, updates rate windows for AMPDU or non-AMPDU attempts, and calls the rate-scaling engine.
- `il4965_rs_get_rate()` fills `info->control.rates[0]` from `lq_sta->last_rate_n_flags`, including MCS, SGI, HT40, duplicate-data, and greenfield flags.
- `il4965_rs_alloc()`, `il4965_rs_free()`, `il4965_rs_alloc_sta()`, `il4965_rs_free_sta()`, and `il4965_rs_rate_init_stub()` satisfy mac80211's rate-control allocation contract.

Core local helpers:

- `il4965_hwrate_to_plcp_idx()`, `il4965_rate_n_flags_from_tbl()`, and `il4965_rs_get_tbl_info_from_mcs()` translate among firmware flags, local rate indexes, and `struct il_scale_tbl_info`.
- `il4965_rs_collect_tx_data()` maintains a 62-entry sliding success bitmap per rate and derives success ratio and average throughput.
- `il4965_rs_rate_scale_perform()` is the main decision engine for rate movement and modulation-mode search.
- `il4965_rs_fill_link_cmd()` builds the firmware retry table, including repeated HT tries, fallback to lower rates, and antenna toggling for legacy retries.
- `il4965_rs_switch_to_siso()`, `il4965_rs_switch_to_mimo2()`, `il4965_rs_move_legacy_other()`, `il4965_rs_move_siso_to_other()`, and `il4965_rs_move_mimo2_to_other()` build candidate search tables for mode changes.
- Traffic-load helpers `il4965_rs_tl_add_packet()`, `il4965_rs_tl_get_load()`, and `il4965_rs_tl_turn_on_agg*()` decide when to request BA aggregation for a TID.
- Debugfs helpers implement `rate_scale_table`, `rate_stats_table`, `rate_scale_data`, and `tx_agg_tid_enable` station files when `CONFIG_MAC80211_DEBUGFS` is enabled.

Important data includes expected throughput tables for legacy, SISO 20/40 MHz, and MIMO2 20/40 MHz modes with normal, SGI, aggregation, and aggregation+SGI variants.

## Control Flow

Station setup starts in `il4965_rs_rate_init()`. The driver clears both LQ tables' rate windows, records supported legacy/SISO/MIMO2 masks from the station and HT capabilities, chooses single- and dual-stream antenna masks from `valid_tx_ant`, sets initial aggregation permission, picks the lowest supported starting rate, and calls `il4965_rs_initialize_lq()`. Initialization builds a legacy starting rate on the first valid TX antenna, sets the expected throughput table, stores the LQ pointer in `il->stations[sta_id].lq`, and sends the firmware LQ command synchronously.

For each packet, mac80211 calls `il4965_rs_get_rate()`. This callback does not run the full algorithm; it reports the last selected rate in mac80211's format and updates `max_rate_idx` from `txrc->rate_idx_mask`. The firmware retry table remains the real fallback source.

After transmission, `il4965_rs_tx_status()` validates the status. If the packet is not data, is no-ack, or is an AMPDU without AMPDU status, it is ignored. The first reported mac80211 rate is compared against `lq.rs_table[0]`; repeated mismatches increment `missed_rate_counter`, and after `IL_MISSED_RATE_MAX` the driver resends the current LQ command to resynchronize firmware and driver. Matching status is attributed to the active table or search table. AMPDU status updates the first-rate window with aggregate length and ack length. Non-AMPDU status walks retry entries and records failed attempts plus the final success/failure in matching rate tables.

`il4965_rs_rate_scale_perform()` then chooses a new rate or mode. It updates per-TID traffic load, detects whether aggregation is active, selects the active or search table, masks rates by association capabilities, and waits until enough successes or failures exist before acting. If in search mode, it compares the search table's measured throughput with `last_tpt`: better search tables become active, worse ones are discarded and the active firmware LQ table is restored. If not searching, it compares current, adjacent-lower, and adjacent-higher throughput and success ratio to decide whether to move down, move up, or hold rate.

When the current mode has been used long enough, `il4965_rs_stay_in_table()` allows a new mode search. The move helpers try candidate actions in a rotating order: legacy can switch antennas, SISO, or MIMO2; SISO can switch antenna, MIMO2, or SGI; MIMO2 can switch antenna, SISO, or SGI. Successful candidates populate the inactive table as the search table and send a new firmware LQ command. When HT mode is stable and throughput is high enough, the code may start TX BA aggregation for the observed TID.

`il4965_rs_fill_link_cmd()` converts the chosen first rate into the 4965 retry table. HT rates are repeated `IL_HT_NUMBER_TRY` times before falling back, while legacy rates use one try and may rotate antennas. After the first fallback step, HT fallback is disabled so the lower-rate path can fall back to legacy A/G rates. Aggregation limits are also written into the LQ command.

## State and Persistence Behavior

Long-lived state is per-station in `struct il_lq_sta`, embedded in mac80211 station private data. It persists across packets and contains:

- two `lq_info[]` tables, one active and one search, each with per-rate sliding windows;
- the firmware `struct il_link_quality_cmd lq`;
- active legacy/SISO/MIMO2 rate masks, supported rates, current band, last selected rate index and flags;
- search state such as `active_tbl`, `search_better_tbl`, `stay_in_tbl`, `action_counter`, success/failure totals, and flush timers;
- traffic-load history per TID and aggregation enable bits;
- debugfs fixed-rate override state when enabled.

Firmware state persists in the device station table after `il_send_lq_cmd()`. The retry table sent here directly affects later hardware transmissions until another LQ command replaces it. The code also triggers mac80211 BA-session state changes via `ieee80211_start_tx_ba_session()` and `ieee80211_stop_tx_ba_session()`.

## Dependencies and Integration Points

Direct dependencies include:

- mac80211 rate-control APIs, TX status structures, HT capabilities, station private data, debugfs station hooks, and BA-session management;
- iwlegacy common definitions in `common.h` for `struct il_priv`, `struct il_lq_sta`, rate masks, LQ table constants, debug macros, and command sending;
- `4965.h` for 4965 rate and driver interfaces;
- firmware command ABI fields such as `rate_n_flags`, `LINK_QUAL_MAX_RETRY_NUM`, and antenna bit masks.

The file is compiled into the `iwl4965` module and is registered by 4965 module setup code outside this file. Runtime integration depends on station add flows calling `il4965_rs_rate_init()` after the firmware station entry exists.

## Risks and Edge Cases

- Rate-status mismatches are expected during table transitions, but persistent mismatches cause LQ resends. Bugs in mac80211-to-firmware rate translation can silently discard status samples and destabilize rate control.
- `il4965_rs_get_adjacent_rate()` starts with `mask = (1 << i)` after `i = idx - 1`; callers must not pass `idx == 0` into the A/HT branch without care because a negative shift would be undefined. Current call paths usually check masks and fallbacks first, but this is a fragile boundary.
- Debugfs read functions allocate fixed 1024-byte buffers while printing table data. The output format should be reviewed for overflow risk if constants grow.
- `il4965_rs_dbgfs_set_mcs()` assumes `lq_sta->drv` is valid when debugfs is enabled; debugfs access after teardown would rely on mac80211 station lifetime ordering.
- Aggregation start is driven by local traffic history and state checks. Incorrect `tid_data->agg.state` synchronization could repeatedly request or suppress BA sessions.
- The algorithm uses many static thresholds and expected throughput tables tuned for 4965 hardware. Changes to rate constants, HT capability interpretation, or antenna masks can produce poor performance without compile failures.

## Test Signals

- Build with and without `CONFIG_MAC80211_DEBUGFS` and `CONFIG_IWLEGACY_DEBUG`.
- Associate to 2.4 GHz and 5 GHz APs, then verify initial LQ command, rate selection, and legacy fallback behavior.
- Exercise HT20, HT40, SGI, greenfield, SISO, and MIMO2 capability combinations and confirm firmware `rate_n_flags` match mac80211 TX status.
- Run traffic that triggers aggregation and verify BA session start/stop plus `is_agg` throughput table selection.
- Use debugfs fixed-rate writes with valid and invalid antenna masks and confirm LQ command behavior.
- Fault or trace repeated TX status mismatch to confirm `missed_rate_counter` resends the LQ command and then recovers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965.c

## Purpose

`4965.c` is the Intel Wireless WiFi Link 4965AGN device-specific operations file. It provides 4965 firmware bootstrap and verification, EEPROM access and validation, NIC radio configuration, TX power and temperature calibration, RXON commit/channel-switch handling, station-command layout conversion, post-scan/post-association/AP setup, LED command support, and the `il4965_ops`/`il4965_cfg` structures consumed by the iwlegacy common layer.

This file is not the whole 4965 driver. It plugs hardware-specific behavior into shared iwlegacy code and delegates TX/RX, mac80211 handlers, calibration details, station/key handling, and debug support to sibling files such as `4965-mac.c`, `4965-calib.c`, `4965-debug.c`, and common iwlegacy modules.

## Important APIs, Types, and Functions

Exported or externally referenced functions:

- `il4965_verify_ucode()` checks whether bootstrap, init, or runtime firmware instruction SRAM matches host images.
- `il4965_eeprom_acquire_semaphore()`, `il4965_eeprom_release_semaphore()`, `il4965_eeprom_check_version()`, and `il4965_eeprom_get_mac()` implement 4965 EEPROM ownership and metadata access.
- `il4965_led_enable()` directly enables the LED register; `il4965_send_led_cmd()` is exported through `il4965_ops`.
- `il4965_nic_config()` writes EEPROM radio configuration into hardware interface registers and stores the calibration-info pointer.
- `il4965_temperature_calib()` refreshes calibrated temperature and schedules TX power work when thermal drift exceeds the threshold.
- `il4965_ops` is the device method table used by shared iwlegacy logic.
- `il4965_cfg` describes the hardware name, firmware API, antenna masks, EEPROM requirements, queue counts, calibration policy, regulatory EEPROM bands, and module parameters.

Core local functions:

- `il4965_verify_inst_sparse()`, `il4965_verify_inst_full()`, `il4965_verify_bsm()`, `il4965_load_bsm()`, `il4965_set_ucode_ptrs()`, and `il4965_init_alive_start()` implement the two-stage BSM/init/runtime firmware boot path.
- `il4965_fill_txpower_tbl()` constructs all 33 rate/chain TX power table entries using regulatory limits, saturation/backoff, EEPROM factory calibration, temperature, voltage, and MIMO chain attenuation.
- `il4965_send_tx_power()` wraps the TX power table in `C_TX_PWR_TBL`.
- `il4965_send_rxon_assoc()` sends a lightweight `C_RXON_ASSOC` when only association-related RXON fields change.
- `il4965_commit_rxon()` validates and commits staging RXON state using either `C_RXON_ASSOC` or full `C_RXON`, handles station/key restoration, and sends TX power after retune.
- `il4965_hw_channel_switch()` builds the 4965 channel-switch command with switch timing and per-channel TX power.
- `il4965_txq_update_byte_cnt_tbl()` mirrors packet byte counts into the scheduler byte-count table.
- `il4965_hw_get_temperature()` computes Kelvin temperature from alive/statistics calibration fields.
- `il4965_build_addsta_hcmd()` converts common add-station command layout into the 4965 firmware command layout.
- `il4965_post_scan()`, `il4965_post_associate()`, and `il4965_config_ap()` perform mode-specific RXON, timing, beacon, calibration, and power-management follow-up.

## Control Flow

Firmware boot starts through the `load_ucode` operation, `il4965_load_bsm()`. The driver writes init-code DMA pointers into BSM registers, copies bootstrap instructions into BSM SRAM, verifies them, copies bootstrap into instruction SRAM, and enables future BSM reloads. When init firmware sends ALIVE, `il4965_init_alive_start()` verifies SRAM, computes initial temperature from alive calibration fields, writes runtime instruction/data pointers with `il4965_set_ucode_ptrs()`, and lets init firmware launch runtime firmware. If verification or pointer setup fails, it queues the driver restart work.

NIC configuration in `il4965_nic_config()` runs under `il->lock`. It reads EEPROM radio config, sets radio/MAC silicon bits in `CSR_HW_IF_CONFIG_REG`, and stores `il->calib_info` from EEPROM TX-power calibration storage. EEPROM access itself is protected by a hardware semaphore in `il4965_eeprom_acquire_semaphore()`.

TX power calculation flows from `il4965_send_tx_power()` to `il4965_fill_txpower_tbl()`. The function derives band, HT40 status, and control channel location from active RXON, validates channel information, maps the channel to a TX attenuation group, adjusts HT40 center channel, clamps EEPROM saturation and regulatory limits, interpolates factory calibration for the target channel, calculates voltage compensation from EEPROM and init-alive values, clamps and converts current temperature, and then fills each rate entry for both TX chains. Each entry accounts for MIMO regulatory half-power, saturation backoff, user limit, temperature compensation, voltage compensation, MIMO chain attenuation, CCK compensation, and gain-table bounds before writing DSP/radio gain fields.

RXON commit is handled by `il4965_commit_rxon()`. It refuses work if firmware is not alive, forces TSF-to-host, validates the staged command, aborts pending channel switch when retuning elsewhere, and chooses `C_RXON_ASSOC` when a full retune is unnecessary. Full RXON may first clear the associated bit on the active configuration so firmware accepts a new associated configuration. Unassociated RXON clears firmware station state, so the driver restores stations and default WEP keys afterward. Associated RXON sets `start_calib = 0`, sends the staged RXON, then initializes sensitivity and sends TX power because a retune requires fresh gain settings.

Post-association logic cancels scans, toggles RXON through unassociated and associated states, sends timing, applies HT and RX chain selection, sets AID/preamble/slot flags, sends beacons for IBSS, updates power mode if chain-noise calibration is already done, starts chain-noise calibration, and enables runtime calibration. AP configuration follows a similar RXON timing and beacon-before-associated-RXON sequence.

Channel switching builds a 4965-specific command from mac80211 channel switch data. It calculates firmware switch time from TSF, beacon interval, and switch count, marks whether radar-channel beacons are expected, embeds a TX power table for the destination channel, and sends `C_CHANNEL_SWITCH`.

## State and Persistence Behavior

Persistent driver state updated here includes:

- firmware image state (`il->ucode_type`, BSM register pointers, runtime/data backup DMA locations);
- EEPROM-derived `il->calib_info`, MAC address reads, version checks, and radio config bits;
- `il->temperature`, `il->last_temperature`, `S_TEMPERATURE`, and scheduled `txpower_work`;
- staging and active RXON state, association flags, station table restoration state, default WEP key restoration, channel-switch status, and `start_calib`;
- chain-noise calibration state and counters;
- scheduler byte-count table entries in `il->scd_bc_tbls.addr`;
- firmware state through commands `C_RXON`, `C_RXON_ASSOC`, `C_TX_PWR_TBL`, `C_CHANNEL_SWITCH`, `C_PHY_CALIBRATION`, `C_LEDS`, and station commands.

State is split between host memory, MMIO/peripheral registers, EEPROM, and firmware command state. Most RXON paths assert or assume `il->mutex`; NIC config uses `il->lock`; EEPROM arbitration uses hardware semaphore polling.

## Dependencies and Integration Points

Direct dependencies include:

- `common.h` iwlegacy core structures, command helpers, RXON helpers, station/key restore helpers, scan/channel-switch helpers, EEPROM query helpers, status bits, and debug macros;
- `4965.h` for hardware bounds, TX power constants, queue/register definitions, and sibling function prototypes;
- mac80211 for interface types, channel switch structures, HT configuration, beacon/timing data, and vif fields;
- Linux PCI/DMA/skbuff/netdevice/module infrastructure;
- firmware ABI command IDs and 4965-specific command layouts;
- sibling 4965 files that implement TX queues, RX, calibration, scanning, station management, beacon commands, debug, and mac80211 handlers referenced by `il4965_ops`.

The file ends with `MODULE_FIRMWARE(iwlwifi-4965-2.ucode)`, which ties kernel firmware loading to the supported API version.

## Risks and Edge Cases

- Firmware verification sparse-checks every 100 bytes before falling back to full bootstrap comparison. Sparse success is a pragmatic boot check, not a complete image proof.
- `il4965_fill_txpower_tbl()` calls `il4965_interpolate_chan()` but does not check its return value before using `ch_eeprom_info`; invalid sub-band lookup could leave calibration data undefined.
- Temperature calculation returns `-1` on calibration conflict. `il4965_temperature_calib()` filters out-of-range values, but initial `il4965_init_alive_start()` assigns the result directly to `il->temperature`.
- TX power send is rejected during hardware scan; callers must tolerate `-EAGAIN` and retry after scan.
- Full RXON transitions clear and restore firmware station/key state. Failures in restore paths leave association setup partially applied and require higher-level recovery.
- Channel-switch timing depends on TSF/beacon conversions and uses low 32 bits of the timestamp. Boundary conditions around wrap or very small switch counts should be tested.
- EEPROM semaphore acquisition returns the last poll result after retries; callers must observe negative returns and release only when acquired.

## Test Signals

- Build `CONFIG_IWL4965=m/y` with debug and debugfs variants.
- Firmware boot tests should trace BSM load, init ALIVE, runtime pointer setup, and runtime ALIVE with valid `iwlwifi-4965-2.ucode`.
- EEPROM tests should cover too-old EEPROM/calibration versions and semaphore timeout behavior.
- Association tests should observe RXON unassoc/assoc sequencing, station/key restoration, TX power command after retune, sensitivity initialization, and chain-noise calibration start.
- TX power tests should vary band, channel group, HT20/HT40, user power limit, temperature, and voltage/alive data, then inspect generated gain table bounds.
- Channel switch tests should verify switch timing, radar `expect_beacon`, destination TX power table generation, and abort of stale pending switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965.h

## Purpose

`4965.h` is the central 4965-specific interface and hardware definition header for the iwlegacy 4965 driver. It declares the 4965 configuration and operations objects, prototypes implemented across the 4965 source files, inline helpers, firmware memory bounds, TX power and temperature constants, queue counts, scheduler byte-count structures, and Flow Handler register offsets/bit masks for RX/TX DMA.

The header documents large parts of the 4965 hardware contract: firmware SRAM ranges, BSM size, EEPROM/TX-power calibration model, gain-table semantics, queue layout, receive-buffer handshakes, and FH register programming.

## Important APIs, Types, and Definitions

Extern objects:

- `il4965_cfg` describes the device to the common iwlegacy probe/setup code.
- `il4965_ops` supplies 4965-specific method implementations.
- `il4965_mod_params` carries module parameters declared elsewhere.

Function prototype groups:

- TX queues and aggregation: TFD attach/free, queue init, reclaim, context allocation/reset/stop, scheduler setup, write pointers, status changes, aggregation start/stop, and empty checks.
- RX and firmware: RX queue reset/init/restock/replenish/free/stop/handle, hardware NIC init, FH dump, uCode verify, NIC config.
- RXON, scan, association, AP/IBSS, station/key management, beacon command, and mac80211 callbacks.
- EEPROM: MAC read, semaphore acquire/release, version check.
- Calibration: chain-noise, sensitivity, runtime calibration reset, and temperature calibration.
- Debug: `il4965_debugfs_ops` when `CONFIG_IWLEGACY_DEBUGFS` is enabled.

Inline helpers:

- `il4965_hw_get_rate()` extracts the low-byte PLCP/MCS value from firmware `rate_n_flags`.
- `il4965_hw_valid_rtc_data_addr()` checks whether a runtime address falls within the 4965 data SRAM window.
- `il4965_get_tx_fail_reason()` returns debug text only when `CONFIG_IWLEGACY_DEBUG` is enabled.

Important constants and structures:

- Firmware memory bounds: `IL49_RTC_INST_*`, `IL49_RTC_DATA_*`, `IL49_MAX_INST_SIZE`, `IL49_MAX_DATA_SIZE`, and `IL49_MAX_BSM_SIZE`.
- Temperature formula constants and valid Kelvin range.
- TX power regulatory/saturation defaults, MIMO compensation, CCK compensation, voltage compensation scale, gain index bounds, and channel-group definitions.
- Queue constants: `IL49_NUM_FIFOS`, `IL49_CMD_FIFO_NUM`, `IL49_NUM_QUEUES`, `IL49_NUM_AMPDU_QUEUES`, `IL49_FIRST_AMPDU_QUEUE`, and `IL4965_FIRST_AMPDU_QUEUE`.
- `struct il4965_scd_bc_tbl`, the packed 1024-byte scheduler byte-count table per TX queue.
- Flow Handler register offsets for keep-warm memory, TFD circular-buffer base addresses, RX status/RBD/write-pointer/config/status registers, TX DMA channel config/credit/buffer status, TX shared status/error, service channels, and TX chicken bits.

## Control Flow and Integration

The common iwlegacy layer includes this header to call hardware-specific operations through `il4965_ops` and to compile 4965-specific modules against shared structures from `common.h`. The prototypes form the cross-file contract for:

1. PCI/mac80211 lifecycle in `4965-mac.c`.
2. Firmware and RXON setup in `4965.c`.
3. RX queue and notification handling in 4965 RX code.
4. TX queue, TFD, scheduler, and aggregation handling in 4965 TX code.
5. Sensitivity and chain-noise calibration in `4965-calib.c`.
6. Rate control in `4965-rs.c`.
7. Optional debugfs support in `4965-debug.c`.

The register definitions are consumed by low-level init, queue setup, RX replenishment, TX scheduler, FH dump, and stop paths. The comments specify ordering requirements such as writing RX buffers before updating the RBD write pointer, incrementing RX write indexes in multiples of eight, duplicating TX byte-count entries for the first 64 TFDs, and polling DMA idle bits after stopping channels.

## State and Persistence Behavior

The header itself stores no runtime state, but it defines state layouts and constants for persistent driver/hardware state:

- EEPROM image size and calibration data offsets used to validate and interpret device-specific nonvolatile data.
- Firmware instruction/data memory ranges and BSM memory limits used while loading and verifying uCode.
- Temperature and TX power constants that shape runtime power tables sent to firmware.
- Queue counts and byte-count table layout that must remain consistent with allocated DMA memory and scheduler programming.
- FH register addresses and masks that persist hardware queue/DMA state until rewritten or reset.

Callers must treat most functions declared here as stateful operations with hardware, firmware, DMA, or mac80211 side effects.

## Dependencies and Integration Points

`4965.h` depends on shared iwlegacy types from `common.h` being visible before or along with it in most translation units. It also references mac80211 types (`ieee80211_hw`, `ieee80211_vif`, `ieee80211_sta`, `ieee80211_tx_info`, key and AMPDU structures), DMA address types, sk_buffs, `nl80211_band`, debugfs structures, and firmware command structures declared in common headers.

The build system compiles this header into the `iwl4965` object set and sibling 3945 code does not use most 4965-specific definitions. `4965.c` consumes the TX power and memory constants; `4965-rs.c` consumes rate prototypes and common state; TX/RX/calibration files consume FH and queue constants.

## Risks and Edge Cases

- `IL49_FIRST_AMPDU_QUEUE` is defined as 7, while `IL4965_FIRST_AMPDU_QUEUE` is later defined as 10. This may reflect different historical meanings, but the duplicate naming is easy to misuse and should be checked before new queue code uses either constant.
- Many register macros are raw offsets and masks. Incorrect channel, queue, or pointer alignment values can program invalid DMA state without type safety.
- `struct il4965_scd_bc_tbl` assumes 1024-byte separation and packed layout. Any change to `TFD_QUEUE_BC_SIZE` or packing assumptions should verify the padding expression remains valid.
- TX power constants encode regulatory and RF assumptions. Changes can affect legal transmit power and distortion margins.
- The comments require RX write pointer increments in multiples of eight and a safety gap between read/write pointers; queue code must preserve these invariants under wrap and low-buffer conditions.
- `il4965_hw_valid_rtc_data_addr()` validates only data SRAM, not instruction SRAM or BSM ranges; callers need the correct address-space helper for the operation.

## Test Signals

- Compile all 4965 objects with `CONFIG_IWL4965`, `CONFIG_IWLEGACY_DEBUG`, and `CONFIG_IWLEGACY_DEBUGFS` combinations to catch prototype drift.
- Static analysis should verify declared functions match definitions across `4965*.c` and that queue constants match array allocations.
- Hardware smoke tests should exercise firmware load, RX queue init/replenish/stop, TX queue setup, AMPDU queue setup, and FH dump paths that use register definitions.
- TX power tests should compare generated tables against the documented formula and gain limits.
- DMA stop tests should verify RX/TX idle polling uses the documented status bits and handles timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Kconfig

## Purpose

`Kconfig` defines the build-time configuration surface for the legacy Intel wireless drivers in this directory. It introduces the shared hidden `IWLEGACY` symbol, user-visible device driver choices for Intel 4965AGN and 3945ABG/BG hardware, and optional debugging/debugfs features shared by both drivers.

## Important Symbols

- `IWLEGACY` is a tristate selected by concrete drivers. It selects firmware loading, LED triggers, and mac80211 LED integration.
- `IWL4965` is the user-visible tristate for Intel Wireless WiFi 4965AGN. It depends on `PCI`, `MAC80211`, and compatible `LEDS_CLASS` configuration, selects `IWLEGACY`, builds module `iwl4965`, and documents the required microcode.
- `IWL3945` is the corresponding user-visible tristate for Intel PRO/Wireless 3945ABG/BG and builds module `iwl3945`.
- `IWLEGACY_DEBUG` enables full debug tracing and the runtime `debug_level` sysfs control.
- `IWLEGACY_DEBUGFS` enables low-impact debugfs inspection and depends on both `IWLEGACY` and `MAC80211_DEBUGFS`.

## Control Flow and Build Integration

Kconfig selection starts from a user or distribution enabling `IWL4965` or `IWL3945`. Either driver selects `IWLEGACY`, which then pulls in shared firmware-loader and LED integration dependencies. The `Makefile` uses these symbols to build `iwlegacy.o`, `iwl4965.o`, optional debug objects, and `iwl3945.o`.

The debug options are placed in a menu gated by `IWLEGACY`, so they are visible only when at least one legacy driver is selected or otherwise enabled. The device options mention firmware installation because the runtime driver requires external uCode in `/lib/firmware`.

## State and Persistence Behavior

This file has no runtime state, but it determines which object files and code paths exist in the kernel build. Built-in versus module choice persists in the kernel configuration and changes driver load/unload behavior. Debug symbols increase module size and expose runtime diagnostics through sysfs/debugfs when combined with matching code.

## Dependencies and Integration Points

The symbols integrate with:

- Linux kbuild through `obj-$(CONFIG_...)` and conditional object lists in the directory `Makefile`;
- mac80211 through `MAC80211`, `MAC80211_LEDS`, and `MAC80211_DEBUGFS`;
- firmware loading through `FW_LOADER`;
- LED class/trigger support through `LEDS_CLASS` and `LEDS_TRIGGERS`;
- user-space firmware packaging for `iwlwifi-4965-2.ucode` and 3945 firmware.

## Risks and Edge Cases

- `IWL4965` and `IWL3945` require `LEDS_CLASS=y || LEDS_CLASS=MAC80211`. Configurations with LED support as an incompatible module state will make the driver unavailable.
- The help text points to an old `intellinuxwireless.org` URL, which may no longer be useful for users obtaining firmware.
- `IWLEGACY_DEBUG` help names a specific example interface path under `wlan0`; actual interface names can differ.
- Because `IWLEGACY` is selected rather than directly prompted, shared code must remain valid when either or both concrete drivers are enabled.

## Test Signals

- Kconfig dependency tests with `PCI`, `MAC80211`, `LEDS_CLASS`, `MAC80211_DEBUGFS`, and module/built-in combinations.
- Build matrix for `IWL4965=m/y`, `IWL3945=m/y`, both enabled, and debug/debugfs toggles.
- Runtime module-load tests should verify firmware-loader requests and LED/debugfs/sysfs surfaces match the selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Makefile

## Purpose

`Makefile` maps the iwlegacy Kconfig symbols to kernel objects. It builds the shared `iwlegacy.o` support object, the 4965 module object `iwl4965.o`, the 3945 module object `iwl3945.o`, and optional debugfs objects.

## Important Build Rules

- `obj-$(CONFIG_IWLEGACY) += iwlegacy.o` builds the shared support module/object from `common.o` plus optional shared debug support.
- `iwlegacy-objs := common.o` is the mandatory shared object list.
- `iwlegacy-$(CONFIG_IWLEGACY_DEBUGFS) += debug.o` adds shared debugfs support when enabled.
- `iwlegacy-objs += $(iwlegacy-m)` appends module-conditional pieces generated by kbuild for the selected optional shared objects.
- `obj-$(CONFIG_IWL4965) += iwl4965.o` builds the 4965 driver from `4965.o`, `4965-mac.o`, `4965-rs.o`, and `4965-calib.o`.
- `iwl4965-$(CONFIG_IWLEGACY_DEBUGFS) += 4965-debug.o` adds 4965-specific debugfs code.
- `obj-$(CONFIG_IWL3945) += iwl3945.o` builds the 3945 driver from `3945-mac.o`, `3945.o`, and `3945-rs.o`.
- `iwl3945-$(CONFIG_IWLEGACY_DEBUGFS) += 3945-debug.o` adds 3945-specific debugfs code.

## Control Flow and Integration

The file is evaluated by kernel kbuild after Kconfig resolves symbols. Enabling `IWL4965` causes kbuild to compile the shared `iwlegacy` object because the Kconfig entry selects `IWLEGACY`, then compile and link the 4965-specific objects into `iwl4965.o`. Debugfs selections append extra object files to both shared and device-specific modules.

This split lets 3945 and 4965 share common code while retaining separate module names and hardware-specific object lists. Rate-control code for 4965 is included through `4965-rs.o`, which registers the `iwl-4965-rs` rate-control operations at runtime.

## State and Persistence Behavior

The Makefile has no runtime state, but it controls which translation units are present in the built kernel or modules. A missing object in these lists means its symbols and init hooks will not exist; an extra optional object changes debugfs surface and module size.

## Dependencies and Integration Points

The rules depend on the Kconfig symbols in the same directory and on Linux kbuild's composite-object conventions. They integrate with source files in this folder:

- shared: `common.c` and optional `debug.c`;
- 4965: `4965.c`, `4965-mac.c`, `4965-rs.c`, `4965-calib.c`, and optional `4965-debug.c`;
- 3945: `3945-mac.c`, `3945.c`, `3945-rs.c`, and optional `3945-debug.c`.

## Risks and Edge Cases

- The `iwlegacy-objs += $(iwlegacy-m)` pattern is a kbuild idiom for optional module pieces; maintainers unfamiliar with it could accidentally duplicate or drop debug objects when editing.
- Adding a new 4965 source file requires updating `iwl4965-objs`; otherwise prototypes may compile only when included elsewhere or fail at link time.
- Debugfs code is gated by `CONFIG_IWLEGACY_DEBUGFS` for both shared and device-specific objects. Any unguarded references from mandatory objects to debug-only symbols would create link failures when debugfs is off.

## Test Signals

- Build with `CONFIG_IWL4965=m`, `CONFIG_IWL3945=m`, both enabled, and debugfs on/off.
- Use `make drivers/net/wireless/intel/iwlegacy/` or equivalent kernel build targets to catch missing object or unresolved symbol changes.
- Inspect linked module contents to confirm `iwl4965.o` includes `4965-rs.o` and optional `4965-debug.o` only under the debugfs config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Makefile -->
