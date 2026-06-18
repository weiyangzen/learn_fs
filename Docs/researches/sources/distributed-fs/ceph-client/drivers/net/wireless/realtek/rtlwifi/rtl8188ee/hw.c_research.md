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
