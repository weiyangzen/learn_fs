# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7203.c

## Purpose

`pfc-sh7203.c` is the SuperH SH7203 pinmux description for the legacy `sh_pfc` framework. It exports `sh7203_pinmux_info`, which lists the SH7203 GPIO pins, alternate function GPIO names, mode-control registers, data registers, and pin/function relationships. Unlike the newer R-Car file, it does not define modern `groups`/`functions` arrays; it uses the older `func_gpios` model where alternate functions are exposed as function GPIOs.

The hardware model is ports PA through PF. PA is input-only in this table, PB-PC-PD-PE-PF carry GPIO input/output plus alternate functions, and PF is a wide 31-bit port split across high and low data/config registers. The alternate functions cover INTC/PINT/IRQ, watchdog and reference outputs, CAN, IIC3, DMAC, ADC trigger, bus-state controller signals, timers, SSU, SCIF, SSI, FLCTL/NAND, and LCDC.

## Important APIs, types, and data

- The large enum defines ordered ID ranges for data pins, input states, output states, hardware mode bits, and function marks. The `.input`, `.output`, and `.function` ranges in `sh7203_pinmux_info` refer directly to these enum boundaries.
- `pinmux_data[]` is the central truth table. Each `PINMUX_DATA()` row binds a GPIO data symbol or alternate `*_MARK` to the required mode bits and, for GPIO-capable pins, input/output controls.
- `pinmux_pins[]` exposes GPIO pins for PA7-PA0, PB12-PB0, PC14-PC0, PD15-PD0, PE15-PE0, and PF30-PF0.
- `PINMUX_FN_BASE` and `pinmux_func_gpios[]` expose function GPIOs such as `IRQ*_PB`, `TIOC*`, `TXD*`, `SSIDATA*`, `NAF*`, and `LCD_DATA*`.
- `pinmux_config_regs[]` describes the memory-mapped 16-bit configuration registers: I/O direction registers (`PBIORL`, `PCIORL`, `PDIORL`, `PEIORL`, `PFIORH`, `PFIORL`), control registers (`PBCRL*`, `PCCRL*`, `PDCRL*`, `PECRL*`, `PFCRH*`, `PFCRL*`), and `IFCR` for PB12 IRQ/refout selection.
- `pinmux_data_regs[]` maps data register bits (`PADRL`, `PBDRL`, `PCDRL`, `PDDRL`, `PEDRL`, `PFDRH`, `PFDRL`) back to the data enum values.

## Control flow

This file has no executable control path. The common `sh_pfc` driver receives GPIO or function requests and interprets these tables.

For a GPIO direction request, the core locates the pin in `pinmux_pins[]`, finds its `*_DATA` entry in `pinmux_data[]`, programs the matching mode bits to GPIO mode, then uses the appropriate I/O direction register entry from `pinmux_config_regs[]`. Data reads and writes use `pinmux_data_regs[]`.

For a function request such as `TXD0`, `LCD_DATA15`, `DACK0_PE`, or `SDA3`, the function GPIO entry names a `*_MARK`. The core resolves the mark through `pinmux_data[]` and writes the required control-register encoding. Some functions have multiple placements, for example DMAC signals on PD or PE, timer clock inputs on PD or PF, SSU signals on PD or PF, and IRQ/PINT functions on PB, PD, or PE.

## State and persistence behavior

There is no in-memory mutable state. State persists in the SH7203 PFC hardware registers under the `0xfffe38xx` to `0xfffe3axx` address range. Direction registers control GPIO input/output, control registers select alternate modes, and data registers hold/read GPIO levels. The table uses `FORCE_IN` and `FORCE_OUT` markers for pins or functions that are not direction-configurable by normal GPIO I/O bits.

## Dependencies and integration points

The file includes `linux/kernel.h`, `<cpu/sh7203.h>`, and `sh_pfc.h`. The CPU header supplies pin IDs such as `PA7`, `PB12`, and `PF30`; `sh_pfc.h` supplies `PINMUX_DATA`, `PINMUX_GPIO`, `GPIO_FN`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `PINMUX_DATA_REG`, and the `struct sh_pfc_soc_info` contract.

The integration point is the exported `sh7203_pinmux_info`. Board code or platform setup that selects the SH7203 PFC passes this structure to the shared SuperH PFC code. Function names in `pinmux_func_gpios[]` form the external selection surface for non-GPIO functions.

## Risks and edge cases

- Table consistency is the main risk. Enum ordering, mode encoding, and register bitfield layout must remain synchronized. The common core depends on the numeric enum ranges being contiguous and correctly bounded.
- The PB5 alternate-function rows appear suspicious: after `PB5_DATA`, the `SDA2_MARK`, `PINT5_PB_MARK`, and `IRQ5_PB_MARK` entries reference `PB6MD_01`, `PB6MD_10`, and `PB6MD_11` instead of `PB5MD_*`. This may be a copy/paste defect that would select PB6 mode bits while claiming PB5 functions.
- Several register descriptors contain reserved fields represented by zeros or negative `GROUP()` widths. Any inserted or removed enum value can misalign later hardware values without a local compiler error.
- Multiple functions share the same physical pins or peripherals: PD/PF SSU alternatives, PD/PF timer clock alternatives, PE/PD DMAC alternatives, and overlapping LCD/FLCTL/SSI functions on PF. Invalid board configurations can conflict at runtime even though each individual group is valid.
- The older function-GPIO model does not provide named pin groups, so external validation is weaker than on modern pinctrl data.

## Test signals

Build coverage should compile the SH PFC driver with SH7203 support and catch missing enum symbols or malformed initializers. Static validation should cross-check every `GPIO_FN()` mark against `pinmux_data[]`, every `PINMUX_GPIO()` data symbol against `pinmux_data_regs[]`, and every mode symbol used in `pinmux_data[]` against exactly one config-register field. Hardware tests should exercise GPIO direction and data paths for each port, plus representative functions from IRQ/PINT, CAN, IIC3, DMAC, BSC, SCIF, SSI, FLCTL, and LCDC. The PB5/PB6 mode-symbol mismatch is a high-value targeted test.
