# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.c

## Purpose
This file implements RTL8192SE hardware control: register get/set callbacks, security CAM programming, firmware-era MAC initialization, full hardware bring-up and shutdown, interrupt control, beacon configuration, EFUSE/EEPROM parsing, rate table programming, RF kill handling, key installation, and suspend/resume PCI quirks.

## Important APIs, Types, And Functions
Public HAL callbacks include `rtl92se_get_hw_reg()`, `rtl92se_set_hw_reg()`, `rtl92se_enable_hw_security_config()`, `rtl8192se_gpiobit3_cfg_inputmode()`, `rtl92se_hw_init()`, `rtl92se_card_disable()`, `rtl92se_interrupt_recognized()`, `rtl92se_set_beacon_related_registers()`, `rtl92se_set_beacon_interval()`, `rtl92se_update_interrupt_mask()`, `rtl92se_read_eeprom_info()`, `rtl92se_update_hal_rate_tbl()`, `rtl92se_update_channel_access_setting()`, `rtl92se_gpio_radio_on_off_checking()`, `rtl92se_set_key()`, `rtl92se_suspend()`, and `rtl92se_resume()`.

Important internal helpers include `_rtl92se_macconfig_before_fwdownload()`, `_rtl92se_macconfig_after_fwdownload()`, `_rtl92se_hw_configure()`, `_rtl92se_set_media_status()`, `_rtl92s_phy_set_rfhalt()`, `_rtl92se_power_domain_init()`, `_rtl92se_read_adapter_info()`, `rtl92se_update_hal_rate_table()`, and `rtl92se_update_hal_rate_mask()`.

## Control Flow
`rtl92se_hw_init()` is the main bring-up sequence. It marks initialization active, temporarily enables local IRQs because init may take hundreds of milliseconds, disables ASPM, performs pre-firmware MAC/power/descriptor-address setup, detects chip cut, configures GPIO3, downloads firmware, applies post-firmware MAC defaults, captures firmware command map state, programs MAC/BB/RF tables, reads RF channel values, enables CCK/OFDM, configures retry/min-spacing/aggregation, stores original PHY register values, applies channel transmit power, writes MAC address, initializes firmware RA behavior, applies EPHY/ASPM workaround, clears/enables security CAM state, sets EDCA defaults, turns on MRC for 1T2R, lights LED, and initializes dynamic management.

Shutdown and RF-off paths call `rtl92se_card_disable()` and `_rtl92s_phy_set_rfhalt()`, which stop link state, set media status to no link, pause TX/CCA, power down BB/RF/MAC blocks, switch clock/control path, configure low-power LED/GPIO state, and mark halt power-save level. RF kill checking may temporarily power up the domain to read GPIO3, then re-halt it if nothing changed.

## State And Persistence
This file owns substantial driver-visible state: `rtlpci->receive_config`, interrupt masks and enabled flag, `rtlpci->being_init_adapter`, `rtlhal->version`, firmware command map/parameter cache, `rtlphy->rf_mode`, `rfreg_chnlval`, RF type, min-space config, EFUSE-derived MAC address, channel power tables, regulatory fields, thermal/crystal values, `ppsc` RF power/hardware radio flags, CAM key buffers/lengths, and rate-adaptive indices in station private state. Hardware register state is persistent until reset/power-down and is replayed during init/resume.

## Dependencies And Integration Points
It depends on rtlwifi PCI transport, EFUSE helpers, regulatory helpers, CAM helpers, power-save helpers, firmware download from `fw.c`, PHY configuration from `phy.c`/`rf.c`, dynamic management from `dm.c`, LED control, mac80211 station/vif state, and shared register definitions. `sw.c` wires these functions into the HAL ops table used by the generic rtlwifi core.

## Risks
Hardware bring-up is highly order-sensitive. Descriptor base addresses must be programmed before firmware download; firmware must be ready before MAC/PHY/RF tables and RA commands; RCR is rewritten after MAC config to avoid throughput and Cisco AP association issues. `rtl92se_hw_init()` enables local IRQs inside a caller context that may have disabled them, so reentrancy assumptions must remain valid before device interrupts are enabled. Power-domain and RF kill flows use sleeps/delays and shared `rf_ps_lock` state; races can leave the NIC powered up or halted incorrectly. EFUSE parsing trusts many offsets and has unusual index selection for OFDM diff (`0x11` for channel 4-8), so table bounds deserve scrutiny. CAM key setup branches differently for AP, station, adhoc, WEP/default keys, and group keys.

## Test Signals
Test cold boot, warm reboot, suspend/resume, IPS/LPS, RF kill toggle, module unload, firmware-missing failure, and repeated hardware init/disable cycles. Runtime signals include firmware ready, MAC/BB/RF config success, interrupts masked/unmasked correctly, correct MAC address from EFUSE, valid channel power programming, association in station/AP/adhoc modes, hardware crypto for pairwise/group/WEP keys, rate table updates for B/G/N and RSSI changes, and no stuck `pwrdomain_protect` or `rfchange_inprogress`.
