# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/sw.c

## Purpose
Provides the PCI module glue for RTL8821AE and RTL8812AE. It initializes software defaults, requests firmware, binds the chip-specific HAL operation table to the shared rtlwifi PCI core, exposes module parameters, and registers the PCI driver IDs.

## Important APIs, Types, And Functions
Key functions are `rtl8821ae_init_aspm_vars`, `rtl8821ae_init_sw_vars`, `rtl8821ae_deinit_sw_vars`, and `rtl8821ae_get_btc_status`. The central data objects are `rtl8821ae_hal_ops`, `rtl8821ae_mod_params`, `rtl8821ae_hal_cfg`, `rtl8821ae_pci_ids`, and `rtl8821ae_driver`. The HAL ops table wires callbacks for EEPROM, interrupts, hardware init/disable/suspend/resume, channel and bandwidth changes, TX/RX descriptor handling, security, H2C/C2H firmware commands, LED control, Bluetooth coexistence, and WoWLAN pattern support.

## Control Flow
PCI probe enters the shared `rtl_pci_probe` through `module_pci_driver`; that core uses `rtl8821ae_hal_cfg` and calls `rtl8821ae_init_sw_vars`. Initialization sets Bluetooth coexistence operations, dynamic-management defaults, HT/VHT capability fields, band defaults, receive and interrupt masks, WoWLAN mode flags, IPS/LPS options from module parameters, ASPM settings, and firmware buffers. It then selects firmware names based on `rtlhal->hw_type` and submits asynchronous normal and WoWLAN firmware requests. Deinit frees firmware buffers. Module parameters alter crypto, IPS/LPS, MSI, ASPM, interrupt-clear, watchdog, and debug behavior before probe.

## State And Persistence
State is stored in rtlwifi private structures: `rtlpriv->dm`, `rtlpriv->psc`, `rtlpriv->rtlhal`, `rtlpci`, `mac`, and firmware buffers allocated with `vzalloc`. Firmware loading is asynchronous and completes through callbacks outside this file. Module parameters persist for the module lifetime but not across unload/reload unless supplied again.

## Dependencies And Integration Points
Integrates with mac80211 through shared rtlwifi core ops, the PCI core through `rtl_pci_probe`/`rtl_pci_disconnect`, the power-management core through `SIMPLE_DEV_PM_OPS`, firmware loading through `request_firmware_nowait`, and chip-specific modules such as `hw.c`, `phy.c`, `dm.c`, `fw.c`, `trx.c`, `led.c`, and Bluetooth coexistence.

## Risks And Edge Cases
Firmware buffer cleanup is asymmetric: `rtl8821ae_deinit_sw_vars` only frees `wowlan_firmware` when `USE_SPECIFIC_FW_TO_SUPPORT_WOWLAN == 1`, while allocation always occurs here. The request-firmware error paths free buffers but do not always null both pointers. Because normal and WoWLAN firmware are requested asynchronously, remove paths must wait for completion before freeing. Incorrect `hw_type` detection selects the wrong firmware and RF/PHY tables. The default MSI and ASPM settings can expose platform-specific PCIe issues.

## Test Signals
Build the module with PCI support, verify both PCI IDs `0x8812` and `0x8821` bind, check firmware request success for normal and WoWLAN blobs, exercise suspend/resume, unload during firmware load, MSI on/off, ASPM on/off, IPS/LPS modes, TX/RX traffic, and WoWLAN wake patterns. Logs should show selected firmware names and no firmware allocation or request failures.
