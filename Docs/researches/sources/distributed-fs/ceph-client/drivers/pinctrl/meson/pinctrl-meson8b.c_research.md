# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson8b.c

## Purpose
This file describes the Amlogic Meson8b CBUS and AOBUS pin controllers. It is a static SoC data provider for the shared Meson pinctrl core and first-generation mux backend.

## Important APIs, Types, and Data
- `meson8b_cbus_pins` lists GPIOX/Y/DV/H/CARD/BOOT/DIF pins, with gaps reflecting the public SoC pin map.
- `meson8b_aobus_pins` lists GPIOAO pins plus `GPIO_BSD_EN` and `GPIO_TEST_N`, with comments noting undocumented pins.
- Pin group tables cover SD/SDXC, PCM, UART, ISO7816, SPI, TSIN, PWM, I2C, HDMI, Ethernet, NAND/NOR, SPDIF, I2S, remote, clock, and HDMI CEC functions.
- `meson8b_cbus_functions` and `meson8b_aobus_functions` expose function groupings, with GPIO as the first selector.
- `meson8b_cbus_banks` uses fine-grained bank ranges such as `X0..11`, `X16..21`, `Y0..1`, and `DIF`; `meson8b_aobus_banks` describes AO pins.
- Pinctrl data structures point to `meson8_pmx_ops`; AOBUS uses `meson8_aobus_parse_dt_extra`.
- `meson8b_pinctrl_dt_match` exposes CBUS and AOBUS compatibles and registers a built-in platform driver.

## Control Flow
The platform driver uses the shared Meson probe. Runtime mux requests go through the first-generation backend, using per-group bit metadata to clear conflicting groups and enable the selected group. Pinconf/GPIO calls use the common Meson bank register calculation based on the ranges in this file.

## State and Persistence
The file holds immutable tables. Mux, pull, direction, and GPIO values persist in hardware registers. No local state machine or save/restore path is present.

## Dependencies and Integration Points
It depends on `dt-bindings/gpio/meson8b-gpio.h`, the Meson common header, and the Meson8 mux header. Device-tree integration is through `amlogic,meson8b-cbus-pinctrl` and `amlogic,meson8b-aobus-pinctrl`.

## Risks
Meson8b has discontinuous pin ranges and undocumented pins; incorrect bank boundaries or IRQ ranges can affect GPIO numbering or interrupt assumptions. The DIF bank is marked with unknown IRQ support (`-1, -1`) and should not be assumed interrupt-capable. The first-generation mux backend relies on complete group pin overlap data to avoid conflicts.

## Test Signals
Build and boot with Meson8b DT nodes, verify CBUS/AOBUS gpiochip registration and pinctrl debugfs output, and run hardware tests on shared-function pins such as SD/SDXC, UART, SPI, HDMI, Ethernet, NAND/NOR, AO remote, and GPIO fallback after peripheral muxing.
