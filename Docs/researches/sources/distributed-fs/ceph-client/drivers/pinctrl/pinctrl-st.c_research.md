# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-st.c

## Purpose
`pinctrl-st.c` implements the STMicroelectronics STi pin controller and GPIO bank driver. It models eight-pin PIO banks, syscfg-backed mux/config fields, optional retiming controls, GPIO direction/data registers, and GPIO IRQ handling for STiH407-related compatibles. It registers pinctrl, pinmux, pinconf, and gpiochip interfaces from one platform device.

## Important APIs, Types, and Functions
`struct st_pinctrl` is the top-level device state with the pinctrl device, bank array, parsed functions/groups, syscon regmap, SoC data, and optional irqmux base. `struct st_gpio_bank` embeds a `gpio_chip`, `pinctrl_gpio_range`, MMIO PIO base, `struct st_pio_control`, software edge-IRQ state, and a spinlock. `struct st_pctl_data` describes compatible-specific syscfg register offsets and retiming style. `struct st_pctl_group`, `struct st_pmx_func`, and `struct st_pinconf` hold DT-derived functions, groups, per-pin configs, and alt function numbers.

Key paths include `st_pctl_probe_dt()` for DT discovery, `st_gpiolib_register_bank()` for each GPIO bank, `st_parse_syscfgs()` for regmap-field setup, `st_pctl_parse_functions()` and `st_pctl_dt_parse_groups()` for ST `st,pins` parsing, `st_pmx_set_mux()` for mux writes, `st_pinconf_set()`/`st_pinconf_get()` for opaque ST pinconf words, and `__gpio_irq_handler()` plus parent chained handlers for IRQ dispatch.

## Control Flow
Probe validates OF, counts child nodes into GPIO banks and function groups, allocates arrays, resolves the `st,syscfg` syscon regmap, selects compatible data, optionally maps an `irqmux` resource and installs an irqmux chained parent handler, creates pin descriptors, then iterates children. GPIO-controller children become gpiochips with pin ranges, optional parent IRQs, and syscfg field mappings. Non-GPIO children become functions with child groups; each group parses properties under a `st,pins` subnode where each property encodes bank phandle, offset, mux, direction, and optional retime fields.

Pinmux state application is direct: for every pin in the selected group, `st_pmx_set_mux()` finds the bank control and writes a four-bit alternate function field in the bank's `alt` regmap field. GPIO direction requests force function zero and write PIO PC0/PC1/PC2 set/clear registers. Pinconf writes update output-enable, pull-up, open-drain, and retime fields depending on packed or dedicated style.

## State and Persistence
The hardware state lives in syscfg regmap fields and PIO MMIO registers. Parsed function/group arrays are devm lifetime allocations. There is no suspend/resume context save in this file; persistence relies on hardware retention or system-level restore. IRQ edge mode is software state in `bank->irq_edge_conf`, protected by `bank->lock`, because hardware supports level comparisons rather than true edge IRQs. GPIO line ownership is managed by gpiochip and pinctrl range integration, while mux/config writes are not globally serialized beyond the regmap/PIO operations and IRQ-edge spinlock.

## Dependencies and Integration Points
The driver integrates with syscon/regmap for mux and retiming controls, platform MMIO resources for PIO banks, OF aliases for bank numbering, OF IRQ resources for bank interrupts, optional top-level irqmux, gpiochip irq helpers, and pinctrl consumer maps. It uses `arch_initcall`, so ordering matters for early platform users. The DT contract is ST-specific: child GPIO nodes, `st,syscfg`, `st,bank-name`, optional `st,retime-pin-mask`, function/group child nodes, and `st,pins` property lists.

## Risks
The ST pinconf format is a driver-private packed `unsigned long`; it is not generic pinconf and requires exact DT macro values. `st_pctl_dt_calculate_pin()` depends on GPIO banks being registered before function parsing and on OF phandles matching bank fwnodes. Software edge emulation repeatedly flips comparison polarity and may lose transitions under high frequency or bouncing inputs. Several regmap-field setup failures are collapsed to `-EINVAL`, reducing diagnostics. GPIO bank base numbers are derived from `gpio` aliases and can collide if aliases are wrong. There is no explicit rollback for a top-level irqmux chained handler if a later probe step fails.

## Test Signals
Test with representative STiH407 DTs containing multiple GPIO banks, syscfg phandles, function groups, and retime masks. Validate mux register fields through regmap reads after selecting states, GPIO direction through PIO PC registers, pinconf debugfs formatting, packed/dedicated/no retime compatibles, level IRQs, rising/falling/both software edge IRQs, and irqmux fan-in. Failure tests should cover missing `st,syscfg`, missing GPIO banks, malformed `st,pins`, invalid IRQ resources, and inconsistent GPIO aliases.
