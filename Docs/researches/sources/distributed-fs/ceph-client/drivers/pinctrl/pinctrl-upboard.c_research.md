# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-upboard.c

## Purpose
Implements the UP Board HAT pin controller for FPGA-backed header pins on UP and UP Squared boards. It exposes pinctrl/pinmux state for board functions such as I2C, SPI, UART, I2S, PWM, and ADC, and also registers a sparse GPIO forwarder so header pins can be requested as Linux GPIOs backed by an external GPIO provider.

## Important APIs, Types, And Functions
Key types are `enum upboard_pin_mode`, `struct upboard_pin`, `struct upboard_pingroup`, `struct upboard_pinctrl_data`, and `struct upboard_pinctrl`. Static UP and UP2 tables define pin descriptors, header pin order, pin groups, per-pin GPIO direction modes, and `struct pinfunction` entries. Runtime operations include `upboard_pinctrl_set_mux()`, `upboard_pinctrl_pin_get_mode()`, `upboard_gpio_request()`, `upboard_gpio_direction_input()`, `upboard_gpio_direction_output()`, and `upboard_pinctrl_probe()`.

## Control Flow
Probe obtains the parent `upboard_fpga`, selects UP or UP2 tables from `fpga_data->type`, rejects unsupported DMI boards, allocates one `regmap_field` set per pin for function-enable, GPIO-enable, and direction bits, registers pinctrl, adds generic groups/functions, registers DMI-provided default mappings, selects the default state, enables the pinctrl device, and finally registers the GPIO forwarder plus sparse pin range. Pinmux selection iterates group pins, switches function-capable pins through `funcbit`, otherwise enables GPIO mode and sets the expected direction.

## State And Persistence
State persists in FPGA registers accessed through the parent regmap: function-enable bits, GPIO-enable bits, and GPIO direction bits. Driver-owned state is devm-managed and includes pin tables, generic group/function registrations, pin range metadata, and GPIO forwarder descriptors added on request.

## Dependencies And Integration Points
Depends on the UP board MFD FPGA driver, regmap, DMI matching, generic pinctrl/pinmux helpers, `gpio/forwarder`, and gpiolib consumer/provider APIs. The DMI mapping currently targets `AAEON` `UP-APL01` and maps default states onto Intel ACPI devices such as `INT3452:*`.

## Risks
Board support is gated by DMI data, so new UP variants need explicit mappings. Function-mode pins without `funcbit` reject function selection with `-EPERM`. Default mappings include an `ssp0` group/function name that is not defined in the local UP/UP2 tables, so validation depends on whether that mapping is ever selected for a supported board. GPIO forwarder request failures must release pinctrl ownership, which this driver handles but remains a key error path.

## Test Signals
Useful signals are probe success on UP and UP2 hardware, default-state selection without unresolved groups/functions, debugfs pin mode output, GPIO request/free/direction round trips through the forwarder, and register traces showing `funcbit`, `enbit`, and `dirbit` updates for each mux mode.
