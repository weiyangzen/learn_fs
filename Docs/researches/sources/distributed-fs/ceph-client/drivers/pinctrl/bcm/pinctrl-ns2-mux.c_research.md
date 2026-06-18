# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns2-mux.c

Purpose: Broadcom Northstar2 IOMUX pinctrl driver for group-based muxing plus per-pin generic pinconf for pins with pad configuration registers. It registers the `brcm,ns2-pinmux` platform driver at `arch_initcall`.

Important APIs/types/functions: `struct ns2_pinctrl`, `ns2_pin`, `ns2_pin_group`, `ns2_pin_function`, and `ns2_mux_log` describe controller state, pins, groups, functions, and conflict tracking. `ns2_pinctrl_ops`, `ns2_pinmux_ops`, and `ns2_pinconf_ops` implement Linux pinctrl, pinmux, and generic pinconf callbacks. `ns2_pinmux_set()` performs masked register updates; `ns2_pin_config_get/set()` handle bias, drive strength, slew rate, and input-enable.

Control flow: probe maps three MMIO resources, initializes the mux log, builds pin descriptors with `drv_data`, binds static group/function tables, then registers the pinctrl device. Device-tree maps use `pinconf_generic_dt_node_to_map_pin`. Mux selection validates selectors, rejects conflicting reuse of the same mux field, selects base0/base1, then updates the target offset under a spinlock.

State and persistence: state lives in hardware mux/pad registers plus an in-memory `mux_log` used only for the running instance. Pinconf persists in MMIO until hardware reset; devm allocations are released on device teardown. Pins 0-62 have `base == -1`, so pinconf operations return `-ENOTSUPP`.

Dependencies/integration: depends on platform resources, OF compatible data, Linux pinctrl core, generic pinconf helpers, and `pinctrl-utils`. Integrates with downstream NAND/NOR/PCIe/UART/PWM consumers through DT pin states.

Risks: static table/register-field mistakes can silently mux the wrong shared pins. Conflict tracking prevents divergent runtime selections but does not reconcile bootloader state. `pinctrl_register()` is non-devm while no remove path unregisters, acceptable for arch-init built-in style but worth checking if modularized.

Test signals: boot with `brcm,ns2-pinmux`, inspect pinctrl debugfs group/function listings, apply DT states for each mux group, verify unsupported pinconf on mfio pins, and scope/register-check pad configuration changes for pins 63-118.
