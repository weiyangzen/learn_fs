# subset-b-004892 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.c

Purpose: `hw.c` is the main RTL8723AE hardware-control implementation. It bridges rtlwifi/mac80211 operations to register writes, firmware commands, EFUSE-derived configuration, PCI descriptor base setup, interrupt control, security CAM programming, beacon behavior, RF-kill checking, rate adaptation commands, and Bluetooth coexistence setup.

Important APIs/functions: exported entry points include `rtl8723e_hw_init`, `rtl8723e_card_disable`, `rtl8723e_get_hw_reg`, `rtl8723e_set_hw_reg`, `rtl8723e_read_eeprom_info`, interrupt enable/disable/update helpers, beacon setters, `rtl8723e_set_network_type`, `rtl8723e_set_check_bssid`, `rtl8723e_update_hal_rate_tbl`, `rtl8723e_gpio_radio_on_off_checking`, `rtl8723e_enable_hw_security_config`, `rtl8723e_set_key`, and BT helpers. Internal helpers include beacon-control bit manipulation, LLT programming, MAC initialization, chip-version decoding, EFUSE tx-power parsing, media-status selection, and rate-table/rate-mask construction.

Control flow: `rtl8723e_hw_init` marks initialization active, temporarily enables local IRQs, disables ASPM, runs `_rtl8712e_init_mac`, downloads firmware, configures MAC/BB/RF tables, patches RF registers for chip cuts, caches RF channel words, enables BB CCK/OFDM, programs MAC defaults, resets CAM, enables hardware security, sets MAC address, restores ASPM, initializes BT hardware, performs IQK/LC calibration, applies EFUSE PA-bias adjustments, and starts dynamic management. `_rtl8712e_init_mac` parses the PCI power-on sequence, configures ePHY, initializes LLT and packet-buffer boundaries when needed, clears interrupt status, writes DMA ring base addresses, and refreshes LEDs. Shutdown flows through `rtl8723e_card_disable` into `_rtl8723e_poweroff_adapter`, which enters LPS/RF-off flow, self-resets firmware when loaded, resets MCU state, parses card-disable flow, and locks power-control registers.

State and persistence: persistent driver state is in `rtlpriv`, `rtlhal`, `rtlphy`, `rtlpci`, `rtlefuse`, `mac`, and `ppsc`. The file caches `rtlpci->receive_config`, interrupt masks, beacon-control shadow `reg_bcn_ctrl_val`, EFUSE tx-power arrays, OEM ID, BT coexistence fields, firmware-ready state, power-save flags, RF power state, CAM key buffers, and IQK initialization state. Hardware state is persisted in device registers such as RCR, CR, MSR, TSF, CAM, EDCA, beacon, interrupt-mask/status, and descriptor-base registers.

Dependencies/integration: depends on rtlwifi common layers (`wifi.h`, `base.h`, `pci.h`, `cam.h`, `ps.h`, `efuse.h`), RTL8723 common PHY/FW/DM helpers, `pwrseqcmd` plus this directory's `pwrseq.h`, LED control, firmware H2C helpers, and BT coexistence. `sw.c` publishes these functions through `rtl8723e_hal_ops`; mac80211 calls arrive through rtlwifi core/pci glue.

Risks: many paths rely on magic register values and chip-cut conditionals with limited validation. EFUSE autoload failure silently falls back to defaults that affect tx power, thermal handling, regulatory behavior, and BT settings. `rtl8723e_bt_reg_init` writes `reg_bt_sco` twice and never persists a distinct ISO field after the first assignment, which looks suspicious. Rate-mask construction is sensitive to station private state, RF type, RSSI level, BT state, and short-GI flags. CAM programming depends on key-buffer length as the add/delete signal. IRQs are deliberately enabled during long initialization, so ordering around `being_init_adapter`, disabled device interrupts, and shared state locks is important. Several suspend/resume hooks are empty.

Test signals: boot/probe with both firmware names, MAC/BB/RF init logs, successful firmware ready, valid interrupts after enabling, association in STA/AP/adhoc modes, beacon timing, hardware encryption for WEP/TKIP/CCMP, RF-kill GPIO toggles, IPS/LPS transitions, BT coexistence initialization, and throughput stability after RCR updates. Regression tests should include EFUSE autoload-fail emulation, CAM clear/add/delete paths, rate-mask H2C command generation, and card-disable/re-enable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.h

Purpose: `hw.h` is the public local interface for RTL8723AE hardware operations implemented in `hw.c`. It exposes lifecycle, register, interrupt, beacon, media, rate, security, RF-kill, Bluetooth coexistence, and suspend/resume functions to `sw.c` and adjacent driver modules.

Important APIs/types: prototypes include `rtl8723e_hw_init`, `rtl8723e_card_disable`, `rtl8723e_read_eeprom_info`, `rtl8723e_get_hw_reg`, `rtl8723e_set_hw_reg`, `rtl8723e_interrupt_recognized`, `rtl8723e_enable_interrupt`, `rtl8723e_disable_interrupt`, `rtl8723e_update_interrupt_mask`, network/beacon/QoS setters, rate-table update, `rtl8723e_gpio_radio_on_off_checking`, hardware security and key programming, BT coexistence readers/initializers, and empty suspend/resume hooks. `CHK_SVID_SMID` is a convenience macro for matching EFUSE subsystem IDs in contexts where `rtlefuse` is in scope.

Control flow: the header does not execute logic; it defines the call surface that `rtl_hal_ops` binds into rtlwifi. Hardware initialization and disable run through these APIs, and runtime operations such as scan, association, encryption, and interrupt handling call back into the prototypes.

State and persistence: no state is defined here, but the signatures show the shared state carriers: `struct ieee80211_hw`, `struct rtl_int`, `struct ieee80211_sta`, `enum nl80211_iftype`, and key material parameters. Implementations mutate `rtlpriv`-attached persistent driver and hardware register state.

Dependencies/integration: requires prior inclusion of rtlwifi/mac80211 types. The header is consumed by `sw.c`, `hw.c`, and modules needing hardware hooks. Its function set mirrors `struct rtl_hal_ops` fields in `sw.c`.

Risks: declarations must stay synchronized with `hw.c` and with rtlwifi operation signatures. The `CHK_SVID_SMID` macro depends on an implicit local variable name and can be fragile if reused outside the intended scope. Suspend/resume declarations exist despite no-op implementation.

Test signals: compile coverage is the primary signal. Any rtlwifi API signature changes should fail at build time. Runtime coverage comes from successful probe, suspend/resume callbacks, association, interrupt handling, and encryption operations routed through these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.c

Purpose: `led.c` implements software LED control for RTL8723AE pins. It maps generic rtlwifi LED actions onto chip LED configuration registers while respecting RF power-off reasons.

Important APIs/functions: `rtl8723e_sw_led_on` and `rtl8723e_sw_led_off` directly program LED pins `LED_PIN_LED0` and `LED_PIN_LED1`; `LED_PIN_GPIO0` is accepted but does nothing. `rtl8723e_led_control` is the public operation used by `rtl_hal_ops`. `_rtl8723e_sw_led_control` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to LED on, and `LED_CTL_POWER_OFF` to LED off.

Control flow: LED actions enter `rtl8723e_led_control`, which first suppresses activity/link/power-on LED updates when the RF-off reason is stronger than power-save. Allowed actions pass to `_rtl8723e_sw_led_control`, which selects `rtlpriv->ledctl.sw_led0` and calls the on/off helper. The helpers read and write `REG_LEDCFG2`, `REG_LEDCFG1`, and, for open-drain LED0 off, `REG_MAC_PINMUX_CFG`.

State and persistence: persistent state is `rtlpriv->ledctl.sw_led0` and `rtlpriv->ledctl.led_opendrain`, initialized/customized elsewhere. Hardware-visible state is the LED register bits, which persist until later writes or power transitions.

Dependencies/integration: uses rtlwifi register I/O from `wifi.h`, PCI-private state from `pci.h`, register constants from `reg.h`, and LED enums from common rtlwifi definitions. Called by `hw.c` during init, card disable, media changes, and RF power transitions; published by `sw.c`.

Risks: GPIO0 is silently unimplemented. LED behavior depends on the open-drain flag derived from OEM customization, so incorrect EFUSE/OEM parsing can invert or disable expected LED behavior. The RF-off guard suppresses many user-visible state changes, which is correct for hard-off states but can hide link changes during edge power transitions.

Test signals: validate LED state on probe, link, no-link, RF off, and power-off for both open-drain and non-open-drain configurations. Confirm no register errors when `sw_led0` is GPIO0 or LED1. Inspect debug logs under `COMP_LED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.h

Purpose: `led.h` declares the RTL8723AE software LED operations used by the hardware layer and operation table.

Important APIs/types: the header exposes `rtl8723e_sw_led_on`, `rtl8723e_sw_led_off`, and `rtl8723e_led_control`, parameterized by `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode`.

Control flow: no executable flow; it is a declaration boundary between `led.c`, `hw.c`, and `sw.c`.

State and persistence: no state is declared. Implementations use `rtlpriv->ledctl` and device LED registers.

Dependencies/integration: relies on prior inclusion of rtlwifi/mac80211 types. `sw.c` assigns `rtl8723e_led_control` to `.led_control`; `hw.c` calls the low-level on/off helpers during LED refresh.

Risks: include guard name says `RTL92CE`, not `RTL8723E`, which is harmless functionally but can confuse maintenance. Prototype drift would break builds.

Test signals: compile coverage plus runtime LED state transitions through the HAL operation table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.c

Purpose: `phy.c` controls RTL8723AE PHY and RF programming above the RF6052-specific power helpers. It implements RF register access, MAC/BB/RF table loading, tx-power index management, channel and bandwidth switching, scan-time DIG backup/restore, IQ/LC calibration, antenna path switching, and RF power-state transitions.

Important APIs/functions: exported functions include `rtl8723e_phy_query_rf_reg`, `rtl8723e_phy_set_rf_reg`, `rtl8723e_phy_mac_config`, `rtl8723e_phy_bb_config`, `rtl8723e_phy_rf_config`, `rtl8723e_phy_config_rf_with_headerfile`, tx-power getters/setters, `rtl8723e_phy_scan_operation_backup`, bandwidth/channel switch callbacks, `rtl8723e_phy_iq_calibrate`, `rtl8723e_phy_lc_calibrate`, `rtl8723e_phy_set_rfpath_switch`, `rtl8723e_phy_set_io_cmd`, and `rtl8723e_phy_set_rf_power_state`. Internal helpers load table arrays, store power-index offsets, sequence channel-change commands, run IQK trials, and enter RF sleep.

Control flow: hardware initialization calls MAC config, BB config, and RF config. BB config enables PLL/BB clocks and applies PHY and AGC table arrays; PG table entries are captured into `mcs_txpwrlevel_origoffset` rather than directly written. Channel switch builds pre, RF-dependent, and post command arrays, sets tx power, writes RF `RF_CHNLBW`, and applies UMC B-cut special settings. Bandwidth switch updates MAC BW registers, RRSR sideband, BB RF mode bits, CCK/OFDM sideband, analog parameters, and RF bandwidth. IQ calibration runs up to three trials, compares result similarity, fills the IQK matrix, and backs up calibration registers for recovery. RF power state transitions enable NIC from halted IPS, turn RF on, disable NIC or LEDs for off, or wait for TX queues before RF sleep.

State and persistence: mutates `rtlpriv->phy` fields such as `rf_mode`, `rf_type`, `num_total_rfpath`, `rfreg_chnlval`, `current_channel`, `current_chan_bw`, `set_bwmode_inprogress`, `sw_chnl_inprogress`, `sw_chnl_stage`, `sw_chnl_step`, `cur_cck_txpwridx`, `cur_ofdm24g_txpwridx`, power-group offsets, IQK backups/results, default gains, and scan initial-gain backup. It also updates `rtlpriv->psc` RF power state and sleep/awake timestamps. Register writes persist PHY, RF, MAC, and power state until reprogrammed.

Dependencies/integration: depends on common rtl8723 PHY helpers for serial RF read/write, BB register access, calibration save/restore, PI mode, IQ matrix fill, and command-array construction. Uses `table.c` arrays, `rf.c` tx-power/bandwidth functions, DM DIG helpers, PCI queue state, rtlwifi power-save helpers, and `hw.c` via `HW_VAR_IO_CMD`.

Risks: RF register access is guarded by `rf_lock`, but higher-level state flags rely on ordering rather than broad locking. `_rtl8723e_phy_fw_rf_serial_write` is deprecated and only warns, so `RF_OP_BY_FW` writes effectively do not program RF. The `RT_CANNOT_IO(hw)` macro is hardcoded false. Channel support warns for channel >14, consistent with 2.4 GHz only. RF sleep waits on TX queues with a bounded loop, so busy queues can still force sleep after warnings. Calibration code is magic-register heavy and sensitive to chip cuts and RF type.

Test signals: successful MAC/BB/RF config during probe, RF register read/write sanity, channel 1-14 switching, 20/40 MHz transitions, tx-power updates from EFUSE and dBm override, scan pause/restore DIG behavior, IQK recovery after card re-enable, LC calibration, IPS/LPS RF on/off/sleep transitions, and queue-drain warnings under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.h

Purpose: `phy.h` defines RTL8723AE PHY constants, small data structures, enums, and exported PHY/RF-control prototypes.

Important APIs/types: constants size channel-switch command arrays, IQK backup arrays, RF path count, tx-power maxima, EFUSE offsets, and calibration tolerance. Enums describe hardware register blocks, baseband config types, rate-adaptive offset areas, and antenna-path bit combinations. Structs describe antenna selection bitfields, a compact EFUSE content layout, and `tx_power_struct` for per-path/channel power indexes and MCS offsets. Prototypes expose RF register access, MAC/BB/RF config, tx-power management, scan backup, bandwidth/channel switching, IQ/LC calibration, RF path switch, IO command handling, and RF power-state changes.

Control flow: no executable flow, but constants and prototypes directly shape `phy.c` control paths. `MAX_PRECMD_CNT`, `MAX_RFDEPENDCMD_CNT`, and `MAX_POSTCMD_CNT` bound channel command arrays; IQK constants bound calibration backup and retry behavior.

State and persistence: the structures describe state later embedded in rtlwifi private structures or used as temporary views. The header itself persists no data.

Dependencies/integration: consumed by `phy.c`, `rf.c`, `hw.c`, `trx.c`, and `sw.c`. It relies on rtlwifi/mac80211 types and shared enums such as `enum radio_path`, `enum io_type`, and `enum rf_pwrstate`.

Risks: there are duplicate definitions of `IQK_ADDA_REG_NUM` and `IQK_DELAY_TIME`, and the prototype `rtl92c_phy_config_rf_with_feaderfile` appears misspelled and is not the implemented `rtl8723e_phy_config_rf_with_headerfile`. `RT_CANNOT_IO(hw)` is defined as `false`, so sleep/unload I/O protection is effectively disabled for this driver slice. EFUSE offset constants overlap with `reg.h` definitions and must stay consistent.

Test signals: compile checks for prototype consistency, channel-switch array bounds, IQK backup sizing, and tx-power structures. Runtime signals come through all `phy.c` paths that use these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.c

Purpose: `pwrseq.c` materializes RTL8723A power-transition macros from `pwrseq.h` into `struct wlan_pwr_cfg` arrays consumed by the common rtlwifi power-sequence parser.

Important APIs/data: exported arrays are `rtl8723A_power_on_flow`, `rtl8723A_radio_off_flow`, `rtl8723A_card_disable_flow`, `rtl8723A_card_enable_flow`, `rtl8723A_suspend_flow`, `rtl8723A_resume_flow`, `rtl8723A_hwpdn_flow`, `rtl8723A_enter_lps_flow`, and `rtl8723A_leave_lps_flow`.

Control flow: no functions execute here. Runtime control flow occurs when callers pass these arrays to `rtl_hal_pwrseqcmdparsing`, mainly in MAC init, poweroff, LPS entry/leave, and card enable/disable paths. Each array concatenates transition macros and terminates with `RTL8723A_TRANS_END`.

State and persistence: the arrays are static driver data. They encode register offsets, interface masks, command types, bit masks, values, polling waits, and delays. Hardware persistence is produced by the parser writing the encoded registers.

Dependencies/integration: depends on `pwrseqcmd.h` for `struct wlan_pwr_cfg`, masks, base addresses, and command constants, and on `pwrseq.h` macro definitions. Used by `hw.c` through the `RTL8723_NIC_*_FLOW` aliases.

Risks: array length declarations must match the number of macro entries. Several arrays use historical step-count names that are larger than actual macro entries, which is safe for initializer capacity but can hide stale documentation. A wrong command or missing `TRANS_END` would break probe, shutdown, suspend, or LPS.

Test signals: successful power-on during probe, RF-off/card-disable without hangs, LPS entry/leave, suspend/resume parser behavior if wired, and absence of power-sequence polling timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.h

Purpose: `pwrseq.h` defines the RTL8723A hardware power-state transition scripts and aliases them to RTL8723 NIC flow names for PCIe use.

Important APIs/data: it documents hardware states POFF, PDN, CARDEMU, ACT, LPS, and SUS. Transition macros encode CARDEMU-to-ACT, ACT-to-CARDEMU, CARDEMU-to-SUS, SUS-to-CARDEMU, card-disable/card-enable, CARDEMU-to-PDN, PDN-to-CARDEMU, ACT-to-LPS, LPS-to-ACT, and `TRANS_END`. It declares all arrays defined in `pwrseq.c` and aliases them as `RTL8723_NIC_PWR_ON_FLOW`, `RTL8723_NIC_RF_OFF_FLOW`, `RTL8723_NIC_DISABLE_FLOW`, `RTL8723_NIC_ENABLE_FLOW`, `RTL8723_NIC_SUSPEND_FLOW`, `RTL8723_NIC_RESUME_FLOW`, `RTL8723_NIC_PDN_FLOW`, `RTL8723_NIC_LPS_ENTER_FLOW`, and `RTL8723_NIC_LPS_LEAVE_FLOW`.

Control flow: the macros are interpreted by `rtl_hal_pwrseqcmdparsing`. Commands perform writes, polling, and delays across MAC, SDIO, USB, and PCI interface masks, though this driver uses the PCI path. LPS entry stops PCIe DMA, pauses TX, polls TX-empty counters, gates BB/MAC clocks, resets MAC TRX, and responds TxOK. LPS leave writes RPWM, delays, switches TSF clocking, enables BB clock and WMAC TRX, and clears TX pause.

State and persistence: state is encoded as immutable command data. Executing it changes hardware power, clock, reset, DMA, TX pause, suspend, and RPWM registers.

Dependencies/integration: includes common `pwrseqcmd.h` and is used by `pwrseq.c` and `hw.c`. Interface masks allow shared definitions across PCI/USB/SDIO, even where this driver is PCI.

Risks: register offsets and bit meanings are hardware-specific and hard to validate statically. Typos in comments and transition names are harmless, but an incorrect command can cause probe or power-save hangs. The card-enable array declaration size references ACT-to-CARDEMU and CARDEMU-to-PDN step counts even though the initializer uses CARDDIS-to-CARDEMU plus CARDEMU-to-ACT, so maintainers should verify capacity if editing.

Test signals: power sequencing should be validated through repeated probe/remove, IPS/LPS cycles, hardware RF-kill, suspend/resume where applicable, and logs from power-sequence polling failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/reg.h

Purpose: `reg.h` is the RTL8723AE register and bitfield map. It names MAC, PCIe, USB, EFUSE, CAM, interrupt, beacon, DMA, PHY, BB, RF, rate, power, and security registers and masks used throughout the driver.

Important APIs/data: definitions include register offsets (`REG_SYS_FUNC_EN`, `REG_CR`, `REG_RCR`, `REG_PCIE_CTRL_REG`, `REG_BCN_CTRL`, `REG_CAMCMD`, `REG_SECCFG`, `RFPGA0_RFMOD`, `RTXAGC_*`, `RF_CHNLBW`), alias names (`MSR`, `ISR`, `TSFR`), rate bitmaps (`RATR_*`, `RATE_*`, `RATE_ALL_*`), interrupt masks (`IMR_*`, `PHIMR_*`), EFUSE size/default/offset constants, receive-config bits (`RCR_*`), security CAM/SCR bits, LLT helpers, power/clock/function bits, BB/RF masks, and common masks such as `MASKDWORD`, `MASKBYTE*`, and `RFREG_OFFSET_MASK`.

Control flow: no code executes here. Control-flow impact is indirect: `hw.c`, `phy.c`, `rf.c`, `trx.c`, `led.c`, `sw.c`, and power-sequence macros use these constants to decide which hardware bits to read, write, poll, or preserve.

State and persistence: the header defines symbolic addresses for persistent device register state. It does not store driver state. Values written through these definitions persist in hardware until reset or subsequent writes.

Dependencies/integration: included by nearly every RTL8723AE source file. `sw.c` maps many constants into the generic `rtl_hal_cfg.maps` table so common rtlwifi code can access chip-specific addresses and bit encodings.

Risks: duplicated definitions appear for some USB registers and defaults, and several names are inherited from older 8192/92S/92C code. Incorrect constants can produce silent hardware misprogramming. The file mixes PCIe-specific and USB/SDIO definitions, so maintainers must watch interface masks and call sites. Magic values in source files often rely on these symbolic definitions being exact.

Test signals: compile coverage catches missing names but not incorrect values. Runtime signals include successful EFUSE reads, firmware download, MAC/BB/RF init, interrupt delivery, RX/TX descriptors, CAM encryption, beacon timing, RF power transitions, and stable tx power/rate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.c

Purpose: `rf.c` implements RF6052-specific RF bandwidth setup, CCK/OFDM transmit-power programming, regulatory power-offset application, and RF path configuration for RTL8723AE.

Important APIs/functions: exported functions are `rtl8723e_phy_rf6052_set_bandwidth`, `rtl8723e_phy_rf6052_set_cck_txpower`, `rtl8723e_phy_rf6052_set_ofdm_txpower`, and `rtl8723e_phy_rf6052_config`. Internal helpers compute OFDM/MCS power bases, calculate per-register write values under regulatory mode, clamp and write OFDM power registers, and load RF table data via `_rtl8723e_phy_rf6052_config_parafile`.

Control flow: bandwidth setup updates cached `rtlphy->rfreg_chnlval[0]` and writes RF `RF_CHNLBW`. CCK power expands per-path power indexes into per-rate AGC words, handles scan mode and regulatory mode, adds original offsets for regulatory mode 0, clamps to `RF6052_MAX_TX_PWR`, and writes CCK AGC registers. OFDM power computes legacy and MCS bases, applies one of four regulatory modes plus dynamic BT high-power reductions, then writes six OFDM/MCS register groups per path. RF config sets total RF path count from RF type, toggles RF environment bits on BB interfaces, applies the RF header table for each active path, and restores RF environment bits.

State and persistence: uses `rtlphy->rfreg_chnlval`, `rtlphy->current_chan_bw`, `rtlphy->rf_type`, `rtlphy->num_total_rfpath`, `rtlphy->mcs_txpwrlevel_origoffset`, `rtlefuse` tx-power/regulatory/group arrays, and `rtlpriv->dm.dynamic_txhighpower_lvl`. Hardware persistence is BB TX AGC registers and RF path registers.

Dependencies/integration: called by `phy.c` during RF config, bandwidth switching, and tx-power updates. Uses `reg.h` register/mask definitions, `def.h` RF path/rate constants, and `table.c` RF arrays through `rtl8723e_phy_config_rf_with_headerfile`.

Risks: tx-power arithmetic subtracts BT dynamic reductions from unsigned values before final clamping, so underflow must be considered when changing logic. Regulatory modes are magic-number driven. Path B calculations exist even for 1T1R, but actual active path count is limited during config. Power table offsets must be initialized by PHY PG-table parsing before runtime power updates.

Test signals: tx-power register dumps for channels 1, 6, 11/13, 20 and 40 MHz, scan vs non-scan mode, regulatory modes 0-3, BT high-power levels, RF_1T1R config, and bandwidth changes. Confirm no power values exceed `0x3f` after writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.h

Purpose: `rf.h` declares the RF6052 helper interface used by `phy.c`.

Important APIs/types: defines `RF6052_MAX_TX_PWR` as `0x3F` and declares bandwidth, CCK tx-power, OFDM tx-power, and RF config functions.

Control flow: no executable flow; it is a boundary for RF helper calls from PHY routines.

State and persistence: no local state. Implementations mutate PHY cached RF words and hardware RF/BB power registers.

Dependencies/integration: requires `struct ieee80211_hw` and integer types from surrounding includes. `phy.c` consumes the API; `rf.c` implements it.

Risks: `RF6052_MAX_TX_PWR` must match chip limits. Prototype drift breaks builds. The API accepts raw `u8 *ppowerlevel` arrays and channel numbers without size/range enforcement at the header boundary.

Test signals: compile coverage and runtime tx-power/bandwidth tests through `phy.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/sw.c

Purpose: `sw.c` is the module registration and software-configuration entry point for the RTL8723AE PCI driver. It initializes software variables, requests firmware, defines the HAL operation table, maps chip constants into common rtlwifi configuration, declares PCI IDs, exposes module parameters, and registers the PCI driver.

Important APIs/functions/data: `rtl8723e_init_sw_vars` initializes BT coexistence ops, DM defaults, transmit/receive config, IRQ masks, power-save policy, MSI/ASPM settings, firmware buffer, and async firmware request. `rtl8723e_deinit_sw_vars` frees firmware memory. `rtl8723e_get_btc_status` always enables BT coexistence support. `is_fw_header` checks firmware signature. `rtl8723e_hal_ops`, `rtl8723e_mod_params`, `rtl8723e_hal_cfg`, `rtl8723e_pci_ids`, and `rtl8723e_driver` bind the driver to rtlwifi and PCI.

Control flow: PCI probe from `module_pci_driver` uses `rtl_pci_probe`, which receives `rtl8723e_hal_cfg` from the device ID. rtlwifi calls `.init_sw_vars`, later `.read_eeprom_info` determines chip version, and firmware is requested asynchronously using either `rtlwifi/rtl8723fw.bin` or `_B.bin` for UMC B-cut. All runtime hardware operations dispatch through `rtl8723e_hal_ops`.

State and persistence: initializes persistent rtlwifi private state: DM flags, band type, MAC/PHY mode, RCR/TCR shadows, IRQ masks, IPS/LPS settings, ASPM constants, firmware buffer pointer/size, module parameters, and BT ops. Module parameters persist for the module lifetime. Firmware memory is vmalloc-backed and freed at deinit.

Dependencies/integration: integrates Linux module/PCI/firmware APIs with rtlwifi core and PCI glue. Depends on local hardware, PHY, TRX, LED, DM, FW, table, BT coexistence, and common rtl8723 modules. `rtl_hal_cfg.maps` bridges chip-specific constants from `reg.h` to generic rtlwifi code.

Risks: firmware selection depends on `rtlhal->version`, but `init_sw_vars` may run before chip version is fully known depending on rtlwifi probe ordering. If async firmware request fails, init returns failure after freeing the buffer. `get_btc_status` returning true forces BT coexistence path availability. The configuration is 2.4 GHz only despite some generic 5 GHz code paths elsewhere. Operation-table mismatches are high blast radius.

Test signals: module load/unload, PCI ID match for `10ec:8723`, successful async firmware load for both firmware names, module parameters affecting power save/MSI/ASPM/debug behavior, HAL operation dispatch during association and traffic, and no firmware-buffer leaks on request failure or unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.c

Purpose: `table.c` contains the static register-programming tables for RTL8723AE MAC, PHY, PHY power-group offsets, RF path A, and AGC setup.

Important APIs/data: exported arrays are `RTL8723EPHY_REG_1TARRAY`, `RTL8723EPHY_REG_ARRAY_PG`, `RTL8723E_RADIOA_1TARRAY`, `RTL8723EMAC_ARRAY`, and `RTL8723EAGCTAB_1TARRAY`. The arrays are sized by constants in `table.h` and consumed by `phy.c`.

Control flow: no functions execute here. `phy.c` iterates arrays as address/value pairs for MAC, PHY, AGC, and RF tables; the PG array is interpreted as address/mask/data triples used to populate tx-power offset state. Special sentinel addresses such as `0xfe` through `0xf9` in PHY/RF arrays encode millisecond or microsecond delays in the loader.

State and persistence: data is static and read-only by convention, though not declared `const`. Loading these tables persists values into MAC, BB, RF, AGC, and power-index state. PG table data persists in `rtlphy->mcs_txpwrlevel_origoffset`.

Dependencies/integration: included through `table.h`; used by `rtl8723e_phy_mac_config`, `_rtl8723e_phy_config_bb_with_headerfile`, `_rtl8723e_phy_config_bb_with_pgheaderfile`, and `rtl8723e_phy_config_rf_with_headerfile`.

Risks: table corruption or length mismatch can misprogram hardware with little diagnostic context. Arrays are writable globals, which increases accidental mutation risk. Values are magic vendor calibration data and are hard to review semantically. Delay sentinels depend on loader logic skipping normal register writes for those entries.

Test signals: successful BB/RF/MAC initialization, no table overrun under KASAN/UBSAN, expected delay handling, register dumps matching vendor baseline, association stability, RX sensitivity, tx power, and calibration behavior after table load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.h

Purpose: `table.h` declares the static RTL8723AE register table arrays and their lengths.

Important APIs/data: length constants cover PHY 1T, PHY PG, Radio A 1T, MAC, and AGC tables. Extern declarations expose `RTL8723EPHY_REG_1TARRAY`, `RTL8723EPHY_REG_ARRAY_PG`, `RTL8723E_RADIOA_1TARRAY`, `RTL8723EMAC_ARRAY`, and `RTL8723EAGCTAB_1TARRAY`.

Control flow: no executable flow. The lengths drive loops in `phy.c` that step by 2 for address/value arrays and by 3 for PG address/mask/data arrays.

State and persistence: no state is stored in the header. The declared arrays represent immutable configuration data, though the declarations are not `const`.

Dependencies/integration: includes `<linux/types.h>` for `u32`. Consumed by `phy.c` and implemented by `table.c`.

Risks: length constants must exactly match initializer sizes. Wrong lengths can skip required programming or read past array bounds. Include guard spelling `__RTL8723E_TABLE__H_` is unusual but functional. Non-const externs allow accidental writes from any includer.

Test signals: compile/link success, KASAN/UBSAN array-bound cleanliness during table load, and hardware init stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.c

Purpose: `trx.c` implements RTL8723AE RX descriptor parsing, PHY status translation, TX descriptor filling, descriptor get/set helpers, TX descriptor ownership checks, and PCI TX polling.

Important APIs/functions: exported functions are `rtl8723e_rx_query_desc`, `rtl8723e_tx_fill_desc`, `rtl8723e_tx_fill_cmddesc`, `rtl8723e_set_desc`, `rtl8723e_get_desc`, `rtl8723e_is_tx_desc_closed`, and `rtl8723e_tx_polling`. Internal helpers map hardware queues to firmware queue selectors, parse PHY status, and translate RX signal data into rtlwifi stats.

Control flow: RX descriptor handling reads length, driver-info size, shift, CRC/ICV, decryption flag, rate, AMPDU flags, TSF, bandwidth, and HT/CCK indicators; it fills `ieee80211_rx_status`, handles robust management frame decryption flags, maps rate indexes, and, when PHY status is present, computes RSSI/PWDB/EVM/signal quality before passing PHY info to common processing. TX fill DMA maps the SKB, derives bandwidth from opmode/station, gets the rtlwifi TCB descriptor, clears the descriptor, sets rate, aggregation, RTS/CTS, bandwidth/subcarrier, packet size, AMPDU density, security type, queue selector, fallback limits, RDG, segment flags, DMA buffer address, rate ID/MAC ID, hardware sequence for LPS non-QoS frames, fragmentation, and BMC bit. Command descriptors are similar but force beacon queue, 1M rate, own bit, and command defaults.

State and persistence: RX mutates `struct rtl_stats`, `struct ieee80211_rx_status`, and `rtlpriv->stats.rx_snr_db`; PHY info processing updates common driver signal statistics. TX descriptors persist DMA addresses and metadata consumed by hardware, and `dma_map_single` creates DMA mappings that must be released later by PCI TX completion code outside this file. Descriptor ownership bits persist in ring memory until hardware clears them.

Dependencies/integration: depends on descriptor bitfield accessors from `trx.h`, rtlwifi PCI rings, mac80211 SKB/status types, common rate mapping and PHY-info helpers, register constants, and security/key metadata. `sw.c` publishes these functions in `rtl_hal_ops`; PCI core code calls them for RX/TX.

Risks: DMA mapping errors return without filling a descriptor, so callers must handle an unusable TX slot. This file maps DMA but does not unmap, relying on the wider PCI TX lifecycle. RX PHY parsing assumes descriptor-reported shifts and driver-info sizes are valid before dereferencing SKB data. Signal formulas are hardware-specific and can regress roaming/rate control if changed. `rtl8723e_is_tx_desc_closed` ignores its `index` argument and checks `ring->idx`, which may be intentional but is a maintenance hazard. Command descriptor uses `USB_HWDESC_HEADER_LEN` names in a PCI driver due shared descriptor definitions.

Test signals: RX traffic with CCK, OFDM, HT, 20/40 MHz, AMPDU, CRC/ICV failure, protected robust management frames, signal/RSSI sanity, and rate-index mapping. TX tests should cover data, management, beacon, control/nullfunc, multicast/broadcast, encrypted WEP/TKIP/CCMP, AMPDU, RTS/CTS, AP/STA/adhoc bandwidth decisions, DMA mapping failure injection, descriptor ownership clearing, and PCI polling per queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/trx.c -->
