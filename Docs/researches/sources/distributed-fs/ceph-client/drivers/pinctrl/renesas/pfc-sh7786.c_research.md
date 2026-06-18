# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7786.c

## Purpose

This source is the SH7786 pin-function-controller description for the `sh_pfc` common driver. It defines GPIO-capable pins for ports PA-PH and PJ, maps alternate functions for external bus, DMA, serial, SSI, flash/status, IRQ, and related SoC signals, and publishes the register tables as `sh7786_pinmux_info`.

## Important APIs, Types, And Functions

The only externally consumed object is `const struct sh_pfc_soc_info sh7786_pinmux_info`. Core data is carried in the enum ranges, `pinmux_data`, `pinmux_pins`, `pinmux_func_gpios`, `pinmux_config_regs`, and `pinmux_data_regs`. The file depends on `PINMUX_DATA`, `PINMUX_GPIO`, `GPIO_FN`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, and `PINMUX_DATA_REG` macros from the common Renesas PFC layer.

## Control Flow

There is no local runtime logic. The shared PFC driver receives `sh7786_pinmux_info` from SoC setup, registers the listed pins/functions, and programs the concrete control and data registers when pinctrl or GPIO clients request a mux, direction, or value change. The alternate-function selector registers `P1MSELR` and `P2MSELR` add another layer of table-driven choice for functions that share a pin.

## State And Persistence

All local tables are immutable. Runtime state is held by the shared PFC core and the SH7786 PFC hardware registers. The register state is volatile hardware configuration and is not saved by this file.

## Dependencies And Integration Points

Dependencies are `<cpu/sh7786.h>` and `sh_pfc.h`. The register map uses PFC control registers beginning at `0xffcc0000`, selector registers at `0xffcc0080` and `0xffcc0082`, and data registers from `0xffcc0020` to `0xffcc0030`. The source integrates with the SuperH PFC core, which exposes the data to Linux pinctrl and GPIO consumers.

## Risks

The SH7786 tables contain many sparse register fields: PE only exposes upper bits, PG only exposes bits 7-5, and PJ has bit 0 reserved in the config/data views. A wrong reserved placeholder or register width changes the semantic position of all following fields. The selector registers are dense and easy to misalign with enum IDs. Because the file has no validation code, errors appear only as incorrect board-level muxing or GPIO behavior.

## Test Signals

Good test signals are compile coverage, successful `sh7786_pfc` registration, debugfs presence of the expected PA-PJ pin set, GPIO direction/value tests on ports with sparse bits, mux validation for serial, SSI, flash/status, external bus, DMA, and IRQ signals, and hardware register readback for `P1MSELR`/`P2MSELR` choices.
