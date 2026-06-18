# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-single.c

## Purpose
`pinctrl-single.c` is a generic Open Firmware platform driver for "one register per pin" and "bit-per-mux" pin controllers, especially TI OMAP/DRA/AM padconf blocks and compatible simple padconf devices. It exposes muxing, optional generic pin configuration, optional GPIO-function mux switching, wake IRQ routing, and noirq suspend/resume context handling through the Linux pinctrl, pinmux, pinconf, irqdomain, and platform-driver APIs.

## Important APIs, Types, and Functions
The central state is `struct pcs_device`, which owns the MMIO base, register width, function mask/shift, pin table, GPIO function ranges, IRQ domain/list, SoC flags, raw spinlock, mutex, and function pointers for 8/16/32-bit register access. `struct pcs_soc_data` supplies compatible-specific flags and interrupt masks. `struct pcs_function` stores one dynamically parsed DT function, including `struct pcs_func_vals` register/value/mask entries and optional `struct pcs_conf_vals` pinconf metadata.

The pinctrl/pinmux entry points are `pcs_pinctrl_ops`, `pcs_pinmux_ops`, and, when enabled, `pcs_pinconf_ops`. `pcs_dt_node_to_map()` dispatches to `pcs_parse_one_pinctrl_entry()` for `pinctrl-single,pins` or `pcs_parse_bits_in_pinctrl_entry()` for `pinctrl-single,bits`. `pcs_set_mux()` applies mux values with raw spinlock protection. `pcs_request_gpio()` searches parsed `pinctrl-single,gpio-range` entries and writes the GPIO mux value. Pin configuration is parsed by `pcs_parse_pinconf()` and applied/read by `pcs_pinconf_set()`, `pcs_pinconf_get()`, and group variants.

IRQ support is centered on `pcs_irq_init_chained_handler()`, `pcs_irqdomain_map()`, `pcs_irq_handle()`, and `pcs_irq_set()`. Power management is handled by `pinctrl_single_suspend_noirq()`, `pinctrl_single_resume_noirq()`, `pcs_save_context()`, and `pcs_restore_context()`.

## Control Flow
`pcs_probe()` obtains compatible data, reads `pinctrl-single,register-width`, optional function mask/off values, and the bit-per-mux flag, patches legacy missing `#pinctrl-cells` when built in, maps the MMIO region, selects width-specific accessors, allocates one pin descriptor per register or bit slice, registers and enables pinctrl, parses GPIO function ranges, and optionally installs an IRQ domain and chained/shared parent handler. DT child nodes are parsed lazily through pinctrl core mapping callbacks when consumers request states; each node becomes a one-group, one-function mapping plus a config mapping if pinconf properties are present.

Mux setting loops over every parsed register/value entry, masks either the per-entry bit field or global function mask, writes the new value, and leaves other bits unchanged. Pinconf get/set first resolves the active pin mux setting back to the parsed function data, then interprets two-cell value/mask or four-cell value/enable/disable/mask DT properties as generic pinconf parameters.

## State and Persistence
Runtime state is mostly in MMIO registers and devm-owned structures. Parsed functions/groups are added dynamically to generic pinctrl registries and remain for the device lifetime. `pcs->gpiofuncs` and `pcs->irqs` are protected by the device mutex when updated. Register accesses that modify shared hardware state use `pcs->lock`. Compatible data may set `PCS_CONTEXT_LOSS_OFF`; in that case noirq suspend snapshots every mux register into `saved_vals`, then resume restores all registers before forcing the default pinctrl state. Interrupt enable state is held in hardware registers and rearmed through an optional platform callback.

## Dependencies and Integration Points
This driver depends on OF pinctrl helpers, generic pinctrl/pinmux registries, generic pinconf encodings, MMIO accessors, platform resources, optional platform data for OMAP PRM wake rearm, and irqdomain/chained IRQ APIs. Compatible strings select plain pinctrl, pinconf-capable pinctrl, shared wake IRQ variants, and context-loss variants. Consumer-facing integration is through device tree states using `pinctrl-single,pins`, `pinctrl-single,bits`, optional `pinctrl-single,gpio-range`, generic pinconf-like vendor properties, and standard pinctrl consumer state selection.

## Risks
The DT parser is permissive in some partial-failure paths: several loops break after invalid rows but still add functions/groups using the `found` count, so malformed DT may produce partial mappings. Pinconf get/set depends on a pin already having a mux setting; unconfigured pins return `-ENOTSUPP`. The width switch lacks an explicit error for unsupported widths, so a bad `register-width` can leave read/write callbacks unset. IRQ handling assumes one wake/status bit per mux register and uses register offsets as hwirqs, which is simple but narrow. Legacy property patching only works for built-in configurations. Context save uses `GFP_ATOMIC` and supports only 16/32/64-bit cases even though probe allows 8-bit accessors.

## Test Signals
Useful tests include DT binding probes for 8/16/32-bit register widths, one-register and bit-per-mux maps, invalid offsets, pinconf two-cell/four-cell properties, GPIO range request switching, shared and chained wake IRQ paths, suspend/resume with context-loss compatibles, and debugfs pin display. Kernel test signals are successful `devm_pinctrl_register_and_init()`, `pinctrl_enable()`, expected register writes under `pcs_set_mux()`, correct irqdomain mapping through `irq_create_of_mapping()`, and absence of partial groups when DT input is invalid.
