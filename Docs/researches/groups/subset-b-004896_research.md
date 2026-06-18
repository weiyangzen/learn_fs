# Research: subset-b-004896

Worker-produced grouped research for the RTL8821AE/RTL8812AE hardware and LED support files. Each source section is wrapped for the reconciliation lane and mirrors the source path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.c

## Purpose

`hw.c` is the main PCIe hardware control implementation for the rtlwifi RTL8821AE/RTL8812AE driver. It binds mac80211-facing operations to Realtek register programming, firmware H2C commands, PCIe DMA setup, EFUSE/EEPROM parsing, WoWLAN preparation, rate-adaptation programming, beacon/media-state control, interrupt masking, RF power-state checks, CAM security-key programming, and Bluetooth coexistence initialization.

The file supports two closely related chips behind runtime `rtlhal->hw_type` checks: `HARDWARE_TYPE_RTL8821AE` and `HARDWARE_TYPE_RTL8812AE`. Most exported functions are called through the per-chip `rtlpriv->cfg->ops` table declared by the surrounding rtlwifi core; many static helpers encode chip-specific register sequences.

## Important APIs, Types, and Functions

Public hardware API implemented here:

- `rtl8821ae_get_hw_reg()` and `rtl8821ae_set_hw_reg()` implement the rtlwifi hardware-variable switchboard. They read or write MAC address, BSSID, media status, slot/SIFS timing, RCR, EFUSE counters, firmware power-save state, RPWM, AID, TSF correction, NAV upper bound, keep-alive H2C state, and join-BSS firmware reports.
- `rtl8821ae_hw_init()` performs full adapter bring-up: disable ASPM, detect already-powered MAC, handle WoWLAN resume fast path, recover PCIe DMA hangs, power-cycle stale MAC state, initialize MAC/LLT/descriptors, download firmware, configure MAC/BB/RF, initialize security/CAM, ASPM backdoor, Bluetooth coexistence, interrupts/DMA release, and dynamic management.
- `rtl8821ae_card_disable()` powers the device down or prepares WoWLAN host sleep depending on `HAL_DEF_WOWLAN`, `mac->opmode`, and `rtlhal->enter_pnp_sleep`.
- `rtl8821ae_read_eeprom_info()` reads chip version, RF path capability, EEPROM/EFUSE boot mode, autoload state, adapter information, power tables, RFE/PA/LNA/BT coexistence fields, channel plan, thermal meter, antenna-diversity settings, board type, and LED open-drain policy.
- `rtl8821ae_enable_interrupt()`, `rtl8821ae_disable_interrupt()`, `rtl8821ae_interrupt_recognized()`, and `rtl8821ae_update_interrupt_mask()` manage HIMR/HIMRE/HSIMR masks and clear recognized interrupt bits.
- `rtl8821ae_set_network_type()`, `rtl8821ae_set_check_bssid()`, `rtl8821ae_set_qos()`, `rtl8821ae_set_beacon_related_registers()`, and `rtl8821ae_set_beacon_interval()` program media-state, beacon gating, BSSID receive filters, EDCA parameters, and beacon timing.
- `rtl8821ae_update_hal_rate_tbl()` chooses between legacy ARFR table writes and firmware RA-mask H2C programming via `rtlpriv->dm.useramask`.
- `rtl8821ae_gpio_radio_on_off_checking()` samples the hardware radio GPIO and updates `ppsc->hwradiooff` under RF power-state locking.
- `rtl8821ae_enable_hw_security_config()` and `rtl8821ae_set_key()` enable the MAC security engine and program/delete CAM entries for WEP/TKIP/AES pairwise and group keys.
- `rtl8821ae_add_wowlan_pattern()` writes wake-frame CAM entries into the RX packet buffer region used by firmware WoWLAN matching.
- `rtl8821ae_bt_reg_init()` and `rtl8821ae_bt_hw_init()` initialize Bluetooth coexistence configuration.
- `rtl8821ae_suspend()` and `rtl8821ae_resume()` are exported stubs.
- `_rtl8821ae_stop_tx_beacon()` and `_rtl8821ae_resume_tx_beacon()` are exported despite leading underscores; they directly gate beacon queue transmission and TBTT prohibit behavior.

Important static helpers include `_rtl8821ae_download_rsvd_page()`, `_rtl8821ae_fwlps_enter()`, `_rtl8821ae_fwlps_leave()`, `_rtl8821ae_set_fw_clock_on()`, `_rtl8821ae_set_fw_clock_off()`, `_rtl8821ae_llt_write()`, `_rtl8821ae_llt_table_init()`, `_rtl8821ae_init_mac()`, `_rtl8821ae_dynamic_rqpn()`, `_rtl8821ae_wowlan_initialize_adapter()`, `_rtl8821ae_poweroff_adapter()`, `_rtl8821ae_read_chip_version()`, `_rtl8821ae_read_power_value_fromprom()`, `_rtl8821ae_read_txpower_info_from_hwpg()`, `_rtl8812ae_read_amplifier_type()`, `_rtl8821ae_read_rfe_type()`, `_rtl8821ae_read_adapter_info()`, `rtl8821ae_update_hal_rate_table()`, and `rtl8821ae_update_hal_rate_mask()`.

Core data dependencies are `struct rtl_priv`, `struct rtl_hal`, `struct rtl_pci`, `struct rtl_mac`, `struct rtl_phy`, `struct rtl_ps_ctl`, `struct rtl_efuse`, `struct rtl_sta_info`, `struct rtl_int`, and `struct rtl_wow_pattern` from the rtlwifi stack and mac80211.

## Control Flow

Adapter initialization starts in `rtl8821ae_hw_init()`. It sets `being_init_adapter`, asks `get_hw_reg(HAL_DEF_WOWLAN)` whether remote wake is enabled, disables ASPM through interface ops, and determines whether the MAC is already powered by reading `REG_CR`. If the adapter is resuming from WoWLAN with the MAC still functional, `_rtl8821ae_wowlan_initialize_adapter()` reads wake reason, recovers PCIe DMA if needed, restores descriptor addresses, disables firmware WoWLAN mode, reinitializes LLT/RQPN if marked, releases DMA, and returns early when successful. Otherwise initialization checks for PCIe DMA hang, powers off stale MAC state, runs `_rtl8821ae_init_mac()`, downloads firmware, configures MAC/BB/RF, applies 1T config for RTL8812AE in RF_1T1R mode, sets MAC defaults, switches to 2.4 GHz, resets CAM, enables hardware security, writes the MAC address, enables ASPM backdoor, initializes BT coexistence, releases DMA, initializes dynamic management, and reports media-status mapping to firmware.

Power-save flow is mediated by `rtl8821ae_set_hw_reg()`. `HW_VAR_FW_LPS_ACTION` calls `_rtl8821ae_fwlps_enter()` or `_rtl8821ae_fwlps_leave()`. Entering firmware LPS marks `ppsc->fw_current_inpsmode`, sends firmware power mode, optionally allows software clock changes, and drives RPWM to RF-off or low-power RF-off. Leaving LPS wakes firmware via RPWM/CPWM acknowledgement, sends active firmware power mode, clears firmware power-save status, and disables software clock changes. `_rtl8821ae_set_fw_clock_off()` refuses to clock off when firmware is not ready, FW PS is inactive, RF is already off, or any PCIe TX ring has queued frames; otherwise it writes `REG_PCIE_HRPWM` and may reschedule `fw_clockoff_timer`.

WoWLAN suspend flow in `rtl8821ae_card_disable()` branches between normal poweroff and WoWLAN preparation. Normal poweroff clears link state, sets media status to unspecified, and runs `_rtl8821ae_poweroff_adapter()`. WoWLAN mode clears firmware wake event state, optionally switches firmware image, reallocates TX packet boundaries for reserved pages, sends global/security information, downloads reserved page packets, enables firmware WoWLAN/keep-alive/disconnect-decision controls for connected station mode, pauses RX DMA, resets TRX rings, clears PCI PME status, preserves MCU state across PERST, enables remote wake control, stops PCIe TX DMA, and clears hardware ROF status if used.

Rate programming starts in `rtl8821ae_update_hal_rate_tbl()`. With firmware RA masks enabled, `rtl8821ae_update_hal_rate_mask()` derives a bitmap from station supported rates, HT MCS masks, VHT MCS map, wireless mode, RSSI level, RF type, channel width, SGI capability, and macid. It translates the rate index through `rtl_mrate_idx_to_arfr_id()` and sends a seven-byte `H2C_8821AE_RA_MASK` command. Without RA masks, `rtl8821ae_update_hal_rate_table()` writes the local ARFR table directly.

EEPROM/EFUSE flow starts with `rtl8821ae_read_eeprom_info()`. Chip version detection sets RF path shape and `rtlhal->hw_rof_enable`; boot source and autoload state come from `REG_9346CR`; successful autoload calls `_rtl8821ae_read_adapter_info()`. Adapter-info parsing allocates `HWSET_MAX_SIZE`, calls `rtl_get_hwinfo()`, parses TX power tables, PA/LNA/RFE type, BT coexistence, board type, channel plan, crystal cap, thermal meter, antenna diversity, OEM ID, and LED open-drain state, then frees the buffer.

## State and Persistence Behavior

This file persists device state in both hardware registers and rtlwifi software structures. Hardware-persistent state includes MAC address, BSSID, RCR receive filters, beacon control, TSF, EDCA, CAM entries, LLT/RQPN packet buffer topology, descriptor base addresses, security engine state, interrupt masks, firmware RPWM/CPWM state, WoWLAN pattern CAM, and PCIe DBI/MDIO ASPM/LTR/L1 settings. Software state mirrors or coordinates hardware through `rtlpci->receive_config`, `rtlpci->reg_bcn_ctrl_val`, `rtlpci->irq_mask[]`, `rtlpci->irq_enabled`, `rtlhal->mac_func_enable`, `rtlhal->fw_ready`, `rtlhal->fw_ps_state`, `rtlhal->fw_clk_change_in_progress`, `rtlhal->allow_sw_to_change_hwclc`, `rtlhal->re_init_llt_table`, `ppsc->rfpwr_state`, `ppsc->fw_current_inpsmode`, `ppsc->hwradiooff`, `rtlefuse` calibration fields, and `rtlpriv->sec.key_buf/key_len`.

Several operations use locking because they cross interrupt, timer, or RF power-state contexts. `_rtl8821ae_return_beacon_queue_skb()` protects beacon TX ring dequeue and DMA unmap with `irq_th_lock`. Firmware clock transitions use `fw_ps_lock`. Hardware radio switch checks use `rf_ps_lock` and `rfchange_inprogress`. Timed persistence exists via `fw_clockoff_timer`, which retries firmware clock-off while TX queues are non-empty or a clock transition is in progress.

## Dependencies and Integration Points

The file depends on rtlwifi common headers (`wifi.h`, `efuse.h`, `base.h`, `regd.h`, `cam.h`, `ps.h`, `pci.h`, `pwrseqcmd.h`) and chip-local headers (`reg.h`, `def.h`, `phy.h`, `dm.h`, `fw.h`, `led.h`, `hw.h`, `pwrseq.h`). It integrates with:

- mac80211 types and state, especially `struct ieee80211_hw`, `struct ieee80211_sta`, station HT/VHT capability fields, and `enum nl80211_iftype`.
- rtlwifi PCI interface ops for ASPM, TRX ring reset, descriptor rings, and IRQ masks.
- firmware command helpers in `fw.c` for power mode, media status, P2P PS, reserved pages, WoWLAN, keep-alive, disconnect decision, global info, and RA masks.
- PHY/DM helpers for MAC/BB/RF config, wireless-band switching, EDCA turbo, IO commands, dynamic management, and BB register writes.
- CAM helpers for hardware key storage.
- Bluetooth coexistence via `../btcoexist/rtl_btc.h` and `btc_ops`.
- Linux PCI config-space helpers, DMA unmap helpers, timers, spinlocks, delays, and warning/logging APIs.

## Risks and Edge Cases

Most risks are sequencing-sensitive. Initialization and WoWLAN paths directly pause, reset, and release TX/RX DMA; missed ordering can leave rings inconsistent with descriptor base registers. `_rtl8821ae_dynamic_rqpn()` resets parts of MAC/BB and reinitializes LLT while polling hardware readiness with bounded loops; timeout paths usually log and continue rather than fully failing. Firmware power-save depends on CPWM acknowledgement and software flags staying synchronized with firmware. If `fw_clk_change_in_progress` is mishandled, clock-off/on timers can churn or race with LPS transitions.

The EEPROM autoload failure path logs `Autoload ERR!!` but does not call `_rtl8821ae_read_adapter_info()` with fallback defaults from this top-level function, leaving later defaults dependent on earlier initialization. The TX-power parser contains many signed 4-bit conversions and array-indexed channel group mappings; off-by-one or unexpected channel values would affect regulatory and power behavior. Hardware register constants are almost entirely magic values, making regressions hard to review without vendor programming guides.

Security CAM programming assumes `rtlpriv->sec.key_len[]` and `key_buf[]` were already updated by higher layers. AP pairwise key allocation can fail when CAM is full; the function logs and returns. `rtl8821ae_bt_reg_init()` assigns `reg_bt_sco` twice, first to `3` and then to `0`, which looks like either a stale comment or a missing assignment to another BT coexistence field. There are also exported underscore-prefixed beacon helpers, increasing the chance of out-of-file callers depending on low-level sequencing.

## Test Signals

Useful validation signals include successful driver probe with `rtl8821ae_hw_init()` returning zero, firmware download success with `rtlhal->fw_ready = true`, no LLT polling failures, no PCIe DMA hang recovery warnings after repeated suspend/resume, stable association in station mode, AP/adhoc beacon transmission after media-state transitions, correct interrupt delivery after enable/disable/mask updates, successful WoWLAN wake reason reporting, CAM key install/delete behavior across WEP/TKIP/AES and AP/client modes, rate-mask H2C command traces under HT/VHT stations, hardware radio switch transitions without stuck `rfchange_inprogress`, LED state updates through media and power transitions, and no WARN_ONCE reports from invalid ACI/channel group/wake-pattern writes. Runtime register traces around `REG_CR`, `REG_RCR`, `REG_HIMR`, `REG_HISRE`, `REG_PCIE_CTRL_REG`, `REG_RXDMA_CONTROL`, `REG_BCN_CTRL`, and `REG_SECCFG` would be especially useful for integration tests or hardware bring-up logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.h

## Purpose

`hw.h` is the public hardware-control interface for the RTL8821AE/RTL8812AE rtlwifi chip module. It exposes the functions implemented in `hw.c` that the chip operation table, PCI glue, mac80211 callbacks, power-management code, and adjacent chip files need to call. The header contains no state of its own; it is a declaration boundary over register programming, initialization, power management, security, rate adaptation, beacon control, WoWLAN, and Bluetooth coexistence helpers.

## Important APIs, Types, and Functions

The declarations use rtlwifi and mac80211 types from included compilation units rather than including those headers directly. Key types include `struct ieee80211_hw`, `struct ieee80211_sta`, `struct rtl_int`, `struct rtl_wow_pattern`, `enum nl80211_iftype`, and standard integer/boolean types.

The header groups the driver surface into several roles:

- Hardware variable access: `rtl8821ae_get_hw_reg()` and `rtl8821ae_set_hw_reg()`.
- Adapter lifecycle: `rtl8821ae_read_eeprom_info()`, `rtl8821ae_hw_init()`, `rtl8821ae_card_disable()`, `rtl8821ae_suspend()`, and `rtl8821ae_resume()`.
- Interrupt handling: `rtl8821ae_interrupt_recognized()`, `rtl8821ae_enable_interrupt()`, `rtl8821ae_disable_interrupt()`, and `rtl8821ae_update_interrupt_mask()`.
- MAC/media/beacon/QoS: `rtl8821ae_set_network_type()`, `rtl8821ae_set_check_bssid()`, `rtl8821ae_set_qos()`, `rtl8821ae_set_beacon_related_registers()`, `rtl8821ae_set_beacon_interval()`, `_rtl8821ae_stop_tx_beacon()`, and `_rtl8821ae_resume_tx_beacon()`.
- Rate and channel access: `rtl8821ae_update_hal_rate_tbl()` and `rtl8821ae_update_channel_access_setting()`.
- RF and power-state checks: `rtl8821ae_gpio_radio_on_off_checking()`.
- Security: `rtl8821ae_enable_hw_security_config()` and `rtl8821ae_set_key()`.
- Bluetooth coexistence: `rtl8821ae_bt_reg_init()` and `rtl8821ae_bt_hw_init()`.
- Receive filtering and WoWLAN: `rtl8821ae_allow_all_destaddr()` and `rtl8821ae_add_wowlan_pattern()`.

## Control Flow

The header does not implement control flow, but its declarations outline the call graph expected by the rest of the chip driver. Probe/setup code calls `rtl8821ae_read_eeprom_info()` before `rtl8821ae_hw_init()` so chip version, RF paths, EFUSE power tables, and board features are known before MAC/BB/RF configuration. Runtime mac80211 state changes call the media, QoS, beacon, rate, and security functions. Interrupt service code calls `rtl8821ae_interrupt_recognized()` after masks have been installed through `rtl8821ae_enable_interrupt()`. Power-management code calls `rtl8821ae_card_disable()` for normal shutdown or WoWLAN preparation, and the empty suspend/resume hooks remain available for the rtlwifi operation table.

## State and Persistence Behavior

No storage is declared in this header. The functions it exposes mutate persistent driver and hardware state in `struct rtl_priv` subobjects and device registers: interrupt masks, receive configuration, beacon control, firmware power-save flags, EFUSE-derived calibration fields, CAM keys, and WoWLAN pattern memory. Because the header is a broad interface, callers must assume many functions have side effects beyond their parameter list. For example, `rtl8821ae_set_key()` uses key material already stored in `rtlpriv->sec`, and `rtl8821ae_update_hal_rate_tbl()` depends on station driver-private metadata.

## Dependencies and Integration Points

`hw.h` is included by the chip implementation and likely by the chip operations registration code. It intentionally relies on prior includes for definitions of mac80211, rtlwifi, and integer types, so include order matters in C files that consume it. It also exposes two underscore-prefixed beacon helpers that are implemented as low-level register routines but remain callable outside `hw.c`; that makes beacon sequencing part of the module ABI.

## Risks and Edge Cases

The header has no compile-time guards beyond the include guard and no documentation for pointer ownership or required locks. Several APIs take untyped `u8 *val` switchboard parameters, so type correctness is implicit in the selected hardware variable. The exported `_rtl8821ae_stop_tx_beacon()` and `_rtl8821ae_resume_tx_beacon()` names look private but are public, which can encourage callers to bypass higher-level media-state routines. Empty `suspend` and `resume` declarations may hide the fact that real suspend behavior is handled by `card_disable()` and WoWLAN helpers.

## Test Signals

Build tests should catch signature drift between this header and `hw.c`. Runtime integration should confirm every function pointer assignment in the RTL8821AE ops table matches these prototypes, especially `get_hw_reg`, `set_hw_reg`, interrupt hooks, security hooks, rate updates, and LED/media paths that call beacon helpers. Static analysis should flag any include-order breakage where `struct ieee80211_hw`, `struct rtl_int`, or `struct rtl_wow_pattern` are not visible before including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.c

## Purpose

`led.c` implements software LED control for RTL8821AE and RTL8812AE devices. It translates rtlwifi LED actions into writes to the chip LED configuration registers and pin-mux register, with separate on/off programming sequences for the RTL8821AE and RTL8812AE register layout. The file is small but sits on a visible user-facing hardware behavior path: link and power state indications.

## Important APIs, Types, and Functions

Public functions:

- `rtl8821ae_sw_led_on(struct ieee80211_hw *hw, enum rtl_led_pin pin)` turns on RTL8821AE LEDs for `LED_PIN_LED0` and `LED_PIN_LED1`; GPIO0 is recognized but not programmed.
- `rtl8812ae_sw_led_on(struct ieee80211_hw *hw, enum rtl_led_pin pin)` selects `REG_LEDCFG1` or `REG_LEDCFG2` for RTL8812AE LED0/LED1 and enables software LED-on control bits.
- `rtl8821ae_sw_led_off(struct ieee80211_hw *hw, enum rtl_led_pin pin)` turns off RTL8821AE LEDs, including an open-drain path that also clears `REG_MAC_PINMUX_CFG` bit 0 for GPIO input behavior.
- `rtl8812ae_sw_led_off(struct ieee80211_hw *hw, enum rtl_led_pin pin)` turns off RTL8812AE LEDs using either open-drain pin-mux handling or a direct `0x28` LED config write.
- `rtl8821ae_led_control(struct ieee80211_hw *hw, enum led_ctl_mode ledaction)` is the exported policy entry point. It suppresses link/activity/power-on LED actions when RF is off for a reason stronger than power save, logs the action, and delegates to `_rtl8821ae_sw_led_control()`.

The private `_rtl8821ae_sw_led_control()` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to LED-on, maps `LED_CTL_POWER_OFF` to LED-off, and ignores other action modes.

## Control Flow

Callers should enter through `rtl8821ae_led_control()`, usually via `rtlpriv->cfg->ops->led_control()` from media-state, initialization, or power paths. The function reads `ppsc->rfoff_reason`; if RF is off due to hardware/software radio, unload, or another non-PS reason, it ignores TX/RX/site-survey/link/start/power-on actions to avoid showing activity while the device is effectively off. Allowed actions are logged and passed to `_rtl8821ae_sw_led_control()`. The helper selects the hardware-specific routine based on `rtlhal->hw_type`, then writes the selected LED registers.

The direct on/off functions can also be called by `hw.c` during LED refresh after MAC initialization. `_rtl8821ae_gen_refresh_led_state()` chooses on/off based on `ppsc->rfoff_reason` and dispatches to either RTL8812AE or RTL8821AE functions.

## State and Persistence Behavior

The code persists LED state in hardware registers: `REG_LEDCFG1`, `REG_LEDCFG2`, and `REG_MAC_PINMUX_CFG`. It reads software configuration from `rtlpriv->ledctl.sw_led0` and `rtlpriv->ledctl.led_opendrain`. It does not maintain a separate cached LED state, so the hardware registers are the effective state. LED writes are not protected by a local lock; callers rely on the broader rtlwifi sequencing around power and media-state transitions.

For open-drain configurations, off transitions also adjust MAC pin muxing by clearing bit 0 in `REG_MAC_PINMUX_CFG`, making pin configuration part of LED state. This means LED off behavior can affect GPIO electrical mode and must remain synchronized with board-specific LED open-drain setup from EEPROM parsing.

## Dependencies and Integration Points

The file includes `../wifi.h`, `../pci.h`, chip `reg.h`, and `led.h`. It depends on `rtl_priv()`, `rtl_hal()`, `rtl_psc()`, `rtl_read_byte()`, `rtl_write_byte()`, `rtl_dbg()`, chip constants such as `REG_LEDCFG1`, `REG_LEDCFG2`, `REG_MAC_PINMUX_CFG`, and shared enums `enum rtl_led_pin` and `enum led_ctl_mode`.

Integration points are the chip ops table and hardware code. `hw.c` calls hardware-specific software LED routines during MAC init refresh and invokes `led_control()` during media-state and power-off transitions. The rest of rtlwifi should not need to know the register differences between RTL8821AE and RTL8812AE.

## Risks and Edge Cases

GPIO0 cases are effectively no-ops in all on/off routines, so boards wired to GPIO0 require another path or will show no LED behavior. `_rtl8821ae_sw_led_control()` treats `LED_CTL_NO_LINK` as LED-on, which may be intentional for Realtek's LED mode but is counterintuitive if a caller expects no-link to extinguish the LED. TX/RX/site-survey/start-to-link actions are ignored by the helper unless filtered earlier, so activity blinking is not implemented here.

There is a likely defect in the RTL8812AE open-drain off path: inside `rtl8812ae_sw_led_off()`, the code reads `ledcfg` from `ledreg`, then executes `ledreg &= 0xd0` before writing `rtl_write_byte(rtlpriv, ledreg, (ledcfg | BIT(3)))`. This masks the register address rather than masking `ledcfg`, unlike the RTL8821AE off path. If reached, it can write to the wrong register address. This should be reviewed against vendor code.

## Test Signals

Hardware smoke tests should check LED0 and LED1 behavior on both RTL8821AE and RTL8812AE devices across power-on, association, disassociation, RF-kill, driver unload, and WoWLAN/card-disable paths. Register tracing should confirm writes target `REG_LEDCFG1` or `REG_LEDCFG2` as intended, especially for RTL8812AE open-drain off. Tests should verify RF-off suppression: link or activity actions should not turn LEDs on when `rfoff_reason > RF_CHANGE_BY_PS`, while `LED_CTL_POWER_OFF` should still force off. Board-variant tests should include `led_opendrain` true and false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.h

## Purpose

`led.h` declares the RTL8821AE/RTL8812AE software LED control interface. It is the header boundary between chip hardware code, the chip operations table, and `led.c`. The file contains only an include guard and function prototypes; it stores no state and defines no local types.

## Important APIs, Types, and Functions

The header declares five functions:

- `rtl8821ae_sw_led_on()` and `rtl8821ae_sw_led_off()` for RTL8821AE-specific direct LED register control.
- `rtl8812ae_sw_led_on()` and `rtl8812ae_sw_led_off()` for RTL8812AE-specific direct LED register control.
- `rtl8821ae_led_control()` as the policy-level LED action entry point that receives `enum led_ctl_mode`.

The prototypes depend on `struct ieee80211_hw`, `enum rtl_led_pin`, and `enum led_ctl_mode` being visible from previous includes, normally via rtlwifi `wifi.h`.

## Control Flow

The header itself has no control flow. Its intended flow is that generic rtlwifi or chip hardware code calls `rtl8821ae_led_control()` for action-based LED policy, while chip-local initialization code may call the hardware-specific direct on/off functions after determining `rtlhal->hw_type`. The direct functions should not be treated as generic LED policy because they bypass RF-off filtering.

## State and Persistence Behavior

No state is declared in the header. The functions declared here persist LED state through hardware register writes in `led.c` and depend on runtime state held in `rtlpriv->ledctl`, `rtlhal->hw_type`, and `ppsc->rfoff_reason`.

## Dependencies and Integration Points

`led.h` is included by `led.c` and `hw.c`. It integrates LED control with the broader RTL8821AE hardware lifecycle: media-state changes call the policy function, while MAC initialization refresh can call the direct hardware-specific functions. Like `hw.h`, this header relies on include order for type definitions rather than including the full mac80211/rtlwifi declarations itself.

## Risks and Edge Cases

The API exposes both direct hardware controls and policy-level control without documenting the difference. A caller using direct functions can turn LEDs on even when RF-off policy would suppress that action. There is no lock contract or register-side effect documentation. Signature drift between `led.h` and `led.c` would be caught at build time, but semantic drift in action handling requires hardware tests.

## Test Signals

Build coverage should ensure all declared prototypes match `led.c`. Runtime validation should confirm the chip ops table calls `rtl8821ae_led_control()` for normal LED policy and that direct functions are limited to chip-local refresh paths. Include-order tests or static analysis can catch consumers that include `led.h` before `struct ieee80211_hw` and LED enums are declared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.h -->
