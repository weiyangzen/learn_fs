# Research: subset-b-004884

This grouped report covers Realtek rtlwifi RTL8192C common PHY helpers and RTL8192CE PCI driver files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.c

## Purpose
This is the RTL8192C-family shared PHY implementation used by RTL8192CE and related rtlwifi drivers. It provides baseband register access, RF 3-wire serial access, BB/RF initialization helpers, transmit-power indexing, channel switching, bandwidth dispatch, IQ/LC/AP calibration entry points, RF path switching, scan-time dynamic-initial-gain pause/resume, and RF on/sleep programming.

## Important APIs, Types, And Functions
Exported entry points include `rtl92c_phy_query_bb_reg()`, `rtl92c_phy_set_bb_reg()`, `_rtl92c_phy_rf_serial_read()`, `_rtl92c_phy_rf_serial_write()`, `rtl92c_phy_rf_config()`, `_rtl92c_phy_bb8192c_config_parafile()`, `_rtl92c_store_pwrindex_diffrate_offset()`, `_rtl92c_phy_init_bb_rf_register_definition()`, `rtl92c_phy_set_txpower_level()`, `rtl92c_phy_update_txpower_dbm()`, `rtl92c_phy_set_bw_mode()`, `rtl92c_phy_sw_chnl()`, `rtl92c_phy_iq_calibrate()`, `rtl92c_phy_lc_calibrate()`, `rtl92c_phy_set_io_cmd()`, `rtl92c_phy_set_io()`, `rtl92ce_phy_set_rf_on()`, and `_rtl92c_phy_set_rf_sleep()`. Internal helpers implement 1T BB adjustments, channel command arrays, RF-channel writes, IQK candidate comparison, ADDA/MAC save and restore, and per-path IQK matrix writes.

## Control Flow
Initialization first maps path-specific BB register definitions, loads chip-specific BB/AGC/PG tables through `rtlpriv->cfg->ops`, optionally adjusts 1T devices, and caches default gain/frame-sync values. RF access goes through `rtl_get_bbreg()`/`rtl_set_bbreg()` and either direct 3-wire LSSI sequences or deprecated firmware RF access stubs. Channel switching builds pre/RF/post command arrays, sets TX power, writes `RF_CHNLBW` for every active RF path, applies a UMC-B-cut channel-6 workaround, and advances stage/step state until complete. IQ calibration performs up to three trials, compares trial similarity, programs path A/B TX/RX imbalance matrices, and saves calibration registers for later recovery.

## State And Persistence
All state is runtime state in `struct rtl_phy`, `struct rtl_efuse`, `struct rtl_priv`, and hardware registers. The file updates `mcs_txpwrlevel_origoffset`, `pwrgroup_cnt`, `default_initialgain`, `framesync`, `phyreg_def[]`, current TX power indices, `rfreg_chnlval[]`, channel/bandwidth in-progress flags, IQK backup arrays, IQK result registers, RFPI mode state, and DIG backup values. EFUSE-derived power arrays are overwritten by `rtl92c_phy_update_txpower_dbm()` for runtime power changes, but this does not write back to EEPROM/EFUSE.

## Dependencies And Integration Points
The code depends on rtlwifi core register helpers, `rtl8192ce/reg.h` register definitions, `rtl8192ce/def.h` chip enums, common DM/FW helpers, and per-device HAL ops for BB table loading, RF6052 configuration, TX-power programming, bandwidth callbacks, and LC calibration. It integrates with mac80211 scan/channel changes, PCI power management through the HAL, dynamic management through `rtl92c_dm_write_dig()`, and firmware H2C power workflows from CE-specific code.

## Risks And Edge Cases
Register sequences are timing-sensitive and use `mdelay()`/`udelay()` around RF read/write edges. The firmware RF serial helpers are deprecated stubs that warn and return zero, so setting `rf_mode` to firmware RF operation would silently lose useful RF access. Channel switching only accepts 2.4 GHz channels 1-14. IQK result selection has several fallback paths and partially populated results can still program TX-only matrices. `RT_CANNOT_IO(hw)` is defined false, so callers rely on higher-level stop/unload checks.

## Test Signals
Useful signals include successful BB/AGC/RF table load during probe, stable RF readback through both RF paths, correct channel and 20/40 MHz switching, TX power updates following channel changes and dbm requests, IQK recovery after power cycle, LC calibration completion, scan entry/exit restoring DIG and TX power, RF on/sleep transitions without stuck TX queues, and absence of WARN_ONCE for illegal channels or deprecated firmware RF paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.h

## Purpose
This header declares the RTL8192C common PHY interface and constants shared by chip-specific drivers. It exposes BB/RF register accessors, PHY initialization, TX-power conversion, channel/bandwidth switching, calibration, RF power, and scan I/O control helpers.

## Important APIs, Types, And Functions
Important definitions include command-count limits, IQK register counts, EFUSE offsets, `MAX_TXPWR_IDX_NMODE_92S`, `enum swchnlcmd_id`, `struct swchnlcmd`, `enum hw90_block_e`, `enum baseband_config_type`, `enum ra_offset_area`, `enum antenna_path`, antenna-select bitfield structs, `struct efuse_contents`, and `struct tx_power_struct`. The prototypes match exported functions in `phy_common.c` and the CE-specific implementations in `phy.c`/`rf.c`.

## Control Flow
The header shapes control flow by giving chip-specific HAL ops a common PHY contract: CE code supplies table-loading and RF6052 routines, while common code calls those through `rtlpriv->cfg->ops`. Channel switching uses `struct swchnlcmd`; BB table loading uses `BASEBAND_CONFIG_PHY_REG` and `BASEBAND_CONFIG_AGC_TAB`; TX power code uses the EFUSE and MCS offset structures declared here.

## State And Persistence
The header declares data layouts but no storage. Its structures describe runtime copies of EFUSE contents and TX-power tables. Persistence remains in hardware EFUSE/EEPROM and runtime caches maintained elsewhere.

## Dependencies And Integration Points
It depends on rtlwifi types such as `struct ieee80211_hw`, `enum radio_path`, `enum wireless_mode`, `enum rf_pwrstate`, and `enum io_type`. It is included by CE PHY/HW code and is part of the internal ABI between `rtl8192c` common code and `rtl8192ce`.

## Risks And Edge Cases
There is duplicated content with `rtl8192ce/phy.h`, including the misspelled `rtl92c_phy_config_rf_with_feaderfile()` prototype. Constants such as `RT_CANNOT_IO(hw)` are hard-coded here, so behavioral changes affect every includer. Bitfield structs are layout-sensitive and should not be used as hardware ABI without endian review.

## Test Signals
Build coverage should catch prototype drift between common and CE implementations. Runtime coverage comes indirectly from probe, channel switch, TX-power update, RF power, and calibration paths that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/phy_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/Makefile

## Purpose
This Kbuild file defines the RTL8192CE PCI module composition. It builds `rtl8192ce.o` from dynamic-management, hardware, LED, PHY, RF, software-registration, table, and transmit/receive descriptor objects.

## Important APIs, Types, And Functions
The key build variables are `rtl8192ce-objs` and `obj-$(CONFIG_RTL8192CE)`. The object list is `dm.o`, `hw.o`, `led.o`, `phy.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`.

## Control Flow
At kernel build time, enabling `CONFIG_RTL8192CE` links the listed objects into one driver module. There is no runtime control flow in this file; runtime module registration is provided by `sw.c`.

## State And Persistence
The file has no runtime state. It controls build artifacts and module linkage only.

## Dependencies And Integration Points
It integrates with Linux Kbuild and the parent rtlwifi/realtek wireless build tree. The module depends on symbols from common rtlwifi code and `../rtl8192c` common helpers referenced by the listed objects.

## Risks And Edge Cases
Omitting an object breaks HAL operations or data tables at link time; adding objects changes the module surface. `trx.o` is part of the module even though this work item does not research it.

## Test Signals
The direct test signal is successful kernel or module build with `CONFIG_RTL8192CE=m/y` and no unresolved symbols from the listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/def.h

## Purpose
This header defines RTL8192CE/RTL8188CE chip-version, queue, RF, power, interface, descriptor-selection, PHY-status, and H2C command metadata used by the CE PCI driver.

## Important APIs, Types, And Functions
Key macros include RSSI/link-quality window sizes, channel-offset constants, RX queue IDs, chip-version bit masks, bonding identifiers, and RF type markers. Important enums are `version_8192c`, `rtl819x_loopback_e`, `rf_optype`, `rf_power_state`, `power_save_mode`, `power_polocy_config`, `interface_select_pci`, and `rtl_desc_qsel`. Small data structures include `phy_sts_cck_8192s_t` and `h2c_cmd_8192c`.

## Control Flow
The header is declarative. `hw.c` reads hardware registers into `enum version_8192c` values, maps those to RF topology, and uses queue IDs and descriptor selectors when programming DMA and descriptors. PHY code uses `rf_optype` to select direct or firmware RF register access.

## State And Persistence
No storage is declared. The enums and macros classify runtime state kept in `rtlhal`, `rtlphy`, PCI rings, and firmware command buffers.

## Dependencies And Integration Points
It is included by CE hardware, PHY, RF, DM, and common PHY code. It links register-level chip detection with rtlwifi-wide concepts such as RF paths, power states, and descriptor queues.

## Risks And Edge Cases
The chip-version enum encodes vendor, cut, package, and RF topology in bit fields, so incorrect masks can misclassify devices and choose wrong 1T/2T tables. The typo `power_polocy_config` is API surface. `struct phy_sts_cck_8192s_t` maps receive PHY reports and is layout-sensitive.

## Test Signals
Probe logs reporting the expected chip version and RF type, correct RX queue selection, valid descriptor qsel mapping, and stable RF operation across 88C, 92C, 1T1R, 1T2R, and 2T2R variants are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.c

## Purpose
This CE-specific dynamic-management file implements near-field dynamic TX-power reduction. It complements shared RTL8192C dynamic-management code by deciding when RTL8192CE should lower transmit power based on received signal power.

## Important APIs, Types, And Functions
The only function is `rtl92ce_dm_dynamic_txpower()`, exposed through the HAL ops table as `.dm_dynamic_txpower`. It uses `dynamic_txpower_enable`, `dm_flag`, `dynamic_txhighpower_lvl`, `last_dtp_lvl`, `undec_sm_pwdb`, `entry_min_undec_sm_pwdb`, and thresholds from `dm.h`.

## Control Flow
The function exits if dynamic TX power is disabled or high-power management is masked by `HAL_DM_HIPWR_DISABLE`. It chooses the signal metric from station, adhoc, or extension-port state, maps the value to normal or level-1 high-power reduction with hysteresis, and calls `rtl92c_phy_set_txpower_level()` when the level changes.

## State And Persistence
Runtime state is stored in `rtlpriv->dm` and current channel state in `rtlpriv->phy`. No persistent state is written. The effect is hardware TX AGC programming through subsequent PHY TX-power calls.

## Dependencies And Integration Points
It depends on rtlwifi `rtl_priv`, `rtl_mac`, and common PHY TX-power programming. It is invoked by the shared DM watchdog path through the CE HAL operation.

## Risks And Edge Cases
The code currently sets both near-field threshold branches to `TXHIGHPWRLEVEL_LEVEL1`; level 2 is defined but unused here. Signal thresholds are magic values and depend on correct RSSI/PWDB smoothing from shared DM. Incorrect link-state classification can leave power normal when close to a peer.

## Test Signals
Validate by observing `dynamic_txhighpower_lvl` changes under high RSSI, TX-power register changes after level transitions, no changes when disabled or disconnected, and stable throughput/range during DM watchdog runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.h

## Purpose
This header defines RTL8192CE dynamic-management thresholds, flags, rate-adaptive states, TX high-power levels, and function prototypes shared by CE and common DM code.

## Important APIs, Types, And Functions
Key constants include `HAL_DM_DIG_DISABLE`, `HAL_DM_HIPWR_DISABLE`, false-alarm DIG thresholds, bandwidth auto-switch thresholds, rate-adaptive states, CCK/OFDM table sizes, TX high-power levels, and near-field TX-power thresholds. Prototypes include shared routines such as `rtl92c_dm_init()`, `rtl92c_dm_watchdog()`, `rtl92c_dm_write_dig()`, `rtl92c_dm_init_edca_turbo()`, `rtl92c_dm_check_txpower_tracking()`, `rtl92c_dm_rf_saving()`, and CE-specific `rtl92ce_dm_dynamic_txpower()`.

## Control Flow
The header itself is declarative. The constants steer watchdog decisions for DIG, EDCA turbo, RF saving, rate adaptation, BT coexistence, and dynamic TX power in `dm.c` and the shared `rtl8192c/dm_common` implementation.

## State And Persistence
No storage is declared. The constants govern runtime fields in `rtlpriv->dm` and related PHY state. Nothing persists across driver unload or device reset.

## Dependencies And Integration Points
It is included by CE DM/HW/PHY/RF/SW code and by common PHY code where scan-time DIG pause/resume calls `rtl92c_dm_write_dig()`.

## Risks And Edge Cases
Threshold constants are tightly coupled to Realtek PHY calibration assumptions. Changing them can affect sensitivity, false alarms, throughput, and regulatory behavior. Some definitions duplicate table lengths and sizes.

## Test Signals
DM watchdog logs, false-alarm counters, rate-mask changes, RF-saving transitions, dynamic TX-power level changes, and stable scan/link behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.c

## Purpose
This is the main RTL8192CE PCI hardware-control implementation. It handles hardware register get/set operations, MAC/LLT/DMA initialization, firmware download orchestration, BB/RF initialization, security CAM programming, EEPROM/EFUSE decoding, chip-version detection, media/beacon state, interrupt masks, RF kill, power-off, rate table/mask updates, Bluetooth coexistence setup, and suspend/resume stubs.

## Important APIs, Types, And Functions
Major exported/internal surfaces include `rtl92ce_get_hw_reg()`, `rtl92ce_set_hw_reg()`, `_rtl92ce_llt_write()`, `_rtl92ce_llt_table_init()`, `_rtl92ce_init_mac()`, `_rtl92ce_hw_configure()`, `rtl92ce_enable_hw_security_config()`, `rtl92ce_hw_init()`, `_rtl92ce_read_chip_version()`, `rtl92ce_set_network_type()`, `rtl92ce_set_check_bssid()`, `rtl92ce_set_qos()`, `rtl92ce_enable_interrupt()`, `rtl92ce_disable_interrupt()`, `rtl92ce_card_disable()`, `rtl92ce_interrupt_recognized()`, beacon setters, `_rtl92ce_read_txpower_info_from_hwpg()`, `rtl92ce_read_eeprom_info()`, rate update helpers, `rtl92ce_gpio_radio_on_off_checking()`, `rtl92ce_set_key()`, and BT coexistence helpers.

## Control Flow
`rtl92ce_hw_init()` disables ASPM, powers and initializes MAC blocks, initializes LLT/page boundaries, downloads firmware, loads MAC/BB/RF tables, applies chip cut workarounds, configures protocol/EDCA/beacon registers, resets CAM, enables hardware security if allowed, sets MAC address, restores ASPM, initializes BT coexistence, calibrates RF if on, applies EFUSE PA-bias/voltage quirks, and starts DM. `set_hw_reg()` is the main dispatch for mac80211/rtlwifi events such as address, BSSID, slot time, aggregation, RCR, RPWM, firmware power mode, join reports, TSF correction, LPS entry/exit, and keepalive H2C commands. EEPROM read flow detects chip type, boot source, autoload status, TX-power tables, BT coexistence, and OEM behavior.

## State And Persistence
Runtime state spans `rtl_pci` register shadows (`receive_config`, `transmit_config`, `irq_mask`, beacon-control shadow, ring DMA addresses), `rtl_hal` firmware/chip/OEM fields, `rtl_phy` RF topology/calibration flags, `rtl_efuse` TX-power/regulatory/thermal tables, `rtl_ps_ctl` RF/LPS state, `rtl_mac` link/opmode/beacon fields, security key buffers, and BT coexistence settings. Hardware state includes MAC, DMA, LLT, descriptor base, interrupt, beacon, TSF, RCR/TCR, CAM, GPIO, RF power, and firmware mailbox registers. Persistent source data is read from EFUSE/EEPROM but not written.

## Dependencies And Integration Points
The file integrates rtlwifi PCI infrastructure, mac80211 state, firmware helpers, common PHY/DM code, CAM helpers, power-save helpers, EFUSE helpers, BT coexistence, and CE LED/PHY/RF/trx code through HAL ops. `sw.c` installs these functions into `rtl8192ce_hal_ops`.

## Risks And Edge Cases
Hardware initialization temporarily enables local IRQs because it can run for hundreds of milliseconds before device interrupts are enabled. LLT polling has a fixed threshold and fails probe on timeout. Firmware download failure aborts init. EEPROM autoload failure leaves defaults and may reduce calibration quality. Power-off and RF-kill paths require careful ordering around firmware self-reset, GPIO, LEDs, and `iqk_initialized`. Rate-mask logic differs by opmode, RF type, HT width, SGI, RSSI, and BT coexistence, creating many interoperability cases.

## Test Signals
Probe/init success, firmware request/download logs, chip-version log, LLT completion, descriptor DMA register programming, successful association in STA/AP/adhoc/mesh, beacon timing, RCR/BSSID filtering, interrupt delivery, RF kill toggles, LPS/IPS entry/exit, CAM key install/delete for WEP/TKIP/CCMP, rate-mask H2C commands, BT coexistence register setup, and clean card-disable/unload are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.h

## Purpose
This header declares the RTL8192CE hardware-control API consumed by `sw.c` and related modules. It also provides the channel-to-power-group helper used for EFUSE TX-power table expansion.

## Important APIs, Types, And Functions
`rtl92c_get_chnl_group()` maps 2.4 GHz channels into three regulatory power groups. Prototypes cover hardware init/disable/suspend/resume, EEPROM read, interrupt recognition and mask updates, network type, BSSID checking, QoS, beacon programming, hardware register get/set, rate-table updates, channel access, RF kill, hardware security, CAM key programming, and BT coexistence initialization.

## Control Flow
The header is declarative; `sw.c` wires these functions into `rtl8192ce_hal_ops`, and rtlwifi core calls them during probe, open/stop, config changes, security changes, and power management.

## State And Persistence
No storage is declared. Functions declared here mutate runtime driver state and hardware registers in `hw.c`. `rtl92c_get_chnl_group()` is pure and has no state.

## Dependencies And Integration Points
It depends on rtlwifi/mac80211 types and is included by CE software registration and PHY code. It binds the CE-specific hardware implementation to the generic rtlwifi HAL.

## Risks And Edge Cases
The channel grouping helper assumes channel numbering where values less than 3, less than 9, and 9 or above map to groups 0, 1, and 2; callers pass zero-based channel indexes in some loops, so off-by-one expectations must be preserved. Prototype drift breaks HAL registration at build time.

## Test Signals
Build success and HAL callbacks exercising init, interrupts, network type, beacon, rate, RF kill, security, and BT paths validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/led.c

## Purpose
This file implements software LED control for RTL8192CE. It turns LED pins on/off through `REG_LEDCFG2` and maps rtlwifi LED actions to those pin writes while respecting RF-off policy.

## Important APIs, Types, And Functions
Exports include `rtl92ce_sw_led_on()`, `rtl92ce_sw_led_off()`, and `rtl92ce_led_control()`. The internal `_rtl92ce_sw_led_control()` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, `LED_CTL_NO_LINK`, and `LED_CTL_POWER_OFF` to on/off operations. State comes from `rtlpriv->ledctl.sw_led0` and `led_opendrain`.

## Control Flow
`rtl92ce_led_control()` filters TX/RX/link/power-on actions when RF is off for reasons stronger than power save. Allowed actions call `_rtl92ce_sw_led_control()`, which selects the configured LED pin and writes the on/off pattern. LED0 off has separate open-drain and normal-drive register values.

## State And Persistence
No persistent state is written. Runtime hardware state is `REG_LEDCFG2`; driver policy state is in `rtlpriv->ledctl` and `rtl_ps_ctl`.

## Dependencies And Integration Points
It depends on `reg.h`, rtlwifi LED enums, PCI register helpers, and RF power state. `hw.c` calls LED actions during init, link/media changes, RF off, and power transitions via the HAL op installed in `sw.c`.

## Risks And Edge Cases
GPIO0 is a no-op in both on and off paths. LED behavior depends on OEM `led_opendrain` customization from EEPROM parsing. Filtering link actions during RF-off avoids misleading LEDs but can hide transient state changes.

## Test Signals
Expected LED state on module load, link/no-link, RF kill, IPS/LPS, power-off, and HP/open-drain platforms is the primary validation signal; register traces should show `REG_LEDCFG2` changes only for supported pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/led.h

## Purpose
This header declares the RTL8192CE software LED API.

## Important APIs, Types, And Functions
It declares `rtl92ce_sw_led_on()`, `rtl92ce_sw_led_off()`, and `rtl92ce_led_control()`, using rtlwifi `enum rtl_led_pin` and `enum led_ctl_mode`.

## Control Flow
The header is declarative. `sw.c` exposes `rtl92ce_led_control()` through HAL ops, and `hw.c`/rtlwifi core trigger LED actions through that callback.

## State And Persistence
No storage is declared. Implementations mutate LED configuration registers and read runtime LED/RF state.

## Dependencies And Integration Points
It is included by CE hardware, software-registration, and LED implementation files. It provides the compile-time contract for CE LED handling.

## Risks And Edge Cases
Prototype drift would break HAL op assignment or callers. The header does not document pin limitations, so callers must rely on implementation behavior for GPIO0/no-op cases.

## Test Signals
Build success and visible/register-level LED behavior during power/link transitions validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.c

## Purpose
This CE-specific PHY file adapts shared RTL8192C PHY logic to the RTL8192CE PCI device. It implements RF register locking, MAC/BB/RF table application, bandwidth callback programming, LC calibration, and RF power-state transitions.

## Important APIs, Types, And Functions
Key functions include `rtl92c_phy_query_rf_reg()`, `rtl92c_phy_mac_config()`, `rtl92c_phy_bb_config()`, `rtl92ce_phy_set_rf_reg()`, `_rtl92ce_phy_config_bb_with_headerfile()`, `_rtl92ce_phy_config_bb_with_pgheaderfile()`, `rtl92c_phy_config_rf_with_headerfile()`, `rtl92ce_phy_set_bw_mode_callback()`, `_rtl92ce_phy_lc_calibrate()`, `_rtl92ce_phy_set_rf_power_state()`, and `rtl92c_phy_set_rf_power_state()`.

## Control Flow
MAC configuration writes `RTL8192CEMAC_2T_ARRAY` byte pairs and applies a 92C/88C register tweak. BB configuration enables BB/RF clocks, powers PLL/RF blocks, sets LEDCFG, initializes common path register definitions, and delegates PHY/AGC table loading to common code. RF register access is serialized by `rf_lock` and chooses direct or deprecated firmware RF serial access based on `rtlphy->rf_mode`. Bandwidth callback programs MAC BW operation, RRSR sideband, BB RF mode, CCK/OFDM sideband registers, RF6052 bandwidth, and clears the in-progress flag. RF power transitions call IPS NIC enable/disable, RF on/sleep helpers, LED updates, and TX-ring drain waits.

## State And Persistence
State is runtime-only in `rtlphy`, `rtlpriv->locks.rf_lock`, `rtl_ps_ctl`, `rtl_mac`, and PCI TX rings. Hardware register state includes BB/RF clocks, MAC table registers, PHY/AGC tables, RF path register values, bandwidth mode, LC calibration bit, and RF on/off/sleep state.

## Dependencies And Integration Points
It depends on `table.c` arrays, `reg.h` masks, common `phy_common.c`, `rf.c` RF6052 helpers, rtlwifi PCI power-save helpers, and HAL ops from `sw.c`. It is called during `hw.c` initialization, channel-width changes, RF power changes, and calibration.

## Risks And Edge Cases
RF register access depends on correct `rf_mode`; firmware-mode helpers are stubs. `rtl92c_phy_bb_config()` has hard-coded power/clock sequencing. RF sleep waits for non-beacon TX queues but can stop after `MAX_DOZE_WAITING_TIMES_9x` even if queues remain busy. LC calibration pauses TX or modifies RF modes based on a status register and must restore state exactly.

## Test Signals
Successful BB/MAC/RF table programming, stable RF register read/write under lock, correct 20/40 MHz operation, LC calibration without stuck TX, IPS enable/disable recovery, RF sleep/on LED behavior, and no queue-drain warnings validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.h

## Purpose
This header declares the RTL8192CE PHY API and duplicates many RTL8192C common PHY constants for CE-local includes.

## Important APIs, Types, And Functions
It defines PHY command limits, IQK/APK counts, EFUSE offsets, TX-power maximums, and `RTL92C_MAX_PATH_NUM`. Prototypes include BB/RF access, MAC/BB/RF configuration, TX power, bandwidth/channel switch, IQ/AP/LC calibration, RF path switching, RF power, scan I/O control, RF serial helpers, table-loading hooks, and bandwidth callback.

## Control Flow
The header allows `hw.c`, `sw.c`, and `phy.c` to share the CE PHY function surface. `sw.c` wires many functions into HAL ops; common code calls CE table-loading and bandwidth callbacks through that HAL.

## State And Persistence
No storage is declared. Constants influence runtime state in `rtl_phy`, `rtl_efuse`, and hardware registers.

## Dependencies And Integration Points
It depends on rtlwifi/mac80211 types and overlaps with `../rtl8192c/phy_common.h`. It bridges CE-specific implementation and common RTL8192C PHY logic.

## Risks And Edge Cases
Duplication with `phy_common.h` can drift. Both headers expose a misspelled `rtl92c_phy_config_rf_with_feaderfile()` prototype. Consumers must include the correct header when they need CE-specific functions such as `_rtl92ce_phy_lc_calibrate()`.

## Test Signals
Compile coverage across `hw.c`, `phy.c`, `rf.c`, and `sw.c`, plus runtime exercise of HAL PHY callbacks, validates this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/reg.h

## Purpose
This header is the RTL8192CE/RTL8192C register and bit-field map. It names MAC, PCIe, DMA, firmware mailbox, beacon, security CAM, EFUSE, power, GPIO, RF, CCK, OFDM, TXAGC, and PHY diagnostic registers plus the masks used by the driver.

## Important APIs, Types, And Functions
The file provides register offsets such as `REG_SYS_FUNC_EN`, `REG_MCUFWDL`, `REG_LLT_INIT`, descriptor base registers, `REG_BCN_CTRL`, `REG_RCR`, `REG_CAMCMD`, `REG_SECCFG`, and PHY addresses like `RFPGA0_RFMOD`, `ROFDM0_*`, and `RTXAGC_*`. It defines link modes, rate bitmaps, CAM algorithms, interrupt masks, EEPROM offsets/defaults, receive-control bits, power/clock bits, LLT helpers, EDCA/SIFS helpers, RF register addresses, and BB mask constants.

## Control Flow
The header has no executable control flow. Driver code uses these constants to compose register writes in initialization, interrupts, beacon/media changes, TX/RX DMA setup, security CAM updates, EFUSE parsing, RF power transitions, channel/bandwidth changes, TX-power programming, and calibration.

## State And Persistence
No in-memory state is declared. The constants address mutable device hardware state and read-only persistent EFUSE/EEPROM offsets. Values written to registers persist until reset, power transition, or later writes.

## Dependencies And Integration Points
It is included by almost every CE source file and by `rtl8192c/phy_common.c`. It is the shared contract between table data, hardware code, PHY/RF code, and rtlwifi generic helpers.

## Risks And Edge Cases
Incorrect offsets or masks can corrupt unrelated device registers. Several USB-oriented definitions are present in this PCI header because it covers the broader 8192C family; callers must choose interface-appropriate registers. Many masks are magic hardware ABI values and are not type-safe. Duplicate aliases such as `RCR_APPFCS`/`APP_FCS` and overlapping beacon/TSF offsets require careful use.

## Test Signals
Build coverage is necessary but insufficient. Runtime signals include successful init/register programming, descriptor DMA operation, interrupts, EFUSE decode, security CAM operation, channel/bandwidth changes, RF calibration, rate control, and register dumps matching Realtek documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.c

## Purpose
This file implements RTL8192CE RF6052 radio configuration and TX-power programming. It handles RF bandwidth bits, CCK/OFDM TX AGC tables, EEPROM regulatory modes, dynamic high-power reductions, and RF table loading for one- and two-transmit-chain devices.

## Important APIs, Types, And Functions
Public functions are `rtl92ce_phy_rf6052_set_bandwidth()`, `rtl92ce_phy_rf6052_set_cck_txpower()`, `rtl92ce_phy_rf6052_set_ofdm_txpower()`, and `rtl92ce_phy_rf6052_config()`. Internal helpers include `rtl92c_phy_get_power_base()`, `_rtl92c_get_txpower_writeval_by_regulatory()`, `_rtl92c_write_ofdm_power_reg()`, and `_rtl92ce_phy_rf6052_config_parafile()`.

## Control Flow
Bandwidth changes update cached `rfreg_chnlval[0]` and write `RF_CHNLBW` for path A. CCK TX power builds four-byte AGC words per RF path, handles scan mode and regulatory mode 0 offsets, clamps each byte to `RF6052_MAX_TX_PWR`, then writes CCK TXAGC registers. OFDM TX power derives OFDM and MCS bases from EFUSE power, HT20/legacy differences, applies regulatory mode logic and customer limits, adjusts for BT dynamic high-power levels, clamps and writes six OFDM/MCS register groups for path A and B. RF config sets total RF paths and writes radio table arrays while toggling RFENV bits.

## State And Persistence
Runtime state includes `rtlphy->rfreg_chnlval`, `num_total_rfpath`, `current_chan_bw`, `mcs_offset`, `pwrgroup_cnt`, EFUSE power/regulatory arrays, and `rtlpriv->dm.dynamic_txhighpower_lvl`. Hardware state includes RF_CHNLBW, RFENV, radio registers, and TXAGC BB registers.

## Dependencies And Integration Points
It depends on `reg.h`, `def.h`, `phy.h`, `rf.h`, `dm.h`, and `table.c` RF arrays through `rtl92c_phy_config_rf_with_headerfile()`. Common PHY TX-power and channel paths call these functions through HAL ops.

## Risks And Edge Cases
Regulatory mode math is complex and byte-packed; signed differences are represented in small fields from EFUSE. Dynamic BT reductions subtract packed byte values and can underflow before clamp logic if not considered. Bandwidth programming only writes path A cached channel value. 1T devices use a dummy one-entry path-B array.

## Test Signals
Validate RF table load on 1T/2T devices, TX power per CCK/OFDM/MCS rate, regulatory modes 0-3, scan-mode power behavior, BT high-power reductions, 20/40 MHz bandwidth changes, and no TXAGC byte above `0x3f`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.h

## Purpose
This header declares the RTL8192CE RF6052 radio helper interface and RF power/path limits.

## Important APIs, Types, And Functions
It defines `RF6052_MAX_TX_PWR` as `0x3f`, `RF6052_MAX_PATH` as `2`, and declares `rtl92ce_phy_rf6052_set_bandwidth()`, `rtl92ce_phy_rf6052_set_cck_txpower()`, `rtl92ce_phy_rf6052_set_ofdm_txpower()`, and `rtl92ce_phy_rf6052_config()`.

## Control Flow
The header is declarative. Common PHY code calls the declared functions through HAL ops while CE PHY initialization and RF configuration use them directly.

## State And Persistence
No storage is declared. Constants constrain runtime TXAGC writes and RF path iteration.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw` and is included by CE PHY, RF, SW, and HW-related files. It is part of the CE HAL RF contract.

## Risks And Edge Cases
The maximum TX power is a packed byte limit used by CCK and OFDM paths; changes would affect regulatory behavior. `RF6052_MAX_PATH` assumes at most two paths for this driver.

## Test Signals
Build coverage and runtime RF6052 configuration, TX-power, and bandwidth tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/sw.c

## Purpose
This is the RTL8192CE PCI driver registration and HAL-configuration file. It initializes software variables, requests firmware, defines module parameters, maps CE hardware operations into rtlwifi HAL ops, publishes register map constants, declares PCI IDs, and registers the PCI driver.

## Important APIs, Types, And Functions
Important functions and data include `rtl92c_init_aspm_vars()`, `rtl92c_init_sw_vars()`, `rtl92c_deinit_sw_vars()`, `rtl8192ce_hal_ops`, `rtl92ce_mod_params`, `rtl92ce_hal_cfg`, `rtl92ce_pci_ids`, `rtlwifi_pm_ops`, and `rtl92ce_driver`. Module metadata names three firmware files and parameters `swenc`, `ips`, `swlps`, `fwlps`, `aspm`, `debug_level`, and `debug_mask`.

## Control Flow
PCI probe from rtlwifi receives `rtl92ce_hal_cfg` via the device table. Software init sets BT registry defaults, DM defaults, TX/RX configs, band/mode, interrupt masks, power-save defaults, ASPM constants, allocates a 16 KiB firmware buffer, chooses firmware by chip version, and starts asynchronous firmware request. HAL ops then route rtlwifi core calls to CE-specific implementations in `hw.c`, `phy.c`, `rf.c`, `dm.c`, `led.c`, and `trx.c`.

## State And Persistence
Runtime state initialized here includes `rtlpriv->dm`, `rtlpci->transmit_config`, `receive_config`, `irq_mask`, `rtlhal` band/macphy mode, `rtl_ps_ctl` power-save knobs, ASPM policy, and `rtlhal.pfirmware`. Module parameters are read at load time but no persistent configuration is written.

## Dependencies And Integration Points
It depends on Linux module/PCI firmware APIs, rtlwifi core and PCI glue, CE hardware/PHY/RF/DM/LED/TRX modules, and common RTL8192C firmware/PHY helpers. `module_pci_driver()` binds the driver to PCI device IDs 0x8191, 0x8178, 0x8177, and 0x8176.

## Risks And Edge Cases
Firmware selection depends on chip version already being read before software init uses it; probe ordering must preserve that assumption. Asynchronous firmware request failure frees the firmware buffer and fails init. The HAL map table must stay synchronized with `reg.h` and rtlwifi generic map indices. Module parameters change power/security behavior and can hide hardware crypto or power-save bugs.

## Test Signals
Successful module load, firmware request callback, correct firmware filename, PCI ID binding, module parameter effects, HAL callbacks invoked by rtlwifi core, suspend/resume through `rtl_pci_suspend/resume`, and clean deinit freeing firmware are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/table.c

## Purpose
This file contains the static Realtek-provided MAC, baseband, RF, power-group, and AGC initialization tables for RTL8192CE. Runtime code iterates these arrays to program the device during MAC/BB/RF initialization and TX-power offset setup.

## Important APIs, Types, And Functions
Exported data arrays are `RTL8192CEPHY_REG_2TARRAY`, `RTL8192CEPHY_REG_1TARRAY`, `RTL8192CEPHY_REG_ARRAY_PG`, `RTL8192CERADIOA_2TARRAY`, `RTL8192CE_RADIOB_2TARRAY`, `RTL8192CE_RADIOA_1TARRAY`, `RTL8192CE_RADIOB_1TARRAY`, `RTL8192CEMAC_2T_ARRAY`, `RTL8192CEAGCTAB_2TARRAY`, and `RTL8192CEAGCTAB_1TARRAY`.

## Control Flow
There is no executable control flow. `phy.c` selects 1T or 2T PHY and AGC arrays based on chip version, applies MAC byte pairs from `RTL8192CEMAC_2T_ARRAY`, applies PHY/AGC address-value pairs with small delays, loads RF path arrays through RF register writes, and passes `RTL8192CEPHY_REG_ARRAY_PG` triples to `_rtl92c_store_pwrindex_diffrate_offset()`.

## State And Persistence
The arrays are static module data. They are not modified by this file. Applying them mutates hardware MAC/BB/RF registers and runtime MCS offset caches in common PHY code.

## Dependencies And Integration Points
It includes `table.h` for lengths and declarations. Consumers are `phy.c`, `rf.c`, and common PHY TX-power offset code. Values are tightly coupled to `reg.h` addresses and chip RF topology.

## Risks And Edge Cases
Array lengths must match the actual initializer counts and the consumer step size: MAC/PHY/RF/AGC arrays are address-value pairs, while PG arrays are address-mask-value triples. A wrong length or value can misprogram RF/BB analog behavior. The 1T path-B radio array has length 1 and contains only `0x0`, so callers must avoid treating it as normal address-value pairs beyond the configured RF path count.

## Test Signals
Successful BB/RF init on 1T and 2T hardware, stable AGC/sensitivity, expected TX power offsets, no out-of-bounds table iteration, and register dumps matching vendor tables validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/table.h

## Purpose
This header declares the RTL8192CE static initialization tables and their expected lengths.

## Important APIs, Types, And Functions
It defines lengths for PHY 2T/1T arrays, PHY power-group triples, RF path A/B arrays for 2T/1T, MAC table, and AGC 2T/1T arrays. It declares the corresponding `u32` arrays exported by `table.c`.

## Control Flow
The header is declarative. Consumers use the length macros to iterate arrays in fixed strides during initialization.

## State And Persistence
No mutable state is declared here. The extern arrays are module data in `table.c` and ultimately program hardware registers when consumed.

## Dependencies And Integration Points
It includes `<linux/types.h>` for `u32` and is included by `table.c` and `phy.c`. It binds vendor table data to CE PHY initialization code.

## Risks And Edge Cases
Length macros are trusted by consumers; any mismatch with the actual arrays can cause missed register writes or out-of-bounds reads. The header guard name has an unusual double underscore/H suffix but is consistent within the file.

## Test Signals
Compile-time array declarations, successful table iteration in `phy.c`, and hardware initialization without table bounds issues validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/table.h -->
