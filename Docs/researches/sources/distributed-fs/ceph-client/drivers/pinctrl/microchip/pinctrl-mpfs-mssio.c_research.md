# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/pinctrl-mpfs-mssio.c

## Purpose
This driver implements PolarFire SoC MSSIO pinmux and pin configuration for 38 pins across MSS banks 4 and 2. It supports per-pin mux function selection, bias, drive strength, Schmitt input, low-power/persist settings, bank voltage selection, and Microchip-specific clamp/IBUF mode bindings.

## Important APIs, Types, and Functions
- Register masks define pad mux, IOCFG fields, bank voltage fields, low-power bits, clamp, lockdown, weak pull-up/down, hysteresis, and drive strength.
- `struct mpfs_pinctrl` stores pinctrl device, regmap for pinctrl syscon, sysreg regmap for bank voltage, mutex, and descriptor.
- `mpfs_pinctrl_drive_strengths` maps hardware drive encodings to mA values; `mpfs_pinctrl_bank_voltages` maps sysreg encodings to microvolts.
- Conversion helpers map requested drive strength and voltage to hardware encodings and back.
- `mpfs_pinctrl_pin_to_iomux_reg()/offset()` and `mpfs_pinctrl_pin_to_iocfg_reg()/offset()` translate pin numbers to register fields.
- `mpfs_pinctrl_set_mux()` uses generic groups and per-pin function strings from DT to write mux functions.
- `mpfs_pinctrl_pinconf_get()` reads generic and custom configs.
- `mpfs_pinctrl_pinconf_generate_config()` converts packed configs into IOCFG register bits and optional bank voltage.
- `mpfs_pinctrl_pinconf_set()` and group set write IOCFG fields and bank voltage.
- `mpfs_pinctrl_probe()` gets parent and sysreg regmaps, initializes descriptor operations and custom params, and registers pinctrl.

## Control Flow
Device-tree mapping uses `pinctrl_generic_pins_function_dt_node_to_map`, so groups and functions are created by generic helpers from DT. Mux setting retrieves a generic group, maps each function string through `mpfs_pinctrl_function_map()`, computes register/offset, and updates the pad mux field. Pinconf set builds a replacement IOCFG value from supplied configs, writes the 15-bit field for each target pin, then updates bank voltage if requested. Pinconf get reads the current field and validates whether the requested config is active.

## State and Persistence
Driver state is `struct mpfs_pinctrl`; hardware mux/config/voltage state persists in syscon registers. The code initializes a mutex but does not use it around register updates. There is no suspend/resume path. Group voltage changes assume all pins in a group belong to the same bank, matching a driver comment about MSS Configurator constraints.

## Dependencies and Integration Points
The driver integrates with parent syscon regmap, the `microchip,mpfs-sysreg-scb` sysreg compatible for bank voltage, Linux generic pinctrl/pinmux/pinconf, custom pinconf parameters, and the `microchip,mpfs-pinctrl-mssio` compatible.

## Risks
`mpfs_pinctrl_pinconf_generate_config()` starts from zero rather than the current IOCFG field, so a partial pinconf update clears unspecified fields. Bank voltage conversion uses a sorted table with an unused sentinel; requests above supported voltages return `-EINVAL`. `MPFS_PINCTRL_LOCKDOWN` is readable but not listed in `mpfs_pinctrl_custom_bindings`, so external DT naming for that custom config is not exposed here. Register write return values from some helpers are not checked. The unused mutex suggests intended serialization that is not enforced beyond regmap behavior.

## Test Signals
Build with `CONFIG_PINCTRL_POLARFIRE_SOC` and validate DT states that assign pin groups and per-pin functions. Test pinconf round trips for pull-up, pull-down, bus-hold, bias-disable, drive-strength, Schmitt, persist, low-power, power-source, clamp, and ibufmd. Hardware validation should read IOCFG and bank voltage registers after DT application and verify group updates across both bank 4 and bank 2.
