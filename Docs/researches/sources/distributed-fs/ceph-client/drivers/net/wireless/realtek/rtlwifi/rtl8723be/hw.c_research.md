# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.c

## Purpose
Provides the RTL8723BE hardware operations behind the rtlwifi/mac80211 driver: power-on/off sequencing, PCIe DMA and LLT setup, firmware download, MAC/BB/RF initialization, hardware register get/set dispatch, beacon and media-state programming, interrupt control, EFUSE/OEM parsing, rate-mask H2C updates, CAM security programming, GPIO radio detection, Bluetooth coexistence setup, and card disable.

## Important APIs, Types, And Functions
Primary public entry points include `rtl8723be_hw_init()`, `rtl8723be_card_disable()`, `rtl8723be_get_hw_reg()`, `rtl8723be_set_hw_reg()`, `rtl8723be_read_eeprom_info()`, `rtl8723be_enable_interrupt()`, `rtl8723be_disable_interrupt()`, `rtl8723be_interrupt_recognized()`, `rtl8723be_set_network_type()`, `rtl8723be_set_check_bssid()`, `rtl8723be_set_qos()`, beacon setup helpers, `rtl8723be_update_hal_rate_tbl()`, `rtl8723be_gpio_radio_on_off_checking()`, `rtl8723be_enable_hw_security_config()`, `rtl8723be_set_key()`, and BT coexistence init/read helpers. Important internals include `_rtl8723be_init_mac()`, `_rtl8723be_llt_table_init()`, `_rtl8723be_poweroff_adapter()`, `_rtl8723be_check_pcie_dma_hang()`, `_rtl8723be_reset_pcie_interface_dma()`, `_rtl8723be_download_rsvd_page()`, `_rtl8723be_fwlps_enter()`/leave, and EFUSE TX-power parsing routines.

## Control Flow
`rtl8723be_hw_init()` enables interrupts locally, disables ASPM, detects whether MAC was already enabled, resets DMA if hung, powers off stale MAC state, runs the MAC power-on flow, downloads firmware, configures MAC/BB/RF, updates receive config, initializes RF channel values, programs hardware defaults, resets CAM, enables security, sets MAC address, applies ASPM backdoor settings, initializes BT hardware, runs RF-path/IQK/thermal/LC calibration when RF is on, releases RX/PCIe DMA, and initializes DM. Shutdown sets no-link media state, updates LEDs, marks NIC halt power level, runs firmware self-reset and power sequencing, resets MCU wrapper, and locks power-control registers.

## State And Persistence
This file is the major state bridge between rtlwifi software state and hardware registers. It mutates `rtlhal` flags (`fw_ready`, `mac_func_enable`, `being_init_adapter`, firmware PS fields), PCI ring DMA registers and IRQ masks, `rtlpci->receive_config`, beacon-control cache, `rtlpriv->sec`/CAM entries, EFUSE TX-power tables, OEM id, board/package type, BT coexistence info, power-save state, MAC link/opmode fields, and LED state. Hardware persistence includes LLT page chains, queue boundaries, DMA descriptors, CAM key slots, media-state register, RCR, interrupt masks, TSF/beacon registers, and firmware LPS/offload state.

## Dependencies And Integration Points
Depends on rtlwifi common EFUSE, CAM, PCI, PS, register, firmware, PHY, DM, LED, power-sequence, and BT coexistence layers. It is called by the rtlwifi core operation table from `sw.c` and routes many generic `HW_VAR_*` operations to RTL8723BE-specific registers or firmware H2C commands. It also integrates with mac80211 station rate capabilities when building RA-mask commands.

## Risks
Initialization order is firmware- and hardware-sensitive: LLT, DMA descriptors, firmware readiness, BB/RF config, CAM, ASPM, BT, and calibration must happen in the right order. PCIe DMA hang reset pauses and restores DMA/register locks and can disrupt live state if misdetected. `set_hw_reg()` is a large switch with many typed `u8 *` casts; wrong caller value types corrupt state. EFUSE parsing uses many defaults and OEM tables, so bad autoload handling affects TX power, LED behavior, and BT antenna selection. CAM key programming must allocate/free correct entries for AP, station, group, pairwise, WEP, and adhoc modes.

## Test Signals
Probe logs should show firmware download, MAC/BB/RF config, chip version, EFUSE autoload, and calibration without errors. Validate interrupts, TX/RX DMA, association and reserved-page download, AP/adhoc beaconing, BSSID filtering, QoS/EDCA, security with WEP/TKIP/CCMP group and pairwise keys, RF-kill GPIO toggles, suspend/card disable/resume path expectations, BT coexistence antenna overrides, and rate-mask H2C changes as RSSI changes. DMA API, lockdep, and firmware assertion logs are important diagnostics.
