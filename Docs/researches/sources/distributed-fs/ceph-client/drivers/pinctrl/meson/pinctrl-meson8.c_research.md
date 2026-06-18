# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8.c

## Purpose
This file describes the Amlogic Meson8 and Meson8m2 pin controllers for CBUS and AO bus domains. It supplies static pin, group, function, and bank tables to the shared Meson core and first-generation Meson8 mux backend.

## Important APIs, Types, and Data
- `meson8_cbus_pins` covers GPIOX/Y/DV/H/Z, CARD, and BOOT pins; `meson8_aobus_pins` covers GPIOAO plus special always-on pins.
- Pin arrays and group tables define SD/SDXC, PCM, UART, ISO7816, I2C, XTAL, DVI/ENC/VGA/HDMI, SPI, Ethernet, NAND/NOR, PWM, I2S, SPDIF, remote, AO I2C, and HDMI CEC functions.
- `meson8_cbus_functions` and `meson8_aobus_functions` expose functions with GPIO first, matching first-generation mux backend expectations.
- `meson8_cbus_banks` and `meson8_aobus_banks` encode register offsets/bits for pull, GPIO direction/value/input, and IRQ ranges.
- `meson8_cbus_pinctrl_data` and `meson8_aobus_pinctrl_data` bind the static data to `meson8_pmx_ops`; AO uses `meson8_aobus_parse_dt_extra`.
- `meson8_pinctrl_dt_match` covers Meson8 and Meson8m2 CBUS/AOBUS compatibles; the driver is built in with `builtin_platform_driver()`.

## Control Flow
Device-tree matching selects either CBUS or AOBUS data, then the shared probe maps resources and registers pinctrl/gpio. Mux selection is handled by `meson8_pmx_ops`, which reads each group’s register bit metadata. Pinconf and GPIO operations use the bank descriptors in this file. AO parsing aliases pull-enable to the pull register range because older AO layouts share those registers.

## State and Persistence
This is static SoC data only. Hardware registers retain mux, pull, and GPIO state. No local dynamic state or suspend/resume logic is implemented.

## Dependencies and Integration Points
It depends on `dt-bindings/gpio/meson8-gpio.h`, `pinctrl-meson.h`, and `pinctrl-meson8-pmx.h`. It integrates with DT compatibles `amlogic,meson8-cbus-pinctrl`, `amlogic,meson8-aobus-pinctrl`, `amlogic,meson8m2-cbus-pinctrl`, and `amlogic,meson8m2-aobus-pinctrl`.

## Risks
The CBUS/AOBUS split requires board DTS nodes to bind the correct compatible and resources. Function ordering must keep GPIO at selector zero. Dense `GROUP()` register/bit tables and `BANK()` register descriptors are susceptible to silent hardware misrouting if copied incorrectly. AO register sharing depends on `meson8_aobus_parse_dt_extra()` and requires the pull resource to be present.

## Test Signals
Boot Meson8 and Meson8m2 boards with both CBUS and AOBUS nodes, validate gpiochip counts, inspect pinctrl debugfs function/group lists, and smoke-test UART/I2C/SD/NAND/Ethernet/HDMI CEC/AO remote pins. GPIO request tests should confirm alternate mux bits are disabled.
