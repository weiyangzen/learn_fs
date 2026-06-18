# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.c

## Purpose
`hw.c` is the RTL8192EE PCIe hardware orchestration layer. It bridges mac80211/rtlwifi core requests to device registers, firmware H2C commands, EFUSE-derived configuration, PCIe DMA rings, interrupt masks, beacon controls, CAM security entries, Bluetooth coexistence hooks, and RF power transitions. It is the main bring-up/tear-down file for this chip.

## Important APIs, Types, And Functions
The exported entry points match `hw.h`: `rtl92ee_hw_init`, `rtl92ee_card_disable`, `rtl92ee_get_hw_reg`, `rtl92ee_set_hw_reg`, `rtl92ee_read_eeprom_info`, interrupt enable/disable/recognition, beacon setup, network type/QoS setup, security setup, key programming, BT coexistence init, suspend/resume stubs, promiscuous RCR control, and firmware clock-off timer callback. Internally, `_rtl92ee_init_mac`, `_rtl92ee_hw_configure`, `_rtl8192ee_check_pcie_dma_hang`, `_rtl8192ee_reset_pcie_interface_dma`, `_rtl92ee_poweroff_adapter`, `_rtl92ee_download_rsvd_page`, `_rtl92ee_read_adapter_info`, and `_rtl92ee_read_txpower_info_from_hwpg` are central. State is carried through `struct rtl_priv`, `rtl_hal`, `rtl_pci`, `rtl_mac`, `rtl_phy`, `rtl_efuse`, and `rtl_ps_ctl`.

## Control Flow
Initialization disables ASPM, detects whether MAC is already alive, checks/resets PCIe DMA hang state, runs the RTL8192E power sequence, initializes MAC/DMA descriptor addresses, downloads firmware, configures MAC/BB/RF tables, enables CCK/OFDM blocks, configures defaults, resets CAM, enables security, writes MAC address, re-enables ASPM, initializes BT coexistence, and runs IQK calibration. Runtime setters use `HW_VAR_*` switch dispatch for MAC address, BSSID, rates, SIFS/slot timing, RCR, RPWM, firmware LPS actions, join reports, AID, TSF correction, and keepalive. Link mode changes update MSR, beacon stop/resume, BSSID filtering, LED state, and beacon timing. Disable transitions stop link state, update LEDs, self-reset firmware when needed, run LPS/card-disable power sequences, reset MCU wrapper, and invalidate IQK state when BT coexistence is not active.

## State And Persistence Behavior
Persistent device-derived values are loaded from EFUSE/EEPROM into `rtl_efuse`: channel plan, tx-power tables, thermal meter, regulatory mode, board type, crystal cap, OEM/customer ID, and BT coexistence flags. Runtime state is cached in `rtlpci->receive_config`, `rtlpci->reg_bcn_ctrl_val`, `rtlpci->irq_mask`, `rtlhal->fw_ready`, firmware power-save state, ASPM state, `ppsc->rfpwr_state`, and security key buffers. Hardware CAM entries persist until explicitly cleared or power-cycled.

## Dependencies And Integration Points
This file depends on rt lwifi core helpers (`rtl_read_*`, `rtl_write_*`, CAM, EFUSE, PCI, base, regulatory, power-save helpers), local chip modules (`phy`, `dm`, `fw`, `led`, `pwrseq`, `reg`, `def`), mac80211 station/link metadata, PCIe DMA ring allocation, firmware H2C command definitions, and BT coexistence ops. It integrates upward through the driver ops table used by the rtlwifi core and downward through register writes and firmware commands.

## Risks
Most behavior is register-sequence sensitive. Risks include silent hardware misconfiguration from wrong constants, polling loops that continue after timeout without hard failure, a likely typo in `rtl92ee_bt_reg_init` where `reg_bt_sco` is assigned twice and `reg_bt_sco` overwrites the intended AMPDU field, concurrency hazards around firmware clock changes despite the lock, DMA hang recovery interacting with live rings, and EFUSE autoload failures leaving partial defaults. Security CAM programming depends on correct `key_len` state from upper layers.

## Test Signals
Useful signals are successful firmware download, `rtl92ee_hw_init` returning zero, interrupt recognition with expected ISR/HISRE masks, stable link mode transitions, beacon TX in AP/IBSS mode, successful reserved-page download, CAM entries visible through encrypted traffic, no PCIe DMA hang logs after reset, correct tx-power from EFUSE defaults and real EFUSE, LED transitions, suspend/resume no-ops not regressing power management, and RF/BT coexistence behavior under IPS/LPS.
