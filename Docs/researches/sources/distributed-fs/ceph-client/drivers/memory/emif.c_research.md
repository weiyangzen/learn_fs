# sources/distributed-fs/ceph-client/drivers/memory/emif.c

## Purpose
`emif.c` is the TI EMIF SDRAM controller driver. It configures LPDDR2 SDRAM power-management, ZQ calibration, temperature-alert handling, interrupt reporting, debugfs inspection, and platform or device-tree derived memory timing metadata for EMIF 4D and 4D5 controllers.

## Important APIs, Types, And Functions
`struct emif_data` is the central per-controller state: mapped base, device pointer, platform data, DDR node, temperature level, selected low-power mode, register-cache pointers, debugfs root, and list linkage. Global `emif1`, `device_list`, and `emif_lock` coordinate duplicate EMIF instances and multi-controller frequency-update workarounds.

Key helpers include `get_emif_bus_width()`, `set_lpmode()`, `do_freq_update()`, `get_addressing_table()`, `get_zq_config_reg()`, `get_temp_alert_config()`, and `get_pwr_mgmt_ctrl()`. Temperature logic is in `get_temperature_level()`, `setup_temperature_sensitive_regs()`, `handle_temp_alert()`, and `emif_threaded_isr()`. Device description paths are `of_get_memory_device_details()` and `get_device_details()`. Probe maps MMIO, performs one-time programming, initializes debugfs, disables stale interrupts, and requests a threaded IRQ.

## Control Flow
Probe builds `emif_data` from OF or platform data, validates DDR type/density/IO width/PHY combination, adds it to the global device list, maps registers, gets the IRQ, programs one-time settings, creates debugfs files, clears interrupts, and enables error/temperature IRQs. One-time programming chooses conservative low-power settings, writes ZQ calibration, reads MR4 temperature, writes temperature alert config, and programs fixed IntelliPHY shadow values.

On interrupts, the hard handler clears SYS and optional LL status registers. SYS temperature alerts call `handle_temp_alert()`. Rising temperature can immediately derate shadow timing registers and force a frequency-update sequence; falling temperature and very-high shutdown events are deferred to the threaded handler. The thread either powers off/restarts on over-temperature or reapplies temperature-sensitive timings under `emif_lock`.

## State And Persistence
Driver state is memory-resident and hardware-backed. `temperature_level`, `lpmode`, `curr_regs`, and `regs_cache` track derived runtime state. Debugfs exposes register-cache data and MR4 level. Hardware state includes power-management, ZQ, temperature-alert, interrupt-enable, and shadow timing registers. There is no explicit suspend/resume implementation here, but shutdown disables and clears interrupts. The driver adds EMIFs to `device_list` and sets `emif1`; remove only tears down debugfs, so list/global cleanup is a notable lifecycle gap.

## Dependencies And Integration Points
It depends on `emif.h` register definitions, `jedec_ddr.h` JEDEC tables, `of_memory.c` helpers, platform data from `linux/platform_data/emif_plat.h`, debugfs, IRQ threading, reboot/poweroff APIs, and device-tree properties such as `device-handle`, `phy-type`, `cs1-used`, `cal-resistor-per-cs`, `low-power-mode`, and `extended-temp-part`.

## Risks
Unsupported DDR geometry or PHY revisions fail probe. Missing or malformed DT timing data falls back to JEDEC defaults, which may be conservative but not board-optimal. Temperature handling can shut the system down for non-extended-temperature parts. Global list and `emif1` state are not unwound on remove. Some frequency-update functionality remains TODO, so low-power errata workarounds are partial. Register-cache calculation is represented by structures but not fully populated in this file, making integration with external PM/DVFS code important.

## Test Signals
Signals include probe success on `ti,emif-4d` and `ti,emif-4d5`, debugfs `regcache_dump` and `mr4`, interrupt tests for access errors and temperature alerts, validation of low-power-mode custom properties, fallback warnings for default timings, and over-temperature paths that call poweroff or restart. Removal and reprobe tests should watch stale `device_list` and `emif1` behavior.
