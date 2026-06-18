# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7264.c

## Purpose

`pfc-sh7264.c` is the SuperH SH7264 pinmux data file for the legacy `sh_pfc` framework. It exports `sh7264_pinmux_info`, describing GPIO-capable pins, alternate function GPIOs, mode-control registers, and data registers for SH7264. The file is a larger sibling of the SH7203 table and covers ports PA, PB, PC, PD, PE, PF, PG, PH, PJ, and PK, while noting that port I is absent and port H has no normal data register.

The alternate functions cover interrupts and PINT, watchdog output, CAN, DMAC, ADC trigger, bus-state controller, timers, SCIF, RSPI, IIC3, SSI, SIOF, SPDIF, NAND flash controller, digital video input, and LCD output. SD-card signals are available on both PG and PK, and LCD/video/serial/audio functions are heavily multiplexed across PF/PG/PJ/PK.

## Important APIs, types, and data

- The top-level enum defines all data symbols, input/output symbols, mode-control symbols, and function marks. `PINMUX_*_BEGIN`/`END` sentinels are consumed by `sh7264_pinmux_info`.
- `pinmux_data[]` binds `*_DATA` and `*_MARK` entries to the exact mode encodings needed by the hardware. It includes port-level comments and special cases such as PH analog input functions.
- `pinmux_pins[]` exposes GPIO pins for PA3-PA0, PB22-PB1, PC10-PC0, PD15-PD0, PE5-PE0, PF12-PF0, PG24-PG0, PJ11-PJ0, and PK11-PK0. PH is deliberately not included in `pinmux_pins[]` because the comments indicate no normal data register for port H, even though PH data symbols and analog-function marks exist.
- `pinmux_func_gpios[]` exposes function GPIOs grouped by subsystem: INTC/PINT, WDT, CAN, DMAC, ADC, BSCh, TMU, SCIF, RSPI, IIC3, SSI, SIOF, SPDIF, NANDFMC, and VDC3.
- `pinmux_config_regs[]` describes the 16-bit mode and direction registers under the `0xfffe38xx`/`0xfffe39xx` ranges. It uses `PINMUX_CFG_REG_VAR()` where leading/trailing reserved fields make the bit layout nonuniform.
- `pinmux_data_regs[]` describes readable/writable GPIO data registers, including split pairs such as `PADR1`/`PADR0`, `PBDR1`/`PBDR0`, `PGDR1`/`PGDR0`, and single registers for PC, PD, PE, PF, PJ, and PK.

## Control flow

There is no local function logic. The common SH PFC core uses the exported table.

For GPIO operations, the core resolves a GPIO pin to its data symbol, programs GPIO mode and direction through `pinmux_config_regs[]`, and accesses the data bit through `pinmux_data_regs[]`. For function selections, the core uses a `GPIO_FN()` entry to resolve a function mark and programs the mode bits listed in `pinmux_data[]`.

The file has several duplicated or alternative placements. CAN functions can combine CTX0/CTX1 or CRX0/CRX1. SD signals are available on PG and PK. SCIF channels span multiple ports. RSPI and SSI signals overlap with PF/PG/PK groups. LCD and digital-video signals share PF/PG regions. These alternatives are represented as separate marks or as repeated marks on different pins/modes.

## State and persistence behavior

The file has no mutable software state. PFC state persists in hardware control, direction, and data registers. Direction state uses `*IOR*` registers; function mode state uses port control registers such as `PBCR*`, `PCCR*`, `PGCR*`, `PJCR*`, and `PKCR*`; data state uses `*DR*` registers. PH is special: comments state that port H has no data register and PH data is connected to the PH port register, so it is modeled for function selection but not exposed as normal GPIO pins.

## Dependencies and integration points

The file includes `linux/kernel.h`, `<cpu/sh7264.h>`, and `sh_pfc.h`. The CPU header provides symbolic pin IDs. `sh_pfc.h` provides the pinmux macros and `struct sh_pfc_soc_info`.

The exported `sh7264_pinmux_info` integrates with the shared SuperH PFC driver. It supplies the old function-GPIO interface (`func_gpios`) rather than modern group/function arrays. Platform code or board setup must select function names exactly as listed by `GPIO_FN()` entries.

## Risks and edge cases

- Several table rows appear suspicious and should be checked against the hardware manual. `PC10_DATA` is followed by `TIOC2B_MARK, PC1MD_1`, which looks like a possible typo for `PC10MD_1`. Similarly, `PG6_DATA` and its alternate rows use `PG7MD_*` mode constants instead of `PG6MD_*`.
- The enum includes `PJ12_DATA` and `PK12_DATA`, and data registers include those symbols, but `pinmux_pins[]` exposes only PJ11-PJ0 and PK11-PK0. That may be intentional because corresponding input/output/mode controls are absent, but it is a boundary worth validating.
- `pinmux_func_gpios[]` lists `PINT7_PG` through `PINT1_PG` but not `PINT0_PG`, while the enum and `pinmux_data[]` contain `PINT0_PG_MARK`. This may be deliberate or an omission in the external function surface.
- PH analog marks exist without normal GPIO exposure. Tests must not assume every data enum produces a `PINMUX_GPIO()` entry.
- The register tables contain many reserved fields encoded as zeros. Misordered enum additions or incomplete mode encodings can program the wrong peripheral function while compiling cleanly.
- Peripheral overlap is extensive, especially among LCD/VDC3, SD, RSPI, SSI/SIOF/SPDIF, and serial pins. Board pinctrl states must avoid selecting incompatible functions on the same physical pins.

## Test signals

Compile-time validation should cover SH7264 PFC support and ensure all enum symbols resolve. Static table checks should verify that every function GPIO has a matching mark in `pinmux_data[]`, every GPIO pin has a data-register mapping, every data-register symbol has a plausible exposed pin or documented exception, and every mode symbol used by `pinmux_data[]` appears in `pinmux_config_regs[]`. Targeted checks should focus on the suspicious `PC10`/`PC1MD`, `PG6`/`PG7MD`, missing `PINT0_PG` exposure, and PJ12/PK12 data-only modeling. Hardware tests should exercise representative GPIO direction/data paths and pin functions for SD, LCD/VDC3, SCIF, RSPI, SSI/SIOF/SPDIF, CAN, BSC, and interrupt lines.
