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
