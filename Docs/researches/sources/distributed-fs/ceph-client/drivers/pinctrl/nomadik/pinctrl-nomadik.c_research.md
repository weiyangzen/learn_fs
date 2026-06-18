# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik.c

## Purpose
This is the common pinctrl, pinmux, and pinconf implementation for Nomadik-family pin controllers. SoC-specific files provide pins, groups, functions, and optional PRCM ALT-Cx metadata; this file registers the Linux pinctrl device, parses device-tree mux/config nodes, maps global pin numbers to `gpio-nomadik` banks, programs GPIO alternate-function and pin configuration registers, and coordinates low-power and glitch-avoidance behavior.

## Important APIs, types, and functions
Key state is `struct nmk_pinctrl`, containing the device, pinctrl device, selected SoC data, and optional PRCM base. Global integration points are `nmk_gpio_chips[]` and `nmk_gpio_slpm_lock`, shared with gpio-nomadik. Muxing is handled by `nmk_pmx_set()`, `__nmk_gpio_set_mode()`, `__nmk_gpio_set_mode_safe()`, `nmk_prcm_altcx_set_mode()`, and `nmk_prcm_gpiocr_get_mode()`. Pin configuration is handled by `nmk_pin_config_set()` and helpers for pull, direction, low-EMI, and sleep mode. Device-tree parsing is implemented by `nmk_pinctrl_dt_node_to_map()` and `nmk_pinctrl_dt_subnode_to_map()`.

## Control flow
`core_initcall(nmk_pinctrl_init)` registers a platform driver. Probe selects STN8815 or DB8500 SoC data from OF match data, follows `nomadik-gpio-chips` references to populate GPIO bank structures, maps optional `prcm`, fills the global pinctrl descriptor, and calls `devm_pinctrl_register()`. Runtime pinctrl calls then enumerate groups/functions from SoC data. A mux request validates the group's alternate setting, optionally enters the ALT-C glitch-avoidance sequence, enables each GPIO bank clock, lazily masks disabled IRQs, writes AFSLA/AFSLB, updates PRCM ALT-Cx bits when needed, and restores sleep registers.

## State and persistence behavior
The driver mutates hardware GPIO registers for mux, pull, direction, output, low-EMI, and sleep behavior. It also mutates shadow fields in `struct nmk_gpio_chip`, including `pull_up`, `lowemi`, and interrupt masks. PRCM GPIOCR writes persist outside the GPIO bank block. Suspend/resume delegates to `pinctrl_force_sleep()` and `pinctrl_force_default()`. The static pinctrl descriptor is reused across probes, so its `pins` and `npins` fields are filled during probe from the selected SoC data.

## Dependencies and integration points
The file depends on Linux pinctrl, pinmux, pinconf, GPIO, IRQ, OF/fwnode, clock, I/O, and platform-driver APIs. Its closest integration is `gpio-nomadik`, which provides bank clocks, register bases, IRQ domains, output helpers, sleep helpers, and bank population. Device-tree bindings use `function`, `groups`, `pins`, `ste,config`, and `ste,*` pin configuration properties.

## Risks
This driver is concurrency and hardware-sequence sensitive. ALT-C transitions temporarily alter sleep-mode state across all banks under `nmk_gpio_slpm_lock`; failure paths must restore clocks and SLPM registers correctly. `find_nmk_gpio_from_pin()` assumes bank-ordered GPIO numbering and can mis-map pins if bank descriptors are sparse or not populated as expected. Device-tree parsing does not reject out-of-range config values strongly; absent `pins`/`groups` properties surface as parse failures. `nmk_pin_config_get()` is unimplemented, so readback through generic pinconf is limited.

## Test signals
Signals include probe ordering with GPIO banks both pre-existing and populated through phandles, pinctrl debugfs group/function listings, muxing plain ALT-A/B/C and DB8500 ALT-Cx groups, GPIO request/free, lazy IRQ masking during mux-to-peripheral, suspend/resume default/sleep states, and dynamic-debug traces around PRCM GPIOCR changes and glitch-safe switching.
