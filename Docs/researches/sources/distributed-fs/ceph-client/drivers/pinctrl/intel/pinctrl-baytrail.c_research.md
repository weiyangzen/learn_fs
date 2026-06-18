# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-baytrail.c

## Purpose
Implements the Intel Bay Trail GPIO/pinctrl driver. Unlike newer Intel descriptor-only drivers, it provides custom pinmux, pinconf, GPIO, IRQ, firmware-workaround, and suspend/resume logic for the SCORE, NCORE, and SUS GPIO banks.

## Important APIs, Types, and Functions
Register macros cover `BYT_CONF0_REG`, `BYT_VAL_REG`, interrupt status, direct IRQ, debounce, pull, mux, direction, and restore masks. Static SoC tables define pins, groups, functions, communities, and ACPI UIDs. Core helpers include `byt_gpio_reg()`, `byt_set_mux()`, `byt_gpio_request_enable()`, `byt_gpio_set_direction()`, `byt_pin_config_get/set()`, GPIO callbacks, IRQ callbacks `byt_irq_ack/mask/unmask/type()`, `byt_gpio_irq_handler()`, direct IRQ sanity helpers, `byt_gpio_probe()`, `byt_pinctrl_probe()`, and PM callbacks `byt_gpio_suspend/resume()`.

## Control Flow
Probe obtains SoC data by ACPI UID, maps the MMIO resource, registers a custom pinctrl descriptor, then registers a gpiochip with optional chained IRQ handling. Pinctrl mux requests write `BYT_PIN_MUX` in CONF0. GPIO request may forcibly switch firmware-misconfigured pads to GPIO mux. Pinconf manages pulls and debounce. IRQ setup clears stale status, masks invalid direct IRQ configurations, and later dispatches pending bits from `BYT_INT_STAT_REG` to gpio irqdomain lines. Suspend saves selected CONF0/VAL bits and resume restores drifted mux, trigger, direction, and level fields.

## State and Persistence Behavior
Runtime state lives in `struct intel_pinctrl`, cloned community descriptors, gpiochip/irqdomain state, and `vg->context.pads` for sleep. A global `byt_lock` serializes MMIO and IRQ updates. Hardware registers hold mux, pull, debounce, level, direction, trigger, and direct-IRQ state.

## Dependencies and Integration Points
Depends on ACPI, gpiolib, pinctrl/pinmux/pinconf-generic, IRQ chips, PM, and shared Intel helper types. It integrates with firmware-created `INT33B2`/`INT33FC` platform devices, consumers using GPIO descriptors, and ACPI/board configurations that may already program direct IRQs.

## Risks
The driver deliberately works around firmware bugs by changing mux or clearing invalid direct IRQ state; regressions can be board-specific. Register fields are active-low for input/output enable, and output direction must be written atomically with level. Direct IRQ pins are excluded from normal GPIO IRQ handling. Suspend restore masks intentionally preserve only selected bits, so changing them can either lose firmware state or restore unsafe state.

## Test Signals
Probe for all three UIDs, GPIO request/direction/value operations, pull strength and debounce pinconf, edge/level IRQ delivery, direct IRQ sanity logs, debugfs GPIO output, suspend/resume state restoration, firmware-misconfigured pad warnings, and Bay Trail board ACPI devices using GPIO interrupts are key signals.
