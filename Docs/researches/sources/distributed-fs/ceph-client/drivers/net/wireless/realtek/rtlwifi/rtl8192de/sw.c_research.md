# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.c

## Purpose
Provides the RTL8192DE PCI module wiring. It initializes software variables, declares module parameters and firmware, maps chip registers and rates into the rtlwifi abstraction, installs the `rtl_hal_ops` callback table, declares PCI IDs, and registers/unregisters the PCI driver.

## Important APIs, Types, And Functions
`rtl92d_init_aspm_vars()` configures PCI ASPM policy constants. `rtl92d_init_sw_vars()` initializes DM defaults, current channel, dual-MAC buffer behavior, TX/RX configuration masks, IRQ masks, power-save settings, early mode, per-TID wait queues, firmware buffer allocation, and asynchronous firmware request. `rtl92d_deinit_sw_vars()` frees firmware memory and purges wait queues. `rtl8192de_hal_ops` is the central integration object for PCI probe, MAC/PHY/RF operations, TX/RX descriptor handling, security, channel/bandwidth, watchdog, LED, and calibration. `rtl92de_hal_cfg` maps abstract rtlwifi indices to RTL8192DE register/rate constants. Module init/exit register the `pci_driver`.

## Control Flow
On module load, `rtl92de_module_init()` registers `rtl92de_driver`. `rtl_pci_probe()` receives matching device IDs and uses `rtl92de_hal_cfg`, which points back to the callbacks in this file. Software initialization sets default operating state, allocates a firmware buffer, and starts `request_firmware_nowait()` for `rtlwifi/rtl8192defw.bin`. Later core flows call the configured operations for hardware initialization, interrupt control, networking mode changes, descriptor fill/query, channel switching, RF power, and calibration. Module exit unregisters the PCI driver.

## State And Persistence
Persistent driver state initialized here includes DM flags, `current_channel`, dual-MAC `disable_amsdu_8k`, PCI RX buffer size, `transmit_config`, `receive_config`, IRQ masks, power-save knobs, firmware buffer pointer/size, `fwctrl_psmode`, early-mode flag, and per-TID skb queues. The file also defines global spinlocks `globalmutex_power`, `globalmutex_for_fwdownload`, and `globalmutex_for_power_and_efuse` used by dual-MAC power and firmware/efuse code.

## Dependencies And Integration Points
Depends on the rtlwifi core, PCI glue, rtl8192d common modules, and local PHY/DM/HW/TRX/LED implementations. It integrates with Linux PCI and module infrastructure, request_firmware, mac80211 through rtlwifi, and kernel PM via `SIMPLE_DEV_PM_OPS`.

## Risks
Asynchronous firmware loading requires the allocated firmware buffer to survive until callback completion and deinit. The `rtl_hal_cfg` callback table is dense; incorrect function assignment can cause failures far from probe. Module parameters directly alter power-save, crypto, ASPM, and debug behavior. Dual-MAC state relies on global spinlocks declared here, making cross-file ordering and lock use important.

## Test Signals
Build the module, verify PCI IDs bind to RTL8192DE hardware, confirm firmware request and callback success, and exercise module unload/reload for firmware buffer and queue cleanup. Runtime signals include interrupts, TX/RX, scan/association, suspend/resume, ASPM behavior, debug module parameters, and dual-MAC operation without lock warnings.
