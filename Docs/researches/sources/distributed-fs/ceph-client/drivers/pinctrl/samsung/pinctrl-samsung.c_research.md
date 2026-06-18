# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.c

## Purpose
This is the common Samsung pinctrl, pinmux, pinconf, GPIO, platform-driver, and power-management implementation. SoC-specific files provide bank descriptions and callbacks; this file turns those descriptions into registered pinctrl devices and gpiochips.

## Important APIs, Types, and Functions
The driver implements `pinctrl_ops`, `pinmux_ops`, `pinconf_ops`, and `gpio_chip` callbacks. Device-tree parsing is handled by `samsung_dt_node_to_map()` and `samsung_dt_subnode_to_map()`, which convert `samsung,pins`, `samsung,pin-function`, and config properties into pinctrl maps. Pinmux programming is in `samsung_pinmux_setup()`. Pin configuration read/write is centralized in `samsung_pinconf_rw()`. GPIO operations include `samsung_gpio_set()`, `samsung_gpio_get()`, direction callbacks, `samsung_gpio_to_irq()`, and `samsung_gpio_set_config()`.

Probe-time helpers include `samsung_pinctrl_get_soc_data()`, `samsung_banks_node_get()`, `samsung_pinctrl_register()`, `samsung_pinctrl_parse_dt()`, `samsung_gpiolib_register()`, and `samsung_pinctrl_probe()`. PM helpers are `samsung_pinctrl_suspend()` and `samsung_pinctrl_resume()`.

## Control Flow
At `postcore_initcall`, the platform driver is registered. Probe allocates `samsung_pinctrl_drv_data`, selects SoC data by `pinctrl` OF alias, maps memory resources, copies static bank data into runtime banks, links bank fwnodes, obtains optional parent IRQ and optional prepared `pclk`, initializes retention control, registers pinctrl, initializes SoC EINT callbacks, initializes pull-value encoding, registers one gpiochip per bank, enables pinctrl, and stores drvdata.

During pinctrl state selection, DT nodes are converted into maps. If a node has no children it is treated as one pin configuration node; otherwise each child is parsed. Each listed `samsung,pins` entry may produce a mux map and a config map. Pinmux and pinconf accesses locate the bank with `pin_to_reg_bank()`, enable the clock, lock the bank raw spinlock, update register fields, unlock, and disable the clock.

Suspend enables the clock, saves supported registers for banks with power-down config, invokes SoC suspend callbacks per bank, disables the clock, then enables retention. Resume enables the clock, invokes SoC resume callbacks, restores saved registers, disables the clock, then disables retention.

## State and Persistence
The main runtime state is `struct samsung_pinctrl_drv_data`, including mapped register bases, pin descriptors, dynamic pin groups/functions, bank array, GPIO chips, optional parent IRQ, optional clock, pull encoding values, and retention control. Per-bank state includes pin base, fwnode, gpiochip, irq_domain, irq_chip, raw spinlock, and `pm_save`. Pinctrl maps and pin/function arrays are devm-managed or freed through pinctrl callbacks.

## Dependencies and Integration Points
The file integrates with the Linux pinctrl core, pinmux/pinconf, gpiolib, irqdomain through bank IRQ domains, OF/property APIs, clock framework, platform driver core, and SoC-specific data from ARM, ARM64, S3C64xx, and S5PV210/Exynos helpers. The OF match table conditionally references exported `*_of_data` symbols based on Kconfig.

## Risks
Pin-to-bank lookup assumes bank arrays are ordered by increasing pin ranges and the input pin is valid. `samsung_pinconf_group_set()` ignores return values from per-pin config writes, so a later pin failure can be hidden. DT parsing logs malformed optional config properties but continues, which can leave partially applied maps. Clock enable failures are propagated in most runtime paths but EINT callback return values from SoC init are not checked in probe. Bank fwnode matching relies on exact bank names or `<bank>-gpio-bank` child names.

## Test Signals
Important signals include successful probe for every compatible, correct generated pin names, pinctrl map parsing for flat and nested DT nodes, mux writes on banks with one and two CON registers, pinconf get/set across all supported config types, GPIO direction/value and bias config, gpio-to-IRQ mapping, suspend/resume register preservation, clock failure handling, and missing bank node warnings in invalid DTBs.
