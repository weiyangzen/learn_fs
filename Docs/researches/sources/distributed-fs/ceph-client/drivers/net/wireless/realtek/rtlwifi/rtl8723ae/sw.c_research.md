# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/sw.c

Purpose: `sw.c` is the module registration and software-configuration entry point for the RTL8723AE PCI driver. It initializes software variables, requests firmware, defines the HAL operation table, maps chip constants into common rtlwifi configuration, declares PCI IDs, exposes module parameters, and registers the PCI driver.

Important APIs/functions/data: `rtl8723e_init_sw_vars` initializes BT coexistence ops, DM defaults, transmit/receive config, IRQ masks, power-save policy, MSI/ASPM settings, firmware buffer, and async firmware request. `rtl8723e_deinit_sw_vars` frees firmware memory. `rtl8723e_get_btc_status` always enables BT coexistence support. `is_fw_header` checks firmware signature. `rtl8723e_hal_ops`, `rtl8723e_mod_params`, `rtl8723e_hal_cfg`, `rtl8723e_pci_ids`, and `rtl8723e_driver` bind the driver to rtlwifi and PCI.

Control flow: PCI probe from `module_pci_driver` uses `rtl_pci_probe`, which receives `rtl8723e_hal_cfg` from the device ID. rtlwifi calls `.init_sw_vars`, later `.read_eeprom_info` determines chip version, and firmware is requested asynchronously using either `rtlwifi/rtl8723fw.bin` or `_B.bin` for UMC B-cut. All runtime hardware operations dispatch through `rtl8723e_hal_ops`.

State and persistence: initializes persistent rtlwifi private state: DM flags, band type, MAC/PHY mode, RCR/TCR shadows, IRQ masks, IPS/LPS settings, ASPM constants, firmware buffer pointer/size, module parameters, and BT ops. Module parameters persist for the module lifetime. Firmware memory is vmalloc-backed and freed at deinit.

Dependencies/integration: integrates Linux module/PCI/firmware APIs with rtlwifi core and PCI glue. Depends on local hardware, PHY, TRX, LED, DM, FW, table, BT coexistence, and common rtl8723 modules. `rtl_hal_cfg.maps` bridges chip-specific constants from `reg.h` to generic rtlwifi code.

Risks: firmware selection depends on `rtlhal->version`, but `init_sw_vars` may run before chip version is fully known depending on rtlwifi probe ordering. If async firmware request fails, init returns failure after freeing the buffer. `get_btc_status` returning true forces BT coexistence path availability. The configuration is 2.4 GHz only despite some generic 5 GHz code paths elsewhere. Operation-table mismatches are high blast radius.

Test signals: module load/unload, PCI ID match for `10ec:8723`, successful async firmware load for both firmware names, module parameters affecting power save/MSI/ASPM/debug behavior, HAL operation dispatch during association and traffic, and no firmware-buffer leaks on request failure or unload.
