# subset-b-004882 Research

This grouped report covers the RTL8188EE rtlwifi driver files listed for subset B. Each section is source-tree aligned and bounded by the exact reconciliation markers used to split the report into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.c

## Purpose

`dm.c` implements RTL8188EE dynamic-management logic that runs after hardware initialization and periodically from the driver watchdog. It adjusts receiver gain, CCK packet detection thresholds, EDCA parameters, transmit power tracking, rate-adaptive masks, and antenna diversity based on RSSI, false-alarm counters, thermal readings, link state, Bluetooth coexistence state, and power-save state. It is the main feedback-loop file for keeping the 8188EE PHY/MAC usable across changing RF conditions.

## Important APIs, Types, And Functions

The public entry points exported through `dm.h` are `rtl88e_dm_init()`, `rtl88e_dm_watchdog()`, `rtl88e_dm_write_dig()`, `rtl88e_dm_init_edca_turbo()`, `rtl88e_dm_check_txpower_tracking()`, `rtl88e_dm_init_rate_adaptive_mask()`, `rtl88e_dm_txpower_track_adjust()`, `rtl88e_dm_set_tx_ant_by_tx_info()`, `rtl88e_dm_ant_sel_statistics()`, and `rtl88e_dm_fast_antenna_training_callback()`. Initialization seeds driver-controlled DM mode, DIG state, EDCA state, rate-mask state, TX-power tracking, baseband power-saving state, and antenna-diversity registers.

Key private helpers include `rtl88e_dm_false_alarm_counter_statistics()` for reading and resetting OFDM/CCK false-alarm counters; `rtl88e_dm_dig()` for dynamic initial gain; `rtl88e_dm_cck_packet_detection_thresh()` for CCK CCA threshold selection; `rtl92c_dm_dynamic_txpower()` for near-field TX-power reductions; `dm_txpower_track_cb_therm()` for thermal swing/TXAGC adjustment and LCK/IQK scheduling; `rtl88e_dm_refresh_rate_adaptive_mask()` for RSSI-tiered station rate updates; and `rtl88e_dm_antenna_diversity()` plus its hardware/fast-training helpers for selecting RX idle and TX antennas.

The static `ofdmswing_table`, `cck_tbl_ch1_13`, and `cck_tbl_ch14` are calibration lookup tables used by TX-power tracking. The implementation uses shared `struct rtl_dm`, `struct dig_t`, `struct false_alarm_statistics`, `struct rate_adaptive`, `struct fast_ant_training`, and `struct rtl_ps_ctl` state defined outside this file.

## Control Flow

`rtl88e_dm_init()` is called from `rtl88ee_hw_init()` after MAC/BB/RF setup, IQK/LCK, and firmware download. It reads the current OFDM initial-gain register and initializes all dynamic-management submodules. After that, `rtl88e_dm_watchdog()` is the normal control loop. The watchdog first queries `HW_VAR_FW_PSMODE_STATUS` and `HW_VAR_FWLPS_RF_ON`, forces `fw_ps_awake` false during P2P power-save mode, takes `rf_ps_lock`, and only runs dynamic updates when RF is on, firmware is not in power-save mode, firmware RF is awake, and no RF change is in progress.

Within a watchdog pass, the order is meaningful: `rtl88e_dm_pwdb_monitor()` updates RSSI/PWDB aggregate state, `rtl88e_dm_dig()` adjusts initial gain using the prior false-alarm counters, `rtl88e_dm_false_alarm_counter_statistics()` samples counters for the next pass, dynamic TX power and thermal tracking run, the rate mask is refreshed if RSSI tier changed, EDCA turbo may alter BE parameters, and antenna diversity may update RX/TX antenna selection. Because false-alarm sampling follows DIG, DIG decisions are one watchdog interval behind the latest hardware counters.

Thermal tracking is a two-phase loop through `rtl88e_dm_check_txpower_tracking()`: the first call triggers the RF thermal meter, the next call reads it and invokes `dm_txpower_track_cb_therm()`. That callback averages thermal readings, compares them with EEPROM and previous LCK/IQK baselines, invokes `rtl88e_phy_lc_calibrate()` or `rtl88e_phy_iq_calibrate()` when deltas exceed thresholds, and adjusts TX power through `rtl88e_phy_set_txpower_level()` when swing indices change.

## State And Persistence Behavior

Most state is volatile driver runtime state in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, `rtlpriv->falsealm_cnt`, and `rtlpriv->dm.fat_table`. Persistent calibration baselines originate from EEPROM/EFUSE fields exposed in `rtl_efuse`, especially thermal meter, antenna-diversity type, OEM ID, and TX-power tables loaded by `hw.c`. The file writes hardware registers directly and therefore has side effects in MAC, BB, and RF blocks: IGI register `ROFDM0_XAAGCCORE1`, CCK CCA registers, EDCA BE parameter, RF thermal trigger, TXAGC/swing-dependent RF power programming, antenna mapping/selection registers, and firmware RSSI monitor register `0x4fe`.

Some local static counters in `rtl88e_dm_pwdb_monitor()` and `rtl88e_dm_check_edca_turbo()` persist across calls to compute deltas in unicast bytes and Bluetooth EDCA values. These are file-local process lifetime variables and are not per-device, which is a subtle multi-adapter risk.

## Dependencies And Integration Points

`dm.c` depends on `wifi.h`, `base.h`, `pci.h`, `core.h`, device register definitions, PHY helpers from `phy.c`, firmware command support from `fw.c`, and TX descriptor helpers from `trx.h`. It calls `rtl_get_bbreg()`, `rtl_set_bbreg()`, `rtl_get_rfreg()`, `rtl_set_rfreg()`, raw MMIO helpers, `rtl_find_sta()`, driver ops such as `update_rate_tbl()`, and calibration functions exported by `phy.c`. It integrates with mac80211 station state through `rtl_find_sta()` and `rtl_sta_info`, with AP/adhoc peers through `entry_list`, with Bluetooth coexistence fields through `rtlpriv->btcoexist`, and with firmware LPS state through `get_hw_reg()`.

## Risks And Edge Cases

The watchdog is register-heavy and assumes RF/MAC blocks are accessible after the power-state checks; missed or stale power-save state can cause invalid MMIO/RF accesses. Several heuristics depend on magic thresholds for false alarms, RSSI, and thermal deltas; regressions can appear as throughput collapse, high packet loss, or unstable TX power rather than simple failures. Antenna diversity indexes arrays by `mac_id` and walks `entry_list`; incorrect station counts or IDs can corrupt per-station antenna statistics. The static byte counters in `rtl88e_dm_pwdb_monitor()` and EDCA static state are shared across adapters. `rtl88e_dm_txpower_track_adjust()` has an unsigned subtraction path in the OFDM branch when `ofdm_val > ofdm_base`, which deserves care if reused.

## Test Signals

Useful signals include watchdog execution under linked and unlinked states, false-alarm counter resets, IGI changes, CCK CCA threshold changes, thermal tracking toggling trigger/read phases, LCK/IQK invocation after forced thermal deltas, EDCA BE register changes for RX-heavy/TX-heavy traffic, rate-mask H2C updates after RSSI tier changes, and antenna selection changes with controlled per-antenna RSSI. Hardware or emulation tests should include RF off, firmware LPS, P2P power-save, scanning, AP/adhoc station lists, HP OEM path, Bluetooth coexistence EDCA overrides, and channel 14 CCK swing selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.h

## Purpose

`dm.h` is the RTL8188EE dynamic-management contract. It defines antenna identifiers, DM-specific RF/BB/MAC register aliases, threshold constants, rate-adaptive and antenna-diversity enums, the software antenna-try state structure, and the functions exported by `dm.c`.

## Important APIs, Types, And Constants

The register macros map dynamic-management names to hardware offsets used by DIG, antenna diversity, false-alarm accounting, EDCA tuning, TX-power tracking, and IQK matrix updates. Thresholds such as `DM_DIG_FA_TH0/1/2`, `DM_DIG_FA_UPPER/LOWER`, `TX_POWER_NEAR_FIELD_THRESH_LVL1/2`, and `TXPWRTRACK_MAX_IDX` encode the main DM heuristics. `enum pwr_track_control_method` selects between baseband swing and TXAGC power tracking. `enum _ANT_DIV_TYPE` is in `phy.h`, while `dm.h` defines the concrete main/aux mapping values consumed by `dm.c`.

The exported functions connect `dm.c` to hardware initialization, periodic watchdog work, TX descriptor construction, RX statistics collection, thermal tracking, EDCA setup, and rate-adaptive-mask initialization.

## Control Flow And Integration

The header itself contains no executable control flow. Its declarations are consumed by `hw.c` during initialization and network-state changes, by TX/RX paths through antenna-selection helpers, and by timer setup through `rtl88e_dm_fast_antenna_training_callback()`. The constants are also tightly coupled to `reg.h` because many values are raw hardware offsets.

## State And Persistence Behavior

`struct swat_t` carries software antenna-try counters and RSSI history, but most active DM state lives in shared driver structures declared elsewhere. The header’s state impact is mostly ABI-like: changing constants or enum values directly changes how `dm.c` writes registers and interprets antenna modes.

## Dependencies, Risks, And Test Signals

`dm.h` assumes Linux kernel integer types, `struct ieee80211_hw`, `struct timer_list`, and rtlwifi shared enums such as `enum rtl_led_pin` are already visible through including translation units. Risks are primarily semantic: duplicated or stale register aliases can cause silent hardware misconfiguration. Tests should compile all RTL8188EE objects, verify that public prototypes match `dm.c`, and exercise each antenna-diversity mode and TX-power tracking mode that relies on these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.c

## Purpose

`fw.c` handles RTL8188EE firmware download, firmware self-reset, host-to-controller mailbox commands, reserved-page packet upload, firmware power-mode commands, AP offload, join-BSS reporting, and P2P power-save offload programming. It is the bridge between the host driver and the 8051-style firmware running on the NIC.

## Important APIs And Functions

`rtl88e_download_fw()` consumes `rtlhal->pfirmware` and `rtlhal->fwsize`, skips a Realtek firmware header when present, enables firmware download mode, writes firmware pages, disables download mode, and waits for checksum and firmware-ready bits. `rtl88e_fill_h2c_cmd()` validates `rtlhal->fw_ready`, copies up to 7 bytes into a temporary H2C buffer, and delegates to `_rtl88e_fill_h2c_command()`. The private H2C writer serializes mailbox access with `h2c_lock` and `rtlhal->h2c_setinprogress`, cycles four HME boxes, waits for firmware to clear the target box through `REG_HMETFR`, and writes normal or extended mailbox registers.

Public command helpers include `rtl88e_set_fw_pwrmode_cmd()`, `rtl88e_set_fw_joinbss_report_cmd()`, `rtl88e_set_fw_ap_off_load_cmd()`, `rtl88e_set_fw_rsvdpagepkt()`, and `rtl88e_set_p2p_ps_offload_cmd()`. `rtl88e_firmware_selfreset()` toggles the MCU reset bit in `REG_SYS_FUNC_EN + 1`.

## Control Flow

Firmware download starts only if the firmware pointer exists. Existing firmware-ready state in `REG_MCUFWDL` causes a self-reset before a fresh load. `_rtl88e_write_fw()` pads firmware using `rtl_fill_dummy()`, splits it into 4 KiB pages, and writes each page through `rtl_fw_page_write()`. `_rtl88e_fw_free_to_go()` polls for `FWDL_CHKSUM_RPT`, sets `MCUFWDL_RDY`, clears `WINTINI_RDY`, resets the firmware, and then polls until `WINTINI_RDY` appears.

H2C command flow is serialized because firmware mailboxes are shared state. If another H2C command is active, the caller waits in 100 us intervals up to a hard limit. For each command, the current `last_hmeboxnum` selects the mailbox register pair, the driver waits for firmware to read the box, writes element ID plus payload bytes, advances the mailbox number modulo four, and clears the in-progress flag.

Reserved-page flow builds static 128-byte-page templates for beacon, PS-Poll, null data, and probe response, patches MAC/BSSID/AID fields from `rtl_mac`, sends the entire reserved buffer via `rtl_cmd_send_packet()`, and then informs firmware of page locations by H2C command. P2P power-save flow programs CTWindow, up to two NoA descriptors, TSF-adjusted start times, P2P role flags, and then sends the compact offload state to firmware.

## State And Persistence Behavior

Firmware state persists in NIC memory and in `rtlhal`: `fw_version`, `fw_subversion`, `fw_ready`, `last_hmeboxnum`, `h2c_setinprogress`, and `p2p_ps_offload`. `reserved_page_packet` is a file-static mutable buffer; each reserved-page upload rewrites address fields in place. P2P offload updates hardware NoA registers and the firmware offload byte structure. Power-mode commands reflect current `rtl_ps_ctl` fields such as smart PS and awake interval.

## Dependencies And Integration Points

The file depends on shared firmware header definitions, efuse/base/core helpers, raw MMIO helpers, H2C field macros from `fw.h`, 802.11 frame field setters, SKB allocation, and `rtl_cmd_send_packet()`. `hw.c` calls firmware download during initialization and routes `HW_VAR_H2C_*` operations into these helpers. Power management in `hw.c` depends on the firmware power-mode command emitted here.

## Risks And Edge Cases

`rtl88e_download_fw()` returns `0` even when `_rtl88e_fw_free_to_go()` reports an error after printing an error, so callers relying only on the return value may mark firmware ready incorrectly. H2C wait loops are bounded but busy-wait with microsecond delays, which can stall callers. The H2C API copies `cmd_len` bytes into an 8-byte temporary buffer and supports only 1-7 byte payloads in the private writer; callers must preserve that contract. `reserved_page_packet` is global mutable state and can race if multiple uploads occur concurrently. P2P NoA count handling mutates `noa_count_type[]` while adjusting start times.

## Test Signals

Tests should check successful and failed firmware download paths, firmware header stripping, page writes with exact and partial 4 KiB sizes, checksum/ready polling timeouts, H2C serialization under concurrent callers, mailbox wraparound, no-command behavior when `fw_ready` is false, reserved-page packet address patching, AP offload fields, power-mode command bytes, and P2P NoA/CTWindow register programming across GO and client roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.h

## Purpose

`fw.h` defines the RTL8188EE firmware interface: firmware image size and polling constants, firmware header detection, firmware power-state bit encodings, H2C command IDs, H2C payload lengths, payload packing helpers, and the public firmware helper prototypes implemented in `fw.c`.

## Important APIs, Types, And Constants

`enum rtl8188e_h2c_cmd` assigns command IDs for reserved pages, join-BSS report, keepalive, AP offload, power mode, P2P power-save offload, WOWLAN, AOAC, and the driver RA-mask extension. The `FW_PS_*` macros encode RPWM/CPWM and firmware low-power states used by `hw.c` clock and firmware-LPS logic. Inline setters such as `set_h2ccmd_pwrmode_parm_mode()`, `set_h2ccmd_pwrmode_parm_rlbm()`, and related macros pack command payloads in firmware-defined byte layouts.

The public prototypes are `rtl88e_download_fw()`, `rtl88e_fill_h2c_cmd()`, `rtl88e_firmware_selfreset()`, `rtl88e_set_fw_pwrmode_cmd()`, `rtl88e_set_fw_joinbss_report_cmd()`, `rtl88e_set_fw_ap_off_load_cmd()`, `rtl88e_set_fw_rsvdpagepkt()`, and `rtl88e_set_p2p_ps_offload_cmd()`.

## Control Flow And Integration

The header has no runtime control flow. It is included by `fw.c` for command construction and by `hw.c` for firmware power-state constants, H2C routing, and firmware reset/download integration. `pagenum_128()` supports reserved-page sizing semantics, while the command length constants constrain `rtl88e_fill_h2c_cmd()` callers.

## State And Persistence Behavior

No state is stored in this header, but macro values define persistent hardware/firmware protocol semantics. Changing IDs, lengths, or bit definitions changes on-wire mailbox payloads and can break firmware compatibility.

## Dependencies, Risks, And Test Signals

The macros depend on little-endian bitfield helpers such as `SET_BITS_TO_LE_1BYTE()` and `u8p_replace_bits()`. There is a duplicated `FW_PWR_STATE_ACTIVE`/`FW_PWR_STATE_RF_OFF` definition pair, which currently resolves identically but should be kept in mind during maintenance. The enum entry `H2C_88E_P2P_PS_OFFLOAD = 024` is an octal literal in C syntax; it equals decimal 20, not decimal 24. Build tests, static checks for payload length versus mailbox capacity, and hardware command smoke tests are the main signals for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.c

## Purpose

`hw.c` is the central RTL8188EE hardware-control implementation. It initializes and shuts down the PCIe NIC, maps mac80211/rtlwifi hardware variables to register operations, manages beacon and interrupt registers, downloads firmware, configures MAC/BB/RF blocks, reads EFUSE/EEPROM adapter data, manages hardware security CAM entries, updates rate tables, handles RF-kill state, and initializes Bluetooth coexistence.

## Important APIs And Functions

The public API exported through `hw.h` includes `rtl88ee_hw_init()`, `rtl88ee_card_disable()`, `rtl88ee_get_hw_reg()`, `rtl88ee_set_hw_reg()`, `rtl88ee_read_eeprom_info()`, `rtl88ee_enable_interrupt()`, `rtl88ee_disable_interrupt()`, `rtl88ee_interrupt_recognized()`, `rtl88ee_set_network_type()`, `rtl88ee_set_check_bssid()`, `rtl88ee_set_qos()`, beacon helpers, `rtl88ee_update_interrupt_mask()`, `rtl88ee_update_hal_rate_tbl()`, `rtl88ee_update_channel_access_setting()`, `rtl88ee_gpio_radio_on_off_checking()`, `rtl88ee_enable_hw_security_config()`, `rtl88ee_set_key()`, Bluetooth coexistence helpers, suspend/resume stubs, and the firmware clock-off timer callback.

Private helpers organize major responsibilities: beacon control (`_rtl88ee_stop_tx_beacon()`, `_rtl88ee_resume_tx_beacon()`, `_rtl88ee_return_beacon_queue_skb()`), firmware LPS/clock transitions (`_rtl88ee_set_fw_clock_on/off()`, `_rtl88ee_fwlps_enter/leave()`), LLT/RQPN and MAC initialization (`_rtl88ee_llt_table_init()`, `_rtl88ee_init_mac()`), EEPROM parsing (`_rtl88ee_read_adapter_info()`, `_rtl88ee_read_txpower_info_from_hwpg()`), rate programming (`rtl88ee_update_hal_rate_table()`, `rtl88ee_update_hal_rate_mask()`), and NIC poweroff (`_rtl88ee_poweroff_adapter()`).

## Control Flow

`rtl88ee_hw_init()` is the primary bring-up sequence. It marks the adapter as initializing, temporarily enables local IRQs because init can be long, disables ASPM, determines whether MAC function was already enabled, runs `_rtl88ee_init_mac()`, downloads firmware with `rtl88e_download_fw()`, marks firmware ready, initializes firmware mailbox and power-state fields, applies MAC/BB/RF parameter tables through `phy.c`, enables BB CCK/OFDM, stores RF channel values, configures RRSR and CAM/security, sets MAC address, configures ASPM backdoor, restores ASPM, selects initial RF path/antenna, runs IQK and LCK, applies PA bias and voltage workarounds, sets NAV, and finally calls `rtl88e_dm_init()`.

`rtl88ee_set_hw_reg()` is a large dispatcher used by the rtlwifi core. It writes MAC address, BSSID, basic rates, SIFS, slot time, ACK preamble, WPA security config, AMPDU spacing/factor, AC/ACM settings, RCR, retry limit, TSF reset/correction, EFUSE counters, PHY IO commands, RPWM, firmware power mode, firmware LPS status, firmware LPS action, join-BSS reserved-page download, P2P offload, AID, and keepalive. `rtl88ee_get_hw_reg()` provides the complementary subset for RCR, RF state, firmware-LPS RF-on status, firmware PS status, TSF, and WOWLAN capability placeholder.

Shutdown flows through `rtl88ee_card_disable()`, which forces no-link media status, optionally powers off LEDs, sets the halt-NIC power-save level, calls `_rtl88ee_poweroff_adapter()`, and clears IQK initialization. `_rtl88ee_poweroff_adapter()` stops TX report, waits for RXDMA idle, disables RX DMA, parses LPS-enter and disable power-sequence arrays, resets firmware/MCU state, disables 32K, and parks GPIOs.

## State And Persistence Behavior

The file is responsible for initializing many long-lived fields in `rtlhal`, `rtlpci`, `rtlphy`, `rtlefuse`, `rtlpriv->psc`, `rtlpriv->sec`, and `rtlpriv->btcoexist`. EEPROM/EFUSE data persists into `rtlefuse`: MAC, vendor/device IDs, channel plan, TX-power levels, thermal meter, regulatory domain, board type, WOWLAN, crystal cap, antenna diversity, and Bluetooth coexistence. Register writes persist in hardware until reset or power transition. CAM entries persist until explicitly cleared or reset. Firmware LPS state spans both driver fields and firmware/hardware RPWM/CPWM registers.

## Dependencies And Integration Points

`hw.c` depends on shared rtlwifi PCI, base, efuse, regulatory, CAM, power-save, power-sequence, firmware, PHY, DM, LED, and register layers. It calls `rtl_hal_pwrseqcmdparsing()` with arrays from `pwrseq.c`, firmware helpers from `fw.c`, PHY config/calibration functions from `phy.c`, LED helpers from `led.c`, CAM helpers from `cam.h`, and PCI ring state from `pci.h`. mac80211 integration is visible through `struct ieee80211_hw`, `struct ieee80211_sta`, interface types, station capabilities, and BSS state fields.

## Risks And Edge Cases

Hardware init has many ordered side effects; moving firmware download, BB/RF config, RF path switching, or DM init can break bring-up. `rtl88e_download_fw()` currently returns success despite internal ready errors, so `rtl88ee_hw_init()` can set `fw_ready` after a printed firmware failure. Beacon queue cleanup directly walks DMA descriptors and must stay synchronized with TX ring ownership. `rtl88ee_set_hw_reg()` uses untyped `u8 *val` casts, so callers must supply exactly the expected storage. Rate-mask H2C programming assumes firmware RA-mask support and correct station drv_priv state. Poweroff waits for queues but may continue after bounded busy waits. EEPROM parsing uses many magic offsets and fallback values; autoload-fail paths are only partial.

## Test Signals

Strong signals include successful probe/init with firmware ready, MAC/BB/RF table programming, correct EEPROM parsing on valid and autoload-fail devices, LLT table initialization, RCR preservation after MAC config, CAM add/delete/clear for WEP/TKIP/AES pairwise and group keys, interrupt mask enable/disable and recognition, beacon mode transitions across station/AP/adhoc/mesh/no-link, reserved-page download on association, RF-kill GPIO transitions, IPS/LPS enter/leave, rate-mask H2C payloads for B/G/N and RSSI levels, Bluetooth coexistence register init, and clean card disable followed by reinitialize with IQK rerun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.h

## Purpose

`hw.h` declares the RTL8188EE hardware-operation surface implemented by `hw.c`. It is the interface used by the rtlwifi core and adjacent RTL8188EE modules to initialize the NIC, manipulate hardware variables, manage interrupts, control beacon/network behavior, program security, read EFUSE data, and handle Bluetooth coexistence.

## Important APIs

The header exposes initialization and teardown (`rtl88ee_hw_init()`, `rtl88ee_card_disable()`), hardware variable dispatch (`rtl88ee_get_hw_reg()`, `rtl88ee_set_hw_reg()`), EEPROM parsing (`rtl88ee_read_eeprom_info()`), interrupt control and recognition, network type/BSSID/QoS/beacon operations, interrupt mask updates, rate table updates, channel access settings, GPIO radio checking, hardware security configuration, CAM key programming, Bluetooth coexistence parsing/register/hardware initialization, suspend/resume stubs, and `rtl88ee_fw_clk_off_timer_callback()`.

## Control Flow And Integration

The header itself is declarative. Function pointers in the device config table normally reference many of these functions, while other RTL8188EE modules call them directly for firmware clock timers and cross-module setup. `rtl88ee_set_hw_reg()` and `rtl88ee_get_hw_reg()` are especially important because they hide many register operations behind generic `HW_VAR_*` selectors used by common rtlwifi code.

## State, Dependencies, Risks, And Test Signals

No state is defined here, but the prototypes operate on shared `struct ieee80211_hw`, `struct rtl_int`, `struct ieee80211_sta`, and kernel/mac80211 types. The primary risk is signature drift from core rtlwifi operation tables or enum semantics. Build coverage should ensure this header remains consistent with `hw.c` and with the ops table that binds the RTL8188EE implementation. Runtime signals are the same as `hw.c`: init, interrupt, network mode, security, rate, RF-kill, and power-management behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.c

## Purpose

`led.c` provides RTL8188EE software LED control for the rtlwifi LED framework. It turns the configured LED pin on or off by manipulating LEDCFG registers and maps high-level link/power LED actions to those pin operations.

## Important APIs And Functions

`rtl88ee_sw_led_on()` handles `LED_PIN_GPIO0` and `LED_PIN_LED0` by setting or clearing `REG_LEDCFG2` bit 7 depending on open-drain configuration; unsupported pins are ignored. `rtl88ee_sw_led_off()` reverses the operation and, for `LED_PIN_LED0`, writes a sequence that clears LED state and sets bit 3. `_rtl88ee_sw_led_control()` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to LED-on, maps `LED_CTL_POWER_OFF` to LED-off, and ignores TX/RX/site-survey/start-to-link/no-link variants. `rtl88ee_led_control()` is the public wrapper.

## Control Flow

Callers such as `hw.c` invoke `rtl88ee_led_control()` when media status, RF power state, or card disable state changes. The public wrapper selects the software LED path; the private dispatcher chooses on/off behavior from the action enum; the pin helpers write MMIO registers through `rtl_write_byte()` after reading current `REG_LEDCFG2` state where needed.

## State And Persistence Behavior

The persistent state is hardware LED configuration in `REG_LEDCFG2` and `rtlpriv->ledctl.led_opendrain`. The selected pin is stored in `rtlpriv->ledctl.sw_led0`, initialized elsewhere. There is no timer or blinking state in this file.

## Dependencies And Integration Points

The file depends on `wifi.h`, `reg.h`, `led.h`, `enum rtl_led_pin`, `enum led_ctl_mode`, and raw MMIO helpers. It is integrated by `hw.c` for init, media status, RF power state, and power-off LED updates.

## Risks And Test Signals

Unsupported LED actions intentionally no-op, so users expecting blink-on-traffic behavior will not see it here. Register semantics differ between open-drain and non-open-drain boards; wrong OEM/board configuration can invert LED behavior. Tests should verify LED on/off register writes for both open-drain modes, link/no-link/power-off action mapping, and no unintended register changes for ignored actions or unsupported pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.h

## Purpose

`led.h` declares the RTL8188EE LED-control functions implemented in `led.c`.

## Important APIs

The exported functions are `rtl88ee_sw_led_on()`, `rtl88ee_sw_led_off()`, and `rtl88ee_led_control()`. The first two operate on a specific `enum rtl_led_pin`; the public control function accepts an `enum led_ctl_mode` and applies the driver’s action mapping.

## Control Flow, State, And Integration

The header has no executable flow or state. `hw.c` and the rtlwifi operation table use these declarations to control LEDs during init, link changes, RF state changes, and shutdown. State lives in `rtlpriv->ledctl` and the LEDCFG hardware register.

## Risks And Test Signals

The header’s main risk is prototype drift with `led.c` or the common rtlwifi LED ops interface. Compile tests and simple hardware LED action tests are sufficient coverage for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.c

## Purpose

`phy.c` implements RTL8188EE baseband and RF programming, RF register serialization, MAC/BB/RF parameter-table loading, TX-power computation and programming, bandwidth and channel switching, scan-related PHY IO commands, IQ calibration, LC calibration, RF path switching, and RF power-state transitions. It is the main physical-layer control file used by hardware initialization, dynamic management, and power management.

## Important APIs And Functions

Public register accessors are `rtl88e_phy_query_bb_reg()`, `rtl88e_phy_set_bb_reg()`, `rtl88e_phy_query_rf_reg()`, and `rtl88e_phy_set_rf_reg()`. RF accesses are serialized with `rtlpriv->locks.rf_lock` and implemented through `_rtl88e_phy_rf_serial_read()` and `_rtl88e_phy_rf_serial_write()`.

Configuration APIs are `rtl88e_phy_mac_config()`, `rtl88e_phy_bb_config()`, `rtl88e_phy_rf_config()`, and `rtl88e_phy_config_rf_with_headerfile()`. They load Realtek table arrays from `table.h`, apply conditional branches based on board/interface/platform, store TX-power original offsets from PG tables, initialize `rtlphy->phyreg_def`, and delegate RF6052 setup to `rf.c`.

Runtime APIs include `rtl88e_phy_set_txpower_level()`, `rtl88e_phy_get_txpower_level()`, `rtl88e_phy_set_bw_mode()`, `rtl88e_phy_sw_chnl()`, `rtl88e_phy_scan_operation_backup()`, `rtl88e_phy_iq_calibrate()`, `rtl88e_phy_lc_calibrate()`, `rtl88e_phy_set_rfpath_switch()`, `rtl88e_phy_set_io_cmd()`, and `rtl88e_phy_set_rf_power_state()`.

## Control Flow

During `rtl88ee_hw_init()`, `rtl88e_phy_mac_config()` writes MAC table bytes, `rtl88e_phy_bb_config()` enables BB/RF functions and loads PHY/PG/AGC tables, and `rtl88e_phy_rf_config()` invokes RF6052 configuration, which calls back into `rtl88e_phy_config_rf_with_headerfile()`. After table programming, initialization reads RF channel state, selects RF path, runs IQK/LCK, and starts DM.

Channel switching is staged by `_rtl88e_phy_sw_chnl_step_by_step()`: precommands set TX power for the target channel, RF-dependent commands write `RF_CHNLBW` with the channel number for each RF path, and postcommands finish immediately. `rtl88e_phy_sw_chnl()` guards against concurrent bandwidth/channel work and halts on invalid stopped/IO states. Bandwidth switching writes MAC bandwidth registers, RRSR sideband fields, BB RF mode bits, CCK/OFDM sideband bits, and then calls `rtl88e_phy_rf6052_set_bandwidth()`.

TX-power flow starts from EFUSE tables loaded in `hw.c`. `_rtl88e_get_txpower_index()` derives CCK, OFDM, HT20, and HT40 indexes for the current channel and RF path. `_rtl88e_ccxpower_index_check()` updates current power indexes in `rtlphy`, and `rtl88e_phy_rf6052_set_cck_txpower()` / `rtl88e_phy_rf6052_set_ofdm_txpower()` write the hardware values. `dm.c` calls this path for thermal tracking and dynamic TX power.

IQK flow runs up to three calibration attempts, saving ADDA/MAC/BB registers, switching PI mode as needed, testing path A TX/RX and optionally path B, comparing candidate results with tolerance, filling IQK matrices, and saving the chosen matrix for recovery. LC calibration waits briefly for scans to stop, pauses TX or changes RF mode, toggles RF channel calibration, waits 100 ms, and restores state.

RF power-state flow in `rtl88e_phy_set_rf_power_state()` delegates to `_rtl88ee_phy_set_rf_power_state()`. ERFON may re-enable the NIC through `rtl_ps_enable_nic()` if halted by IPS or directly turns RF on. ERFOFF and ERFSLEEP wait for TX queues to drain with bounded loops, then either disable NIC for IPS/halt or put RF to sleep and update LEDs.

## State And Persistence Behavior

The file updates persistent runtime fields in `rtlpriv->phy`: RF register definitions, RF path/channel values, current TX-power indexes, original MCS TX-power offsets, default initial gains, framesync values, channel/bandwidth in-progress flags, IQK backups/results, RFPI state, LCK flag, IO command state, and RF type/path information. It also updates `rtlpriv->psc.rfpwr_state` on successful RF power changes. Hardware side effects include BB/RF tables, RF channel/bandwidth registers, TXAGC power registers, IQK/LC calibration registers, antenna path switches, scan CCA/IGI settings, RF sleep/on register sequences, and PCI TX-queue-dependent power decisions.

## Dependencies And Integration Points

`phy.c` depends on `wifi.h`, `pci.h`, `ps.h`, device register definitions, `rf.h`, `dm.h`, and large table arrays from `table.h`. It integrates with `hw.c` for initialization and power-state operations, `dm.c` for thermal tracking, DIG scan pause/resume, and antenna path decisions, `rf.c` for RF6052-specific TX power and RF config, and shared rtlwifi power-save helpers for NIC enable/disable.

## Risks And Edge Cases

The table parsers use sentinel values (`0xcdcdcdcd`, `0xDEAD`, `0xCDEF`, `0xCDCD`) and manual index increments; malformed table lengths can skip or overrun intended entries despite boundary guards. RF register access requires correct `phyreg_def` initialization before use. Channel switching only warns for channels outside 1-14 and is 2.4 GHz specific, despite some generic 5 GHz structures elsewhere. Calibration code has many magic register values and sleeps; running during scan, RF changes, or power transitions can affect traffic. RF power-off waits for queues but proceeds after bounded retries. IO scan pause/resume changes DIG/CCA but the write-DIG call is commented out in resume, so state and hardware can diverge if not otherwise refreshed.

## Test Signals

Coverage should include MAC/BB/AGC/RF table loading, conditional table branches for board/interface/platform values, RF register read/write serialization, channel switch across channels 1/6/11/14, bandwidth 20 and 20/40 with both sidebands, EFUSE-derived TX-power programming and default fallback, scan backup/restore, IQK success/failure/recovery paths, LCK while scanning, RF path switch for main/aux and antenna-diversity modes, ERFON/ERFOFF/ERFSLEEP transitions with queued TX traffic, and integration with DM thermal tracking and hardware init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.h

## Purpose

`phy.h` defines RTL8188EE PHY-layer constants, EEPROM offsets, channel-switch command structures, configuration enums, antenna and antenna-diversity enums, EFUSE/TX-power helper structures, and the public PHY function prototypes implemented in `phy.c`.

## Important APIs, Types, And Constants

`struct swchnlcmd` and `enum swchnlcmd_id` define the staged channel-switch command format. `enum baseband_config_type` selects PHY register versus AGC table loading. `struct efuse_contents`, `struct tx_power_struct`, and related offset macros describe EFUSE and TX-power data shapes. `enum _ANT_DIV_TYPE` defines the antenna-diversity modes consumed by both `phy.c` and `dm.c`.

The exported prototypes cover BB/RF register access, MAC/BB/RF configuration, original hardware register snapshotting, TX-power get/set, scan backup/restore, bandwidth changes, channel switching, IQK/LCK calibration, RF path switching, RF header-table config, PHY IO commands, and RF power-state changes.

## Control Flow And Integration

This header is included by `hw.c`, `dm.c`, and RF-related RTL8188EE modules. It does not execute logic, but its structures drive `phy.c` command staging and EFUSE interpretation. Constants such as `MAX_TX_COUNT`, IQK register counts, and EEPROM offsets must remain synchronized with table parsing and EFUSE layouts.

## State And Persistence Behavior

No state is allocated here. The declared structures describe state stored in `rtlphy`, `rtlefuse`, or stack temporaries in implementation files. The enums and macro values directly affect persisted hardware register programming and calibration behavior.

## Dependencies, Risks, And Test Signals

The header depends on shared rtlwifi channel, RF path, IO type, and power-state enums. Risks include duplicated macro definitions (`IQK_ADDA_REG_NUM`, `IQK_MAC_REG_NUM`) and magic EEPROM offsets becoming inconsistent with hardware documentation. Build tests, table parser tests, EFUSE decode tests, and end-to-end PHY init/channel/power tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.c

## Purpose

`pwrseq.c` materializes the RTL8188EE power transition tables declared as macros in `pwrseq.h`. These arrays are consumed by the shared rtlwifi power-sequence parser to move the NIC between card emulation, active, suspend, power-down/card-disabled, radio-off, and low-power states.

## Important APIs And Data

The file defines `struct wlan_pwr_cfg` arrays: `rtl8188ee_power_on_flow`, `rtl8188ee_radio_off_flow`, `rtl8188ee_card_disable_flow`, `rtl8188ee_card_enable_flow`, `rtl8188ee_suspend_flow`, `rtl8188ee_resume_flow`, `rtl8188ee_hwpdn_flow`, `rtl8188ee_enter_lps_flow`, and `rtl8188ee_leave_lps_flow`. Each array concatenates one or more transition macros and ends with `RTL8188EE_TRANS_END`.

## Control Flow

There is no executable function in this file. Runtime control flow occurs when callers such as `_rtl88ee_init_mac()` and `_rtl88ee_poweroff_adapter()` pass these arrays to `rtl_hal_pwrseqcmdparsing()`. The parser walks array entries, applies interface/fab/cut masks, performs writes, polls, delays, and stops at the end command.

## State And Persistence Behavior

The arrays are static driver data with no mutable state. Their entries cause persistent hardware state changes when parsed: MAC reset bits, suspend bits, RF-off writes, TX pause, DMA/WMAC reset, RPWM writes, BB clock and TSF clock changes, and card power-down controls.

## Dependencies And Integration Points

`pwrseq.c` depends on `../pwrseqcmd.h` for `struct wlan_pwr_cfg` and command definitions, and on `pwrseq.h` for transition macros and array size expressions. `hw.c` integrates these arrays into MAC init and adapter poweroff. The arrays are also exposed through aliases in `pwrseq.h`.

## Risks And Test Signals

Array size macros must match the number of entries emitted by transition macros plus the end marker; a mismatch can truncate or leave uninitialized entries. The `rtl8188ee_card_enable_flow` size expression uses ACT-to-CARDEMU and CARDEMU-to-PDN step counts even though the initializer uses CARDDIS-to-CARDEMU and CARDEMU-to-ACT; the counts are currently both 10, but this is fragile. Tests should verify parser success for NIC enable, disable, suspend/resume, radio off, and LPS enter/leave, including PCIe interface mask filtering and polling timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.h

## Purpose

`pwrseq.h` describes RTL8188EE hardware power-state transitions in the `struct wlan_pwr_cfg` macro format consumed by the shared rtlwifi power-sequence parser. It documents the six hardware states and defines step counts, transition command macros, external arrays, and NIC-flow aliases.

## Important APIs, Types, And Constants

The transition macros include `RTL8188EE_TRANS_CARDEMU_TO_ACT`, `RTL8188EE_TRANS_ACT_TO_CARDEMU`, `RTL8188EE_TRANS_CARDEMU_TO_SUS`, `RTL8188EE_TRANS_SUS_TO_CARDEMU`, `RTL8188EE_TRANS_CARDEMU_TO_CARDDIS`, `RTL8188EE_TRANS_CARDDIS_TO_CARDEMU`, `RTL8188EE_TRANS_CARDEMU_TO_PDN`, `RTL8188EE_TRANS_PDN_TO_CARDEMU`, `RTL8188EE_TRANS_ACT_TO_LPS`, `RTL8188EE_TRANS_LPS_TO_ACT`, and `RTL8188EE_TRANS_END`. Each entry encodes register offset, cut/fab/interface masks, base address, command type, bit mask, and value. Extern declarations expose the arrays defined in `pwrseq.c`, and `RTL8188EE_NIC_*` aliases provide the names used by hardware code.

## Control Flow

The header itself does not execute; it expands into data initializers. At runtime `rtl_hal_pwrseqcmdparsing()` walks the generated arrays. Write commands update registers, polling commands wait for masked values, delay commands sleep for microseconds or milliseconds, and `PWR_CMD_END` terminates a flow.

## State And Persistence Behavior

The macro arrays encode transitions that persist in hardware power state: enabling/disabling WL suspend, resetting BB/MAC, pausing TX, polling TX queues idle, switching TSF/BB clocks, setting RPWM for SDIO/USB/PCIe, entering low-power state, and driving power-down bits. They do not allocate driver state themselves.

## Dependencies And Integration Points

The header depends on `../pwrseqcmd.h` for command constants and masks. It is included by `pwrseq.c` to instantiate arrays and by `hw.c` through flow aliases used during MAC init and adapter poweroff. Although many entries include USB/SDIO masks, this RTL8188EE PCIe driver selects PCIe-specific behavior through parser interface masks.

## Risks And Test Signals

The macros contain hardware-document magic values; small edits can make the NIC fail to wake, sleep, or power down. Step-count definitions must stay aligned with macro entry counts and extern array sizes. Comments mention RTL8723 in the include guard and PCIe section despite RTL8188EE content, which is cosmetic but can confuse maintenance. Tests should parse every alias flow with PCIe masks, validate that each reaches `RTL8188EE_TRANS_END`, and run suspend/resume, IPS, LPS, NIC enable, and NIC disable cycles on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.h -->
