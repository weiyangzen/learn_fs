# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7110.c

## Purpose
This is the common JH7110 pinctrl/GPIO/IRQ implementation shared by the SYS and AON controller instances. SoC-instance files provide pin tables, register bases, masks, IRQ handlers, and per-pin mux callbacks; this file implements the generic pinctrl, pinmux, pinconf, gpiochip, interrupt-chip, probe, and suspend/resume behavior.

## Important APIs, types, and functions
Packed DT pinmux decoding is handled by `jh7110_pinmux_pin/din/dout/doen/function()`. Exported helpers are `jh7110_set_gpiomux()`, `jh7110_pinctrl_probe()`, `jh7110_from_irq_desc()`, and `jh7110_pinctrl_pm_ops`. DT parsing is `jh7110_dt_node_to_map()`. Mux application is `jh7110_set_mux()` through the SoC callback `jh7110_set_one_pin_mux`. Pinconf uses `jh7110_padcfg_rmw()`, `jh7110_pinconf_get()`, and `jh7110_pinconf_group_set()`. GPIO callbacks include direction/get/set/set_config/add_pin_ranges. IRQ callbacks include ack, mask, mask_ack, unmask, set_type, and a shared `jh7110_irq_chip`.

## Control flow
Probe obtains `jh7110_pinctrl_soc_info` from the OF match, allocates state and optional saved registers, maps the MMIO resource, deasserts reset, optionally enables a clock, creates a pinctrl descriptor from instance pin data, registers pinctrl, registers a gpiochip with instance GPIO count, installs the instance chained IRQ handler and hardware-init callback, and enables pinctrl. DT parsing creates one group per child node under a pinctrl state, requiring a `pinmux` array, then adds a mux map and optional config map. Mux setting decodes each packed value and calls the instance callback. Generic GPIO mux writes update per-four-pin packed DOUT/DOEN registers and optional GPI selector registers. IRQ set-type maps requested edge/level semantics onto instance IRQ register bases and parent handler selection.

## State and persistence behavior
Software state is devm-managed `struct jh7110_pinctrl`. Raw spinlocks serialize register RMW; a mutex serializes dynamic group/function creation. With sleep PM enabled, suspend copies `info->nsaved_regs` 32-bit registers from the MMIO base into `saved_regs`, and resume writes them back. Pinconf and mux state otherwise persists in hardware registers until reset or later writes.

## Dependencies and integration points
The file depends on Linux pinctrl generic group/function helpers, generic pinconf, gpiolib IRQ helpers, platform reset/clock APIs, and JH7110 DT bindings. It integrates with instance files through `struct jh7110_pinctrl_soc_info`, which supplies pin descriptors, masks, register bases, callbacks, and saved-register count. It integrates with DT consumers via packed `pinmux` arrays and generic pinconf properties.

## Risks
`jh7110_pinconf_get()` returns 0 when padcfg callbacks are missing or a pin has no padcfg base, which can look like success without packing a result. The shared `jh7110_irq_chip` is a mutable static whose `.name` is assigned during probe, so multiple instances can overwrite the displayed name. IRQ polarity for level high/low is opposite-looking compared with JH7100 comments and must match JH7110 hardware. Suspend/resume blindly saves a register prefix; if future instances have sparse or side-effect registers in that range, restore may be unsafe.

## Test signals
Build and runtime tests should enable SYS and AON together, verify both gpiochips register with separate line counts, parse DT pinmux groups, apply generic pinconf, exercise GPIO input/output/set, dispatch IRQs through each instance handler, and suspend/resume while preserving mux and pad configuration. Debugfs pin output should show decoded `dout`, `doen`, and `din` for GPIO pins.
