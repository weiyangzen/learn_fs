<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.c

## Purpose
Implements the shared Allwinner/sunxi pinctrl, pinmux, pin configuration, GPIO, and GPIO-backed IRQ controller logic. SoC-specific sunxi files provide pin/function descriptors; this file turns those descriptors and device-tree nodes into Linux pinctrl, gpiolib, regulator, and irqdomain registrations.

## Important APIs, Types, And Functions
Key entry points are `sunxi_pinctrl_init_with_flags`, `sunxi_pinctrl_init`, and `sunxi_pinctrl_dt_table_init` from the companion header. Register helpers `sunxi_mux_reg`, `sunxi_data_reg`, `sunxi_dlevel_reg`, and `sunxi_pull_reg` calculate banked MMIO offsets. Pinctrl callbacks include `sunxi_pctrl_dt_node_to_map`, `sunxi_pconf_get/set`, `sunxi_pmx_set_mux`, `sunxi_pmx_gpio_set_direction`, and GPIO callbacks for direction, get/set, OF translation, and `to_irq`. IRQ logic is handled by `sunxi_pinctrl_irq_set_type`, mask/unmask/ack helpers, chained handler `sunxi_pinctrl_irq_handler`, and `sunxi_pinctrl_irq_domain_ops`.

## Control Flow
Probe allocates `struct sunxi_pinctrl`, maps MMIO, derives register layout flags, builds runtime group/function state from descriptor pins, registers pinctrl, registers a gpiochip and pin ranges, enables the APB clock, creates an IRQ domain, maps each hardware IRQ, masks/clears banks, installs chained parent handlers, and optionally programs debounce clocks. Device-tree pin state parsing accepts generic and legacy Allwinner properties, validates that each pin supports the requested function, and emits mux/config maps. GPIO IRQ requests lock the GPIO line, optionally move reset mux state to input, then mux the pin to its IRQ function.

## State And Persistence Behavior
Driver state persists in `struct sunxi_pinctrl`: MMIO base, descriptor pointer, runtime groups/functions, irq map arrays, irq domain, gpiochip, pinctrl device, flags, register layout parameters, spinlock, and per-bank regulator/refcount state. Hardware state persists in mux, data, drive, pull, IO-bias, IRQ config/control/status, and debounce registers. The code does not save/restore registers itself; it relies on normal pinctrl states and platform power handling.

## Dependencies And Integration Points
Integrates with Linux pinctrl core, gpiolib, irqdomain/chained IRQs, regulators named `vcc-p<bank>`, device tree pinctrl bindings, optional APB/oscillator clocks, and Allwinner DT binding constants. SoC descriptor files provide pins, functions, variants, IRQ bank maps, and IO-bias behavior.

## Risks And Edge Cases
Register offset calculation is layout-sensitive, especially D1/new layouts and bank K at `0x500`. Function lookup must respect pin and function variants or unsupported mux values can be exposed. The shared spinlock protects read-modify-write MMIO paths but not all IO-bias writes use identical locking. Regulator refcounts are per logical bank and depend on correct pin base/bank arithmetic. IRQ readback may temporarily remux lines on SoCs with `irq_read_needs_mux`.

## Test Signals
Probe on old and new register layouts, DT parsing for generic and legacy properties, GPIO request/free regulator refcounts, pin mux changes, drive and pull get/set, GPIO input/output, gpio-to-irq mapping, edge and level IRQ delivery, wake propagation, debounce programming, variant-specific pins/functions, and failure injection for clocks, regulators, IRQs, and pinctrl/gpio registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sunxi.c -->
