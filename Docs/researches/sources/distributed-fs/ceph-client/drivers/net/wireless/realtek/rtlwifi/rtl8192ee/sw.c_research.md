# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/sw.c

## Purpose
This file is the PCI driver registration and rtlwifi HAL binding layer for the Realtek RTL8192EE 802.11n PCIe chipset. It initializes module parameters and software state, requests `rtlwifi/rtl8192eefw.bin`, exposes the PCI device table, and binds chip-specific callbacks into the shared rtlwifi PCI/mac80211 core through `struct rtl_hal_ops` and `struct rtl_hal_cfg`.

## Important APIs, Types, And Functions
`rtl92ee_init_aspm_vars()` seeds PCIe ASPM policy constants, including device/host ASPM masks, radio-off D3 behavior, and module-controlled ASPM support. `rtl92ee_init_sw_vars()` initializes Bluetooth coexistence, MSI support, dynamic-management defaults, transmit/receive configuration, interrupt masks, power-save defaults, early-mode state, firmware buffer allocation, and asynchronous firmware loading through `request_firmware_nowait()`. `rtl92ee_deinit_sw_vars()` releases the firmware buffer. `rtl92ee_get_btc_status()` advertises Bluetooth coexistence support.

The central data objects are `rtl8192ee_hal_ops`, `rtl92ee_mod_params`, `rtl92ee_hal_cfg`, `rtl92ee_pci_ids`, and `rtl92ee_driver`. The HAL ops table connects the generic rtlwifi core to RTL8192EE-specific EEPROM, interrupt, init, power, channel, descriptor, security, BB/RF, H2C, Bluetooth coexistence, and C2H rate-report handlers. The HAL config maps generic rtlwifi register and interrupt identifiers to 8192EE register constants and rate constants.

## Control Flow
Kernel module loading registers `rtl92ee_driver` via `module_pci_driver()`. PCI probe is handled by the shared `rtl_pci_probe()` using `rtl92ee_hal_cfg` from the matching PCI id. During software initialization, the file programs default state before hardware init: receive filter bits, interrupt masks, power-save policy, current band, MAC/PHY mode, and firmware storage. Firmware loading is asynchronous and handled by the shared `rtl_fw_cb`, so init must tolerate callback-driven firmware availability.

## State And Persistence
Persistent runtime state is stored in shared `rtl_priv`, `rtl_pci`, `rtl_hal`, `rtl_dm`, and `rtl_ps_ctl` objects. The file sets long-lived module parameters such as `swenc`, `ips`, `swlps`, `fwlps`, `msi`, `dma64`, `aspm`, `debug_level`, `debug_mask`, and `disable_watchdog`. The firmware buffer is allocated with `vzalloc(0x8000)` and freed only in deinit. Hardware register state itself is replayed through HAL callbacks during probe, resume, and restart rather than persisted here.

## Dependencies And Integration Points
This module integrates with Linux PCI, firmware loader, module parameter APIs, mac80211 through rtlwifi core, rtlwifi PCI transport, Realtek Bluetooth coexistence (`../btcoexist/rtl_btc.h`), and all sibling chip modules (`hw`, `phy`, `dm`, `fw`, `trx`, `led`, `table`). Firmware name and max size must match the blob expected by `fw.c`.

## Risks
The most important risks are registration-table drift and firmware lifetime bugs. If any HAL callback is mismatched with the descriptor or register layout, the generic rtlwifi core will call the wrong chip-specific behavior. The asynchronous firmware request means the firmware buffer must remain valid until callback completion. `dma64` defaults false despite 64-bit descriptor helpers elsewhere, so enabling it must be tested with the PCI transport. ASPM defaults and power-save module parameters can cause platform-specific wake, RF kill, or resume regressions.

## Test Signals
Useful signals include successful module load/probe on PCI id `0x818B`, firmware request completion for `rtlwifi/rtl8192eefw.bin`, correct registration of rtlwifi ops, interrupts arriving through configured masks, MSI on/off behavior, suspend/resume through `rtl_pci_suspend()` and `rtl_pci_resume()`, and clean unload without leaked firmware buffer. Runtime tests should exercise TX/RX, scan, association, Bluetooth coexistence paths, LPS/IPS, hardware crypto, and watchdog-disabled module option.
