# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.c

## Purpose
This is the common MA35 pinctrl, pinmux, pinconf, GPIO, and GPIO-IRQ implementation. SoC-specific files provide pin descriptors and an MFP offset/shift to pin-number decoder; this file parses device-tree function/group nodes, programs shared multi-function pin registers through a syscon regmap, registers per-bank GPIO chips, and implements generic pin configuration for pulls, drive strength, Schmitt trigger, slew rate, output enable, and power source.

## Important APIs, types, and functions
The exported entry points are `ma35_pinctrl_probe()`, `ma35_pinctrl_suspend()`, and `ma35_pinctrl_resume()`. Important internal types are `struct ma35_pinctrl`, `struct ma35_pin_ctrl`, `struct ma35_pin_bank`, and `struct ma35_pin_setting`. Key callbacks include `ma35_pinctrl_dt_node_to_map_func()`, `ma35_pinmux_set_mux()`, GPIO direction/get/set/request helpers, IRQ helpers `ma35_irq_gpio_ack/mask/unmask/irqtype()` and `ma35_irq_demux_intgroup()`, and pinconf helpers for pull, drive, Schmitt, slew, output, and power source.

## Control flow
`ma35_pinctrl_probe()` validates SoC info, allocates controller state and a pinctrl descriptor, obtains the system-controller regmap from the `nuvoton,sys` phandle, discovers GPIO child nodes, parses non-GPIO child nodes into functions and groups, registers and enables pinctrl, then registers each valid GPIO bank. A mux request walks the selected group's `ma35_pin_setting` entries and writes each 4-bit MFP field. A GPIO request clears that pin's MFP field to GPIO mode. IRQ flow reads a bank `INTSRC`, dispatches set bits through the gpio irq domain, and acknowledges by writing the source bit.

## State and persistence behavior
Runtime state includes parsed group/function arrays, per-bank register bases, clocks, IRQ numbers, irq type/enable shadows, and the shared syscon regmap. Hardware state persists in MFP registers, GPIO mode/output/pull/drive/slew/Schmitt/power registers, and GPIO interrupt registers. Clocks are prepared and enabled for valid banks during discovery and remain enabled for GPIO/pinctrl operation. Suspend/resume forces pinctrl sleep/default states.

## Dependencies and integration points
The driver depends on Linux pinctrl/pinmux/pinconf, generic pinconf DT parsing, gpiolib, gpio irqchip helpers, IRQ core, clocks, OF/fwnode, syscon/regmap, and MMIO. Device tree supplies GPIO bank child nodes and function/group nodes with `nuvoton,pins` triples of MFP register index, port shift, and mux value. It integrates with SoC data through `struct ma35_pinctrl_soc_info`.

## Risks
There are several correctness risks. `ma35_pinctrl_parse_functions()` uses a static `grp_index`, which is safe for a single probe path but would be fragile if multiple MA35 controllers probed in one boot. `ma35_pinctrl_dt_node_to_map_func()` can leak the parent reference on the `of_get_parent()` error path after allocating maps. GPIO child discovery increments `id` without checking against `MA35_GPIO_BANK_MAX`. Pinconf helpers assume valid bank register bases derived from global pin numbers. IRQ type handling maps level-high/level-low to `handle_edge_irq`, which deserves hardware validation.

## Test signals
Test with MA35D1 device trees that define GPIO children and multiple function nodes. Verify pinctrl debugfs functions/groups, mux writes to syscon MFP registers, GPIO request fallback to mux value 0, GPIO direction/output/input paths, interrupt rising/falling/both behavior, generic pinconf read/write for pulls, drive strengths at 1.8 V and 3.3 V, Schmitt, slew, power source, and suspend/resume state transitions.
