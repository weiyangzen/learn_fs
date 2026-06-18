# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/sw.c

## Purpose
This is the RTL8192CE PCI driver registration and HAL-configuration file. It initializes software variables, requests firmware, defines module parameters, maps CE hardware operations into rtlwifi HAL ops, publishes register map constants, declares PCI IDs, and registers the PCI driver.

## Important APIs, Types, And Functions
Important functions and data include `rtl92c_init_aspm_vars()`, `rtl92c_init_sw_vars()`, `rtl92c_deinit_sw_vars()`, `rtl8192ce_hal_ops`, `rtl92ce_mod_params`, `rtl92ce_hal_cfg`, `rtl92ce_pci_ids`, `rtlwifi_pm_ops`, and `rtl92ce_driver`. Module metadata names three firmware files and parameters `swenc`, `ips`, `swlps`, `fwlps`, `aspm`, `debug_level`, and `debug_mask`.

## Control Flow
PCI probe from rtlwifi receives `rtl92ce_hal_cfg` via the device table. Software init sets BT registry defaults, DM defaults, TX/RX configs, band/mode, interrupt masks, power-save defaults, ASPM constants, allocates a 16 KiB firmware buffer, chooses firmware by chip version, and starts asynchronous firmware request. HAL ops then route rtlwifi core calls to CE-specific implementations in `hw.c`, `phy.c`, `rf.c`, `dm.c`, `led.c`, and `trx.c`.

## State And Persistence
Runtime state initialized here includes `rtlpriv->dm`, `rtlpci->transmit_config`, `receive_config`, `irq_mask`, `rtlhal` band/macphy mode, `rtl_ps_ctl` power-save knobs, ASPM policy, and `rtlhal.pfirmware`. Module parameters are read at load time but no persistent configuration is written.

## Dependencies And Integration Points
It depends on Linux module/PCI firmware APIs, rtlwifi core and PCI glue, CE hardware/PHY/RF/DM/LED/TRX modules, and common RTL8192C firmware/PHY helpers. `module_pci_driver()` binds the driver to PCI device IDs 0x8191, 0x8178, 0x8177, and 0x8176.

## Risks And Edge Cases
Firmware selection depends on chip version already being read before software init uses it; probe ordering must preserve that assumption. Asynchronous firmware request failure frees the firmware buffer and fails init. The HAL map table must stay synchronized with `reg.h` and rtlwifi generic map indices. Module parameters change power/security behavior and can hide hardware crypto or power-save bugs.

## Test Signals
Successful module load, firmware request callback, correct firmware filename, PCI ID binding, module parameter effects, HAL callbacks invoked by rtlwifi core, suspend/resume through `rtl_pci_suspend/resume`, and clean deinit freeing firmware are key signals.
