# Research: subset-b-004819

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/dev.h

## Purpose

`dev.h` is the private state and implementation-contract header for the legacy Intel iwlwifi DVM op-mode. It defines the constants, calibration state, aggregation state, RXON context model, device-family configuration hooks, Bluetooth coexistence parameters, per-station/per-vif private data, power/thermal/debug state, and the central `struct iwl_priv` used by the DVM source files. It deliberately separates driver-internal definitions from firmware command ABI definitions in `commands.h`.

## Important APIs, Types, and Functions

Important declarations include CT-kill thresholds, RTS/MSDU/MPDU defaults, scan-rate constants, sensitivity/chain-noise calibration constants, `union iwl_ht_rate_supp`, `struct iwl_ht_config`, `struct iwl_qos_info`, `enum iwl_agg_state`, `struct iwl_ht_agg`, `struct iwl_tid_data`, `struct iwl_station_entry`, `struct iwl_station_priv`, `struct iwl_vif_priv`, `struct iwl_sensitivity_ranges`, `struct iwl_sensitivity_data`, `struct iwl_chain_noise_data`, `struct iwl_event_log`, `struct iwl_rf_reset`, `enum iwl_rxon_context_id`, `struct iwl_rxon_context`, `struct iwl_hw_params`, `struct iwl_dvm_bt_params`, `struct iwl_dvm_cfg`, `struct iwl_wipan_noa_data`, and the large `struct iwl_priv`.

The header also exposes conversion/access helpers: `IWL_OP_MODE_GET_DVM()`, `IWL_MAC80211_GET_DVM()`, `iwl_rxon_ctx_from_vif()`, `for_each_context()`, `iwl_is_associated_ctx()`, `iwl_is_associated()`, and `iwl_is_any_associated()`. `iwl_update_chain_flags()` and `iwl_bcast_addr` are forward declarations used across device-family code.

## Control Flow

The structures in this file define how the rest of the DVM driver sequences work. `struct iwl_priv` is allocated inside the mac80211 `hw->priv` area and then threaded through op-mode, mac80211, transport, firmware command, scan, station, power, BT coexistence, thermal throttling, WoWLAN, LED, debugfs, and recovery paths. RXON contexts represent BSS and PAN firmware contexts; `for_each_context()` lets lifecycle paths update every valid context without hard-coding PAN support.

Aggregation flow is modeled per station/TID through `struct iwl_tid_data` and `struct iwl_ht_agg`: start/operational/emptying/stop states coordinate TX reply, compressed BA, queue ID, sequence number, and mac80211 notification readiness. Calibration flow stores sensitivity and chain-noise accumulators in `iwl_priv`, while device-family callbacks in `struct iwl_dvm_cfg` provide runtime hooks for hardware parameter setup, channel switch command shape, NIC config, and temperature conversion.

## State and Persistence Behavior

`struct iwl_priv` contains nearly all persistent software state for a DVM device: status bits, mutex/spinlock-protected station tables, queue stop counters, queue-to-mac80211 mappings, active and staging RXON commands, scan request state, current temperature, firmware reload counters, statistics snapshots, BT coexistence state, calibration state, rate-control state, power manager, thermal throttle state, WEP/key state, WoWLAN key material, LED registration state, NVM/EEPROM data, delayed work/timers, and current firmware image type.

The state is not inherently synchronized by this header. Callers must follow the comments: station table access generally requires `sta_lock`, most firmware command/lifecycle changes require `priv->mutex`, and RCU protects `noa_data`.

## Dependencies and Integration Points

`dev.h` depends on Linux interrupt/wait/LED/slab/mutex APIs, mac80211-facing types through included iwlwifi headers, firmware image definitions, NVM utilities, CSR/register definitions, debugging, transport, notification waits, and local DVM headers `led.h`, `power.h`, `rs.h`, and `tt.h`. It is consumed by nearly every DVM translation unit.

## Risks and Edge Cases

The main risk is contract drift: many fields are updated by separate files with implicit locking and status-bit assumptions. RXON context `active` is `const` to force explicit casts at hardware-update sites, so accidental direct mutation is discouraged but still possible. Aggregation, station, and queue state can become inconsistent if firmware error/restart paths do not clear all tables in sync with mac80211 reconfiguration. The many feature-dependent fields under `CONFIG_IWLWIFI_DEBUGFS`, `CONFIG_IWLWIFI_LEDS`, and `CONFIG_PM_SLEEP` require compile coverage across configs.

## Test Signals

Useful signals are allmodconfig/build coverage, lockdep during start/stop/reset/scan/AMPDU paths, mac80211 station and vif lifecycle tests, suspend/resume with WoWLAN enabled and disabled, BT coexistence notification handling, and firmware restart recovery checks that verify station/key/aggregation/queue state is reset consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/devices.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/devices.c

## Purpose

`devices.c` provides DVM device-family specialization for Intel 1000/100/2000/105/2030/135/5000/5150/6000/6000i/6005/6050/6150/6030 families. It fills `struct iwl_dvm_cfg` instances with family-specific callbacks, sensitivity tables, thermal thresholds, BT coexistence defaults, NIC register configuration, and channel-switch command implementations.

## Important APIs, Types, and Functions

The exported objects are the `iwl_dvm_*_cfg` constants selected by `main.c` based on `trans->mac_cfg->device_family`. Local helpers include `iwl1000_set_ct_threshold()`, `iwl1000_nic_config()`, beacon-time helpers `iwl_usecs_to_beacons()` and `iwl_add_beacon_time()`, family-specific `*_hw_set_hw_params()` callbacks, `iwl2000_nic_config()`, `iwl_temp_calib_to_offset()`, `iwl5150_temperature()`, `iwl5000_hw_channel_switch()`, `iwl6000_nic_config()`, and `iwl6000_hw_channel_switch()`.

Static `struct iwl_sensitivity_ranges` tables define per-family OFDM/CCK energy/correlation thresholds. Static `struct iwl_dvm_bt_params` instances define advanced coexistence capabilities, priority boost, aggregation time limit, SCO handling, and command-session version.

## Control Flow

At op-mode start, `main.c` chooses one config object and later calls `priv->lib->set_hw_params()`, `priv->lib->nic_config()`, `priv->lib->temperature()`, and optionally `priv->lib->set_channel_switch()`. Hardware parameter callbacks set CT-kill thresholds and sensitivity table pointers. NIC callbacks set CSR/peripheral bits, such as SVR voltage for 1000, radio IQ inversion for 2000, calibration version and radio SKU bits for 6000-series variants.

Channel-switch callbacks build either `struct iwl5000_channel_switch_cmd` or dynamically allocated `struct iwl6000_channel_switch_cmd`, compute firmware switch time from mac80211 CSA count, TSF, current ucode beacon time, and beacon interval, set channel/RXON flags/radar expectations, and send `REPLY_CHANNEL_SWITCH`.

## State and Persistence Behavior

The file writes persistent fields in `priv->hw_params`, `priv->temperature`, and family config constants. NIC config writes hardware CSR/PRPH registers. Channel-switch updates are sent to firmware but rely on mac80211-side state prepared in `mac80211.c` (`ctx->staging`, `priv->switch_channel`, and `STATUS_CHANNEL_SWITCH_PENDING`).

## Dependencies and Integration Points

Dependencies include `iwl-io.h`, `iwl-prph.h`, `iwl-nvm-utils.h`, `agn.h`, `dev.h`, `commands.h`, Linux unit conversions, mac80211 channel-switch structures, and DVM command send helpers. Thermal callbacks integrate with `iwl_tt_handler()`, and channel switch integrates with `iwlagn_mac_channel_switch()` and firmware notifications.

## Risks and Edge Cases

Beacon-time arithmetic is sensitive to interval units and wrap behavior. The channel-switch code is explicitly marked `MULTI-FIXME`; it assumes the BSS context and is not fully correct for multiple active interfaces. `iwl5150_set_ct_threshold()` uses calibration values and a negative voltage-to-temperature coefficient, so bad NVM calibration can misprogram CT-kill. `iwl6000_nic_config()` warns on unknown device families, making selector correctness critical.

## Test Signals

Validation should cover boot/probe for every device family mapping, thermal threshold programming, 5150 temperature conversion with known calibration values, CSA on 5000 and 6000 command formats, radar-channel switch expectations, and register traces confirming family-specific NIC config bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/eeprom.c

## Purpose

`eeprom.c` reads DVM-era EEPROM/OTP NVM images from hardware and parses them into `struct iwl_nvm_data` for mac80211 registration and device initialization. It translates indirect EEPROM sections, validates signatures, reads OTP linked-list images when needed, builds regulatory channel maps, computes maximum TX power, extracts MAC/radio/SKU/calibration data, and initializes supported-band/rate/HT capability structures.

## Important APIs, Types, and Functions

Externally used functions are `iwl_read_eeprom()` and `iwl_parse_eeprom_data()`. Important local helpers include `iwl_eeprom_query16()`, `eeprom_indirect_address()`, `iwl_eeprom_query_addr()`, `iwl_eeprom_read_calib()`, `iwl_get_max_txpwr_half_dbm()`, `iwl_eeprom_enh_txp_read_element()`, `iwl_eeprom_enhanced_txpower()`, `iwl_init_band_reference()`, `iwl_mod_ht40_chan_info()`, `iwl_init_channel_map()`, EEPROM semaphore helpers, signature validation, OTP access helpers, `iwl_read_otp_word()`, `iwl_is_otp_empty()`, `iwl_find_otp_image()`, and `iwl_init_sbands()`.

The file defines EEPROM offsets, indirect-section link offsets, SKU/radio masks, regulatory channel flag structures, enhanced TX power entries, static EEPROM band channel lists, and static mac80211 rate tables.

## Control Flow

`iwl_read_eeprom()` determines whether the device uses OTP or EEPROM, allocates a raw image buffer sized from hardware config, validates the signature, acquires the EEPROM semaphore, and reads 16-bit words. OTP flow activates the NIC, configures OTP access, clears ECC status, optionally traverses the OTP linked list to locate the valid image, then reads each word with ECC checks. EEPROM flow polls `CSR_EEPROM_REG` for valid data for each address. All success paths release the semaphore and return the blob.

`iwl_parse_eeprom_data()` allocates flexible `iwl_nvm_data`, reads MAC address count, calibration header, crystal and temperature calibration values, radio config masks, SKU capabilities, NVM version, optional antenna overrides, validates nonzero antennas, then calls `iwl_init_sbands()`. Channel initialization loops through regulatory bands 1-5 to add valid 2.4/5 GHz channels and set `NO_IR`, `RADAR`, `NO_HT40`, and max power. Enhanced TX power entries may raise per-channel max power and set `max_tx_pwr_half_dbm`; otherwise channel limits are used. HT40 bands 6-7 clear HT40 plus/minus restrictions where EEPROM permits.

## State and Persistence Behavior

The raw EEPROM blob is owned by `priv->eeprom_blob`; parsed data is owned by `priv->nvm_data`. `iwl_nvm_data` persists MAC addresses, antenna masks, SKU flags, calibration versions/values, max power, channel array, supported bands, and HT capabilities. Hardware state touched during reads includes CSR EEPROM/OTP registers, EEPROM ownership semaphore bits, NIC activation state, OTP ECC acknowledgment bits, and shadow RAM power-management disables.

## Dependencies and Integration Points

The file depends on transport register access (`iwl_read32()`, `iwl_write32()`, `iwl_poll_bits()`), CSR/PRPH constants, `iwl_trans_activate_nic()`, NVM utility helpers `iwl_init_sband_channels()` and `iwl_init_ht_hw_capab()`, mac80211 channel/rate structures, module parameters such as `disable_11n`, and per-device `cfg->eeprom_params`.

## Risks and Edge Cases

Most accessors use `WARN_ON()` for bounds and return zero/NULL, so malformed NVM can degrade into parse failure or wrong defaults. `iwl_eeprom_enhanced_txpower()` assumes the TX power length pointer is valid before dereferencing. OTP reads must handle correctable and uncorrectable ECC differently; uncorrectable ECC aborts, correctable ECC logs and continues. OTP linked-list traversal depends on `max_ll_items` and skips the link pointer by adding two bytes. Regulatory correctness depends on EEPROM flags and enhanced TX power data being interpreted precisely.

## Test Signals

Test with EEPROM and OTP devices, shadow-RAM and non-shadow-RAM OTP, bad signature cases, semaphore timeout injection, OTP ECC injection, truncated/malformed blobs, antenna override configs, 2.4/5 GHz channel count validation, HT40 enablement checks, enhanced TX power parsing, and NVM version rejection in `main.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.c

## Purpose

`led.c` implements optional Linux LED-class integration for DVM devices. It registers a per-wiphy LED, supports radio-state or throughput-triggered modes, translates brightness/blink requests into firmware `REPLY_LEDS_CMD` commands, and compensates blink timings for MAC clock deviations.

## Important APIs, Types, and Functions

Exported functions are `iwlagn_led_enable()`, `iwl_leds_init()`, and `iwl_leds_exit()`. Local helpers include `iwl_blink_compensation()`, `iwl_send_led_cmd()`, `iwl_led_cmd()`, `iwl_led_brightness_set()`, and `iwl_led_blink_set()`. The static `iwl_blink[]` table maps throughput thresholds to blink periods for `ieee80211_create_tpt_led_trigger()`.

## Control Flow

`iwl_leds_init()` checks module LED mode, resolves default mode from device config, allocates a LED name based on the wiphy, installs brightness and blink callbacks, chooses a throughput or RF-state default trigger, registers the LED class device, and marks `priv->led_registered`. Brightness and blink callbacks call `iwl_led_cmd()`, which rejects requests when the device is not ready, avoids duplicate commands, maps `off == 0` to solid-on firmware semantics, applies hardware compensation to on/off values, sends an async LED host command, and caches the current blink values on success.

`iwlagn_led_enable()` directly turns on LED register control during device start. `iwl_leds_exit()` unregisters the LED and frees the allocated name only if registration succeeded.

## State and Persistence Behavior

Persistent software state includes `priv->led`, `priv->blink_on`, `priv->blink_off`, and `priv->led_registered`. Hardware state includes `CSR_LED_REG` and firmware LED command state. `iwl_send_led_cmd()` masks `CSR_LED_REG` down to BSM control bits before sending the command.

## Dependencies and Integration Points

The file depends on Linux LED class APIs, mac80211 LED triggers, iwlwifi module parameters, transport register access, firmware command wrappers, and `CONFIG_IWLWIFI_LEDS`. `mac80211.c` initializes and exits LED support during hardware registration/unregistration and enables the LED on mac80211 start.

## Risks and Edge Cases

LED commands are asynchronous and only gated by `STATUS_READY`; callers must tolerate failures during reset/rfkill. A zero compensation value logs an error and uses raw timing. Duplicate blink suppression relies on cached uncompensated values. Name allocation or LED registration failure leaves LED support disabled without failing device registration.

## Test Signals

Build with LEDs enabled and disabled, exercise `led_mode` values disable/default/blink/RF-state, verify registration cleanup on failure injection, confirm throughput trigger changes firmware blink commands, test brightness on/off during running device, and ensure no command is sent before `STATUS_READY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.h

## Purpose

`led.h` is the small public DVM LED interface. It defines firmware LED constants and declares LED lifecycle helpers, while compiling them to no-op inline functions when `CONFIG_IWLWIFI_LEDS` is disabled.

## Important APIs, Types, and Functions

The header forward-declares `struct iwl_priv`, defines `IWL_LED_SOLID`, `IWL_DEF_LED_INTRVL`, `IWL_LED_ACTIVITY`, and `IWL_LED_LINK`, and declares `iwlagn_led_enable()`, `iwl_leds_init()`, and `iwl_leds_exit()` for LED-enabled builds.

## Control Flow

Callers can unconditionally call LED helpers. With LED support enabled, calls are implemented by `led.c`; otherwise they compile away. This keeps `mac80211.c` and `dev.h` independent of `#ifdef` blocks around each callsite.

## State and Persistence Behavior

The header has no storage. Its enabled implementation mutates LED class-device state in `struct iwl_priv`, cached blink values, `CSR_LED_REG`, and firmware LED state. Disabled builds perform no state changes.

## Dependencies and Integration Points

The header is included by `dev.h` and therefore becomes part of the broader DVM private header set. Its constants must match `struct iwl_led_cmd` semantics in `commands.h` and the LED firmware command implemented in `led.c`.

## Risks and Edge Cases

The main risk is interface drift between `led.h` prototypes and `led.c`, or accidental reliance on side effects in callers when LED support may be compiled out. Constants are untyped macros and must remain compatible with little-endian command fields.

## Test Signals

Compile with `CONFIG_IWLWIFI_LEDS=y` and `n`, check for unused/static inline warnings, and exercise mac80211 register/start/unregister paths in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/lib.c

## Purpose

`lib.c` contains DVM shared runtime helpers for firmware command safety, TX power, temperature, hardware-rate conversion, IBSS station management, TX FIFO flush, advanced Bluetooth coexistence, RX-chain selection, TX antenna cycling, and WoWLAN programming. It is a support layer used by mac80211 callbacks, main lifecycle code, scan/rate/station code, and power/thermal handlers.

## Important APIs, Types, and Functions

Exports include `iwlagn_hw_valid_rtc_data_addr()`, `iwlagn_send_tx_power()`, `iwlagn_temperature()`, `iwlagn_hwrate_to_mac80211_idx()`, `iwlagn_manage_ibss_station()`, `iwlagn_txfifo_flush()`, `iwlagn_dev_txfifo_flush()`, `iwlagn_send_advance_bt_config()`, `iwlagn_bt_adjust_rssi_monitor()`, `iwlagn_bt_coex_rssi_monitor()`, `iwlagn_bt_rx_handler_setup()`, `iwlagn_bt_setup_deferred_work()`, `iwlagn_bt_cancel_deferred_work()`, `iwlagn_set_rxon_chain()`, `iwl_toggle_tx_ant()`, `iwlagn_send_patterns()`, `iwlagn_suspend()`, `iwl_dvm_send_cmd()`, and `iwl_dvm_send_cmd_pdu()`.

Key local helpers cover BT traffic/SCO classification, BT notification parsing, kill-mask and reduced-TX-power decisions, RX-chain count calculation, TKIP P1K conversion, and WoWLAN key iteration.

## Control Flow

Command paths should use `iwl_dvm_send_cmd()` or `_pdu()`, which reject RF-kill/CT-kill, firmware-error, and unloaded-firmware states; synchronous commands assert `priv->mutex`. TX power checks scanning state, clamps requested half-dBm power to NVM regulatory max, selects command version by firmware API, and sends the power command. TX FIFO flush builds v2/v3 command payloads depending on firmware API and queue masks, optionally stops/wakes mac80211 queues around device-wide flush.

BT coexistence starts with initial config in `main.c`, then runtime notifications are dispatched to `iwlagn_bt_coex_profile_notif()`. That updates traffic load/status/SCO state, queues work for chain/SMPS/RSSI monitor changes, and queues runtime config if reduced TX power or ACK/CTS kill masks changed. `iwlagn_set_rxon_chain()` then computes active/idle RX chains from valid antennas, chain-noise calibration, SMPS, power state, and BT traffic.

WoWLAN suspend flow cancels scans, restarts hardware with WoWLAN firmware, commits saved RXON, sets power mode, reprograms keys and replay counters, sends D3 config, wake filters, and packet patterns.

## State and Persistence Behavior

This file updates `priv->temperature`, `tx_power_user_lmt`-derived firmware state, IBSS station IDs, BT flags/masks/traffic load/RSSI monitor context/reduced-power state, `current_ht_config.smps`, RXON staging `rx_chain`, WoWLAN flags/key material command payloads, firmware loaded state during suspend, and command gating around `priv->status`. It also touches mac80211 queues and RSSI reporting state.

## Dependencies and Integration Points

Dependencies include mac80211 station/key/WoWLAN APIs, iwl transport command send/free operations, firmware command IDs and structures, module parameters, station/key helpers, scan cancellation, RXON commit, power update, thermal handler, rate tables, and BT/coex constants.

## Risks and Edge Cases

BT coexistence has many asynchronous updates and relies on ordered work plus `priv->mutex`; stale notifications during scans are deferred. `iwlagn_fill_txpower_mode()` only examines the BSS context, which can be wrong for multi-context scenarios. `iwl_toggle_tx_ant()` returns antenna index 0 under high 2.4 GHz BT load regardless of valid mask assumptions. WoWLAN key programming temporarily drops `priv->mutex` for mac80211 key iteration; this is considered acceptable in suspend but remains a lock-ordering-sensitive path. Command wrappers return `-EIO` for many states, so callers must handle reset/rfkill cleanly.

## Test Signals

Exercise firmware command rejection under RF-kill/CT-kill/FW error/unloaded firmware, TX power clamp tests against enhanced EEPROM limits, FIFO flush with API v2/v3, BT profile notifications with SCO/A2DP/ACL/load transitions, RX-chain updates under SMPS and BT traffic, WoWLAN suspend with CCMP/TKIP/WEP and patterns, and lockdep around suspend key iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/mac80211.c

## Purpose

`mac80211.c` is the DVM op-mode's mac80211 integration surface. It allocates/registers `ieee80211_hw`, advertises hardware capabilities, implements `struct ieee80211_ops`, translates mac80211 lifecycle/interface/station/key/scan/AMPDU/channel-switch/suspend events into DVM firmware operations, and coordinates restart/reconfiguration with `main.c`.

## Important APIs, Types, and Functions

Public functions include `iwlagn_mac_setup_register()`, `iwlagn_mac_unregister()`, `iwl_chswitch_done()`, `iwl_alloc_all()`, and the exported `iwlagn_hw_ops`. Important callbacks include start/stop, WoWLAN suspend/resume/set_wakeup, TX, TKIP update, key set/remove, AMPDU action, station add/remove/state/notify, channel switch, filter configuration, flush, set TIM, TX queue config, TX last beacon, add/remove/change interface, hardware scan, event callback, and reconfig complete.

## Control Flow

Registration configures mac80211 flags, queue counts, station/vif private sizes, supported interface modes/combinations, regulatory flags, WoWLAN support, scan limits, bands from NVM, LEDs, and extended features before calling `ieee80211_register_hw()`.

Start flow locks `priv->mutex`, calls `__iwl_up()`, allocates broadcast stations, starts hardware, runs init ucode, restarts hardware, loads runtime ucode, runs `iwl_alive_start()`, then enables LED and marks open. Stop flow calls `iwl_down()`, cancels deferred work, and flushes the workqueue. Interface add selects a valid RXON context, handles monitor FCS behavior, assigns vif private context, and commits RXON. Interface remove/change tears down or reconfigures the same context under mutex.

Station state callbacks map mac80211 transitions to station add/remove and rate initialization. Key callbacks choose default WEP versus dynamic keys and can mark unsupported RX keys TX-only. AMPDU callbacks start/stop RX/TX aggregation and maintain RTS-for-aggregation state. Channel switch prepares staging RXON, sets pending status, and delegates command formatting to the device-family hook. Scan callbacks track `scan_request`/`scan_vif` and either defer during internal scans or start hardware scan.

WoWLAN suspend delegates to `iwlagn_suspend()` for firmware reconfiguration and D3 handoff. Resume reads WoWLAN status, reports wake reason, prepares restart, resets RXON config, and forces mac80211 disconnect/reconfiguration.

## State and Persistence Behavior

The file mutates mac80211 hardware registration state, LED registration, `priv->is_open`, `mac80211_registered`, RXON context `vif` and `is_active`, vif queue maps, `iw_mode`, key tables, station private data, aggregation counters, scan tracking fields, channel-switch status and target channel, WoWLAN replay/key material, BT RSSI PS-poll flag, QoS parameters, AP beacon update work, and transport software reset completion state.

## Dependencies and Integration Points

It depends on mac80211/cfg80211 APIs, DVM station/key/RXON/scan/TX/rate helpers declared in `agn.h`, LED and power helpers, firmware loading via `main.c`, transport D3 operations, notification waits, and NVM-derived bands/capabilities. It is called by mac80211 after `iwl_op_mode_dvm_start()` registers the hardware.

## Risks and Edge Cases

Multiple comments flag incomplete multi-interface handling, especially channel switch affecting only BSS context. Many callbacks mask errors during RF-kill to avoid mac80211 warnings. Interface type change masks firmware commit errors to avoid mac80211/driver state divergence. Resume intentionally sends an extra echo due to firmware leaving an RBD open, then restarts normal firmware. Key handling may return success with `WEP_INVALID_OFFSET` when hardware RX programming is unavailable. Scan and power operations require careful ordering with `priv->mutex`.

## Test Signals

Run mac80211/cfg80211 lifecycle tests: register/unregister, open/close, add/remove/change station/AP/monitor/P2P interfaces, association and station state transitions, hardware crypto set/remove, AMPDU start/stop, CSA success/failure, scan during internal scan, queue flush with drop/no-drop, WoWLAN suspend/resume wake reasons, RF-kill during callbacks, and restart/reconfig completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/main.c

## Purpose

`main.c` is the DVM op-mode module and lifecycle core. It registers the `iwldvm` op-mode and rate control, starts/stops device instances, selects device-family configuration, reads and parses NVM, initializes driver state and contexts, manages firmware alive/down/restart flows, schedules deferred work/timers, handles firmware errors and event logs, configures NIC registers, and implements transport-facing op-mode callbacks.

## Important APIs, Types, and Functions

Key exported or callback functions include `iwl_update_chain_flags()`, `iwlagn_send_beacon_cmd()`, `iwl_send_statistics_request()`, `iwl_alive_start()`, `iwl_down()`, `iwlagn_prepare_restart()`, `iwl_cancel_deferred_work()`, `iwl_dump_nic_event_log()`, `iwlagn_lift_passive_no_rx()`, `iwl_op_mode_dvm_start()`, `iwl_op_mode_dvm_stop()`, transport callbacks in `iwl_dvm_ops`, and module `iwl_init()`/`iwl_exit()`.

Important local helpers handle beacon TIM parsing/update, BT runtime/full-concurrency work, periodic statistics, continuous event tracing, TX flush work, RXON context initialization, CT-kill config, runtime calibration config, TX antenna config, legacy BT config, station clearing, runtime calibration work, driver init/uninit, hardware/NVM parameter checks, firmware error dumps, software reset, NIC config, queue stop/wake, SKB free, and RF-kill state propagation.

## Control Flow

Module init registers rate control then the `iwldvm` op-mode. `iwl_op_mode_dvm_start()` allocates mac80211 hardware/private op-mode state, selects `priv->lib`, configures transport command groups/queues/no-reclaim commands/RX buffer size, enters op-mode, starts hardware long enough to read EEPROM/OTP, stops hardware, parses NVM, checks versions and SKU, derives MAC addresses and chain counts, initializes queues/driver state/work/timers/RX handlers/power/thermal/context metadata, registers with mac80211, and registers debugfs. Cleanup unwinds in reverse.

Runtime bring-up occurs after mac80211 start via `iwl_alive_start()`: mark alive, optionally start ucode tracing, configure BT coexistence and priority tables, request runtime calibration, wake queues, send TX antenna config, initialize or preserve RXON association state, reset runtime calibration, mark ready, commit RXON, configure CT-kill, and update power mode. Down/restart paths cancel scan, set exit-pending, clear firmware and driver station/key state, reset BT state, stop queues, stop transport, preserve selected status bits, clear beacon SKB, and prepare mac80211 restart.

Firmware error handling records FW error status, aborts notification waits, dumps error/event logs unless command-queue-full CT-kill applies, rate-limits continuous reloads, and queues restart work if enabled.

## State and Persistence Behavior

This file owns op-mode registration, `priv->status` transitions (`ALIVE`, `READY`, `EXIT_PENDING`, `FW_ERROR`, RF-kill), `ucode_loaded`, current ucode type, event-log cursor counters, firmware reload counters, workqueue/timers, queue stop counts and `transport_queue_stop`, RXON context command IDs/modes/queues, beacon command/SKB state, NVM-derived addresses, BT defaults, calibration command IDs, power/thermal init state, station/key clearing, debugfs registration, and transport configuration fields.

Hardware/firmware state touched includes NIC start/stop, EEPROM reads, CSR/PRPH NIC config, BT/CT-kill/calibration/TX antenna/statistics/beacon commands, SRAM event/error log reads, and mac80211 queue stop/wake.

## Dependencies and Integration Points

`main.c` integrates transport op-mode APIs, firmware image/capability data, NVM parsing from `eeprom.c`, device-family configs from `devices.c`, mac80211 registration from `mac80211.c`, scan/RX/TX/station/rate/calibration/thermal/debugfs helpers, Linux module infrastructure, and trace/debug logging.

## Risks and Edge Cases

Probe has many partial-initialization labels; incorrect unwind ordering can leak workqueues, NVM blobs, or registered mac80211 state. Restart intentionally preserves some BT state while clearing most device state. Status-bit masking in `iwl_down()` is compact and easy to misread. Continuous event tracing handles firmware write-pointer/wrap races; any simplification may drop or over-read logs. Queue stop/wake uses refcounts per mac80211 queue and must remain balanced. Firmware reload rate limiting stops repeated restarts after too many fast failures.

## Test Signals

Test module load/unload, op-mode start failure injection at each probe stage, NVM version/SKU rejection, mac80211 registration failure unwind, normal start/stop, firmware alive sequence, CT-kill config variants, firmware error/restart rate limiting, event/error log dumping with bogus pointers and wrap cases, queue full/not-full balancing, passive no-rx lifting, RF-kill state propagation, and transport op-mode enter/leave ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.c

## Purpose

`power.c` builds and sends DVM firmware power-table commands. It maps mac80211 power-save/idle/DTIM state, module parameters, WoWLAN, thermal throttling, advanced power-management support, BT coexistence, shadow-register support, and PCI bus power management into `struct iwl_powertable_cmd` values.

## Important APIs, Types, and Functions

Exported functions are `iwl_power_set_mode()`, `iwl_power_update_mode()`, and `iwl_power_initialize()`. Local helpers include `iwl_static_sleep_cmd()`, `iwl_power_sleep_cam_cmd()`, `iwl_set_power()`, and `iwl_power_build_cmd()`. The file defines `force_cam` module parameter, legacy and advanced power vector tables for DTIM ranges 0-2, 3-10, and greater than 10, plus `struct iwl_power_vec_entry`.

## Control Flow

`iwl_power_update_mode()` builds a command and delegates to `iwl_power_set_mode()`. Command construction first honors `force_cam`, then chooses DTIM period, WoWLAN maximum sleep level, idle maximum sleep when supported, thermal-throttle power mode, CAM when mac80211 PS is disabled, debug override, module `power_level`, or default level 1. `iwl_static_sleep_cmd()` selects legacy or advanced tables based on `priv->lib->adv_pm`, chooses DTIM range, adjusts sleep intervals for skip-DTIM/listen interval constraints, sets sleep-over-DTIM, shadow register, BT SCO, PCI PM flags, clamps to `IWL_CONN_MAX_LISTEN_INTERVAL`, and enforces monotonic/max interval limits.

`iwl_power_set_mode()` requires `priv->mutex`, skips unchanged commands unless forced, rejects RF-not-ready, caches `sleep_cmd_next`, defers non-forced updates while scanning, enables PMI before allowing sleep, sends `POWER_TABLE_CMD`, disables PMI for CAM on success, updates RX chain flags when chain-noise calibration permits, and commits `sleep_cmd`.

## State and Persistence Behavior

Persistent state includes `priv->power_data.sleep_cmd`, `sleep_cmd_next`, `debug_sleep_level_override`, and `bus_pm`. The file toggles `STATUS_POWER_PMI` indirectly through `iwl_dvm_set_pmi()`, may update RXON chain state through `iwl_update_chain_flags()`, and programs firmware power-table state. It reads mac80211 config flags, DTIM period, WoWLAN state, thermal state, BT params, transport PM support, and module parameters.

## Dependencies and Integration Points

Dependencies include mac80211 config, DVM command wrappers, transport PM capability, thermal throttle helpers, BT coexistence helpers, RX-chain update logic, firmware power command definitions, and module parameters. `main.c` initializes power state and calls power update after firmware alive; `lib.c` calls it during WoWLAN setup.

## Risks and Edge Cases

`force_cam` defaults true, so normal runtime power saving is disabled unless the module parameter changes. Scan deferral means `sleep_cmd_next` can differ from firmware state until scan completion. Chain updates are skipped during chain-noise calibration. DTIM zero is normalized specially. Advanced and legacy table layouts differ; incorrect `adv_pm` config can send incompatible flags. All synchronous paths require `priv->mutex`.

## Test Signals

Exercise CAM default, explicit power levels 1-5, debug override, WoWLAN mode, idle mode, thermal throttling modes, DTIM 0/1/2/3/10/11, scan deferral and later apply, PCI PM flag, shadow register flag, BT SCO flag, RF-not-ready rejection, and RX chain update behavior around calibration states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.h

## Purpose

`power.h` declares the DVM power-management state container and public power-mode functions. It is the interface between the broad driver state in `dev.h`, firmware power commands in `commands.h`, and the implementation in `power.c`.

## Important APIs, Types, and Functions

`struct iwl_power_mgr` stores the currently applied sleep command, the next sleep command deferred during scanning, a debug sleep-level override, and whether bus power management is supported/enabled. The declared functions are `iwl_power_set_mode()`, `iwl_power_update_mode()`, and `iwl_power_initialize()`.

## Control Flow

Callers initialize `priv->power_data` once during op-mode start, then call `iwl_power_update_mode()` when firmware becomes alive or when mac80211/power/thermal state changes. Lower-level callers that already prepared a command can call `iwl_power_set_mode()` directly, normally while holding `priv->mutex`.

## State and Persistence Behavior

The header has no storage of its own, but `struct iwl_power_mgr` persists in `struct iwl_priv`. Its fields represent both software cache and pending firmware state, so callers must treat them as part of the device lifecycle and reset/reinitialize them on full teardown.

## Dependencies and Integration Points

The header includes `commands.h` for `struct iwl_powertable_cmd` and is included by `dev.h`. It integrates with `power.c`, `main.c`, `lib.c` WoWLAN flow, thermal throttling, mac80211 configuration, and firmware command dispatch.

## Risks and Edge Cases

The API contract is mostly implicit: `iwl_power_set_mode()` requires the driver mutex and may defer during scans. New callers must not assume an immediate firmware update just because the cached next command changed. The debug override is an integer and should stay in the valid power-index range or be reset to `-1`.

## Test Signals

Compile all users for prototype drift, run lockdep around direct `iwl_power_set_mode()` callers, and validate that initialization sets `debug_sleep_level_override = -1`, detects bus PM support, and clears cached sleep command state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.h -->
