# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eic7700.c

## Purpose
This platform driver implements pinctrl, pinmux, and pinconf for the ESWIN EIC7700 SoC. It describes 164 pins, per-pin function slots, generic pin configuration fields, GPIO request/direction integration, and a probe-time RGMII voltage mode setup derived from a `vrgmii` regulator.

## Important APIs, Types, and Functions
`struct eic7700_pin` stores up to eight function selectors per pin. `struct eic7700_pinctrl` stores MMIO base, pinctrl descriptor, and a flexible array of `struct pinfunction` records. Register fields include input enable, pull-up/down, drive strength, Schmitt trigger, and function select in each per-pin 32-bit word. Key callbacks are group accessors, `eic7700_pin_config_get`, `eic7700_pin_config_set`, `eic7700_set_mux`, `eic7700_gpio_request_enable`, `eic7700_gpio_disable_free`, `eic7700_gpio_set_direction`, `eic7700_pinctrl_init_function_groups`, and `eic7700_pinctrl_probe`.

## Control Flow and State
Probe allocates state sized for all functions, maps MMIO, obtains `vrgmii`, reads its voltage, programs both RGMII mode registers for 1.8 V or 3.3 V, fills the pinctrl descriptor, builds function-to-group membership by scanning every pin's function slots, registers and initializes pinctrl, then enables it. Muxing validates that the requested function appears in the selected pin's function slot array, then writes that slot index to the `FUNC_SEL` field. GPIO request selects `F_GPIO`; GPIO free tries to select `F_DISABLED`; GPIO direction toggles the input-enable bit.

## State and Persistence Behavior
All hardware state is MMIO and arranged as one register per pin plus separate RGMII mode registers. Function group arrays are generated once at probe and devm-managed. Pinconf get returns `-EINVAL` when a supported boolean config is currently false, matching common generic-pinconf conventions. Drive strength encoding differs for RGMII/LPDDR reference clock pins versus other pins.

## Dependencies and Integration Points
The driver depends on platform bus, OF compatible `eswin,eic7700-pinctrl`, regulator framework, MMIO helpers, pinctrl, pinmux, and generic pinconf. It does not register a gpiochip; GPIO operation is through pinmux hooks used by a GPIO controller integration.

## Risks
The static per-pin function table is large and board-critical. `eic7700_gpio_disable_free` calls `eic7700_set_mux` with `F_DISABLED`, but many pins do not list disabled as a valid slot, so free can log errors or fail silently through a void callback. The driver accepts only exactly 1.8 V or 3.3 V for `vrgmii`; regulator rounding or unavailable voltage causes probe failure. Relaxed unlocked RMW on per-pin registers can race with concurrent pinconf/mux operations.

## Test Signals
Tests should validate regulator-voltage-dependent RGMII mode writes, pinctrl registration and `pinctrl_enable`, function group counts for each selector, valid and invalid mux requests, GPIO request/free on pins with and without disabled slots, pinconf get/set for bias, drive strength, input enable, and Schmitt, and DT states for major peripherals such as RGMII, I2C, UART, SPI, SDIO, PWM, MIPI CSI, and USB.
