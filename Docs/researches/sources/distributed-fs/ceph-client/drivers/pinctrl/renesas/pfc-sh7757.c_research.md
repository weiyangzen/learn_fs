# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7757.c

## Purpose

This file is the SuperH SH7757 B0-step pin-function-controller description consumed by the shared Renesas `sh_pfc` core. It is a declarative SoC map: it names GPIO-capable pins from ports PTA through PTZ, describes input/output/function selector IDs, maps alternate-function marks to pins, lists exported function GPIO names, and publishes the register layout through `sh7757_pinmux_info`.

## Important APIs, Types, And Functions

The central API surface is the exported `const struct sh_pfc_soc_info sh7757_pinmux_info`. Important tables are the large enum ranges bounded by `PINMUX_DATA_BEGIN/END`, `PINMUX_INPUT_BEGIN/END`, `PINMUX_OUTPUT_BEGIN/END`, and `PINMUX_FUNCTION_BEGIN/END`; `pinmux_data`; `pinmux_pins`; `pinmux_func_gpios`; `pinmux_config_regs`; and `pinmux_data_regs`. The implementation relies on `sh_pfc.h` macros such as `PINMUX_DATA()`, `PINMUX_GPIO()`, `GPIO_FN()`, `PINMUX_CFG_REG()`, `PINMUX_CFG_REG_VAR()`, `PINMUX_DATA_REG()`, and `GROUP()`.

## Control Flow

There is no executable probe or callback code in this source. Board or CPU setup code references `sh7757_pinmux_info`, and the shared `sh_pfc` driver uses the static tables to register pins, function GPIOs, mux choices, and data registers. Runtime pin selection in the core resolves requested marks through `pinmux_data`, programs the port control registers in `pinmux_config_regs`, and reads or writes GPIO data through `pinmux_data_regs`.

## State And Persistence

All file-owned state is static constant data. Persistent runtime state is hardware register state in the PFC block, not state stored by this file. Register values remain until reset, power loss, or a later pinctrl/GPIO operation changes the same fields. The disabled `PPCR` config block under `#if 0` is source state only and is not exposed to the core.

## Dependencies And Integration Points

The file depends on `<cpu/sh7757.h>` for SoC mark and GPIO IDs and on the Renesas `sh_pfc` common model. It describes direct MMIO register addresses around `0xffec0000` through `0xffec0084`: per-port control registers `PACR` through `PZCR`, selector registers `PSEL0` through `PSEL8`, and data registers `PADR` through `PZDR`. Covered peripheral signals include memory bus, MMC/SD, SCIF/COM serial, I2C/DDC, SGPIO, USB VBUS, JTAG/debug, audio, PWM, LPC-like signals, event inputs, SIM, SPI, and on-chip NAND/data pins.

## Risks

The main risk is table correctness. Enum order, `PINMUX_DATA()` associations, function GPIO ordering, register addresses, bit widths, and reserved-field padding must match the SH7757 hardware manual exactly. Several ports have missing top bits, and the config tables use zero placeholders for reserved fields that the common core must not program. The `PPCR` register is deliberately excluded while `PPDR` remains present, which can surprise GPIO coverage expectations for PTP pins. Incorrect selector entries in `PSEL0`-`PSEL8` would silently route a peripheral to the wrong alternate signal.

## Test Signals

Useful signals are build coverage for SH7757 PFC support, successful registration of `sh7757_pfc`, pinctrl debugfs listing of PTA-PTZ pins and function GPIOs, GPIO direction/value tests on ports with full and partial bit coverage, mux tests for high-value peripherals such as MMC, serial, I2C, SGPIO, USB VBUS, and memory bus signals, and readback tests confirming reserved fields are not modified.
