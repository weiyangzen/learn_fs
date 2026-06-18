# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lpc18xx.c

## Purpose
Implements the NXP LPC18xx/LPC43xx System Control Unit pin controller. It covers a large static pin/function table, pin muxing, analog ADC/DAC enable paths, USB1 and I2C0 special pins, generic pin configuration, and routing GPIO pins to the LPC GPIO pin interrupt selector.

## Important APIs, Types, and Functions
Core types are `struct lpc18xx_scu_data`, `struct lpc18xx_pmx_func`, and `struct lpc18xx_pin_caps`. Static tables define function IDs, function names, per-pin capability records, and `lpc18xx_pins`. Pinconf helpers include `lpc18xx_pconf_get`, `lpc18xx_pconf_set`, `lpc18xx_pconf_get_pin`, `lpc18xx_pconf_set_pin`, `lpc18xx_pconf_get_usb1`, `lpc18xx_pconf_set_usb1`, `lpc18xx_pconf_get_i2c0`, `lpc18xx_pconf_set_i2c0`, and GPIO interrupt selector helpers. Pinmux is handled by `lpc18xx_pmx_set`, and function-to-group maps are built by `lpc18xx_create_group_func_map`.

## Control Flow and State
Probe maps the SCU MMIO resource, obtains and enables the input clock, builds per-function group lists by scanning every pin capability, and registers a built-in platform pinctrl driver. Normal muxing finds the function index within the selected pin capability and writes it into `LPC18XX_SCU_PIN_MODE_MASK`. ADC/DAC functions first write analog-safe pin config and then set ENAIO registers. USB1 and I2C0 pins bypass normal muxing and use special register layouts for power, pull-down, input, slew, glitch filter, and Schmitt settings. Pinconf performs one read of the pin register, applies all requested configs to a local value, and writes once at the end except GPIO pin interrupt routing, which writes PINTSEL registers directly.

## Dependencies and Integration Points
Depends on the platform clock framework, MMIO, pinctrl generic DT parsing for per-pin maps, custom pinconf parameter `nxp,gpio-pin-interrupt`, and GPIO ranges to translate SCU pins to GPIO numbers for PINTSEL routing. The driver binds `nxp,lpc1850-scu` and is built in with `builtin_platform_driver`, so the clock remains enabled for the lifetime of the system.

## Risks and Test Signals
Risks include mistakes in the dense datasheet-derived pin table, special-case divergence for USB1/I2C0/analog pins, unsupported drive-strength or slew requests being accepted on the wrong pin type, PINTSEL bitfield mistakes, and no remove path to disable the clock. Test signals include per-function debugfs group membership, mux attempts for invalid functions producing `-EINVAL`, ADC/DAC enable register readback, pinconf get-after-set for pull/input/slew/Schmitt/drive strength, GPIO interrupt routing for all eight PINTSEL slots, and board boot tests for LPC18xx/LPC43xx peripherals.
