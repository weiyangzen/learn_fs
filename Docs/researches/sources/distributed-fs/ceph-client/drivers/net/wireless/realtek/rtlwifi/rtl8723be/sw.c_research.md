<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/sw.c

## Purpose
Registers the RTL8723BE PCI driver with rtlwifi and the kernel PCI/module core. It initializes software defaults, power-management settings, firmware loading, HAL operation callbacks, register maps, module parameters, PCI IDs, and module metadata.

## Important APIs, Types, And Functions
- Initialization helpers: `rtl8723be_init_aspm_vars`, `rtl8723be_init_sw_vars`, `rtl8723be_deinit_sw_vars`, `rtl8723be_get_btc_status`, and `is_fw_header`.
- HAL operation table `rtl8723be_hal_ops` wires rtlwifi callbacks for EEPROM, interrupts, hardware init/disable/suspend/resume, network type, QoS, beacon handling, rate tables, TX/RX descriptors, channel/RF operations, watchdog, security, BB/RF accessors, H2C firmware commands, BTC status, and firmware header detection.
- HAL configuration `rtl8723be_hal_cfg` maps generic rtlwifi register roles, EFUSE roles, CAM/security roles, interrupt bits, and rate constants to RTL8723BE register definitions.
- Module parameters include `swenc`, `debug_level`, `debug_mask`, `ips`, `swlps`, `fwlps`, `msi`, `aspm`, `disable_watchdog`, and `ant_sel`.
- PCI registration uses `rtl8723be_pci_ids`, `SIMPLE_DEV_PM_OPS`, `rtl_pci_probe`, `rtl_pci_disconnect`, and `module_pci_driver`.

## Control Flow
At module load, `module_pci_driver` registers a PCI driver for Realtek device `0xB723`. During probe, rtlwifi calls `rtl8723be_init_sw_vars`, which initializes Bluetooth coexistence hooks, dynamic-management defaults, transmit/receive configuration masks, interrupt masks, IPS/LPS/MSI/ASPM module settings, band and MAC/PHY mode, firmware buffer allocation, and asynchronous firmware request for `rtlwifi/rtl8723befw_36.bin`. Later rtlwifi invokes the `rtl8723be_hal_ops` callbacks for hardware bring-up, TX/RX, scanning, power, security, and teardown. Deinit frees the firmware buffer.

## State And Persistence
The file initializes persistent driver state in `rtl_priv`, `rtl_pci`, `rtl_mac`, `rtl_hal`, PHY, DM, PSC, and BT coexistence structures. It allocates `rtlhal.pfirmware` with `vzalloc`, records `max_fw_size`, sets interrupt masks and receive/transmit configs, stores module parameter values, and registers immutable HAL config tables. Firmware is requested asynchronously and stored until deinit.

## Dependencies And Integration Points
Depends on rtlwifi core, PCI support, shared RTL8723 common firmware/PHY/DM helpers, chip-specific hardware/PHY/DM/FW/TRX/LED/table modules, and Bluetooth coexistence ops. Kernel integration points are firmware loading, module parameters, PCI device matching, and PM callbacks.

## Risks And Edge Cases
Asynchronous firmware loading means hardware init must tolerate firmware not ready until the callback completes. Firmware buffer allocation failure aborts probe setup. Incorrect HAL op wiring can misroute descriptor handling, interrupts, or RF access. Register-map mistakes affect generic rtlwifi helpers. Module parameter defaults shape power saving and ASPM behavior, so changes can cause hangs, missed interrupts, higher power use, or resume failures. The firmware header check accepts signatures masked by `0xfff0`, so it must stay aligned with firmware format.

## Test Signals
Signals include module insertion/removal, PCI probe on `0xB723`, firmware request success and fallback naming behavior, hardware init through the HAL ops table, interrupt delivery, TX/RX traffic, suspend/resume, module parameter parsing, Bluetooth coexistence presence, and no leaks from repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/sw.c -->
