# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-xway.c

## Purpose
Implements the Lantiq XWAY-family pinctrl, pinmux, pinconf, and GPIO driver for ASE, Danube, xRX100, xRX200, and xRX300 SoCs. Large static tables describe each SoC's multifunction pins, groups, functions, and external interrupt pin mapping; shared MMIO code applies mux, GPIO, and pinconf changes.

## Important APIs, Types, And Functions
Important data includes `enum xway_mux`, `struct pinctrl_xway_soc`, per-SoC `ltq_mfp_pin` arrays, `ltq_pin_group` arrays, and `ltq_pmx_func` arrays. Runtime functions include `xway_mux_apply()`, `xway_pinconf_get()`, `xway_pinconf_set()`, `xway_pinconf_group_set()`, GPIO callbacks `xway_gpio_get/set/dir_in/dir_out/to_irq()`, and `pinmux_xway_probe()`.

## Control Flow
Probe maps the MMIO resource, selects SoC data from OF match data with Danube fallback, creates one pin descriptor per GPIO, fills the generic Lantiq `ltq_pinmux_info`, registers with `ltq_pinctrl_register()`, registers a GPIO chip, and adds a pinctrl GPIO range for older DTs lacking `gpio-ranges`. Mux application writes two alternate-function bits per pin through `GPIO_ALT0` and `GPIO_ALT1`, with special port-3 register offsets. Pinconf get/set reads or mutates open-drain, pull, and output direction registers.

## State And Persistence
Runtime state is mostly MMIO register state: ALT0/ALT1 mux bits, output, input, direction, open-drain, pull-enable, and pull-select registers. Driver metadata is stored in the global `xway_info`, `xway_pctrl_desc`, and `xway_chip` structures filled at probe time.

## Dependencies And Integration Points
Depends on the shared Lantiq pinctrl layer from `pinctrl-lantiq.h`, `lantiq_soc.h` register helpers, gpiolib, OF matching, and the Lantiq external interrupt helper `ltq_eiu_get_irq()`. It integrates with DT compatible strings `lantiq,ase-pinctrl`, `lantiq,danube-pinctrl`, `lantiq,xrx100-pinctrl`, `lantiq,xrx200-pinctrl`, and `lantiq,xrx300-pinctrl`.

## Risks
The driver uses global mutable state, so it assumes one active controller instance. Port-3 special-case offsets are easy to break when changing register definitions. Table accuracy is critical because the generic Lantiq layer trusts group/function mux values. GPIO `to_irq()` returns `-1` rather than a standard negative errno when no EXIN mapping exists.

## Test Signals
Signals include per-compatible probe, pinmux selection for representative functions on each SoC family, pinconf readback for open-drain and pulls, GPIO direction/value tests across ports including port 3, `gpio-ranges` and legacy range paths, and external IRQ mapping for every EXIN entry.
