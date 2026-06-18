# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a73a4.c

## Purpose
Provides the complete Renesas R-Mobile APE6/R8A73A4 pin-function-controller description consumed by the common `sh_pfc` pinctrl/GPIO driver. The file is almost entirely declarative: it names the SoC pins, enumerates all legal GPIO and alternate-function states, describes function groups exposed to pinctrl consumers, maps configuration and data registers, wires GPIO pins to interrupt numbers, and exports `r8a73a4_pinmux_info` for the Renesas PFC core.

## Important APIs, Types, and Functions
The exported API is `const struct sh_pfc_soc_info r8a73a4_pinmux_info`, referenced from the Renesas PFC platform match table and declared in `sh_pfc.h`. It points at `pinmux_pins`, `pinmux_groups`, `pinmux_functions`, `pinmux_config_regs`, `pinmux_data_regs`, `pinmux_data`, and `pinmux_irqs`.

The main generated-ID enum spans `PINMUX_DATA_BEGIN/END`, `PINMUX_INPUT_BEGIN/END`, `PINMUX_OUTPUT_BEGIN/END`, `PINMUX_FUNCTION_BEGIN/END`, and `PINMUX_MARK_BEGIN/END`. It creates per-port IDs for data/input/output/function states across a sparse port map from port 0 through port 329, plus module-select states for `MSEL1CR`, `MSEL3CR`, `MSEL4CR`, `MSEL5CR`, and `MSEL8CR`. `CPU_ALL_PORT()` defines the sparse R8A73A4 port inventory used by `PORT_ALL()`.

`pinmux_data[]` is the cross-reference table that tells the core which marks are valid on each port and which function selector and optional MSEL bits are required. `pinmux_pins[]` lists the pins and supported pinconf capabilities, mostly `SH_PFC_PIN_CFG_INPUT | SH_PFC_PIN_CFG_OUTPUT | SH_PFC_PIN_CFG_PULL_UP_DOWN`, with output-only exceptions for pins 74 and 288. `IRQC_PINS_MUX()` creates one-pin interrupt groups. `pinmux_groups[]` and `pinmux_functions[]` expose logical pinctrl functions for `irqc`, `mmc0`, `mmc1`, `scifa0`, `scifa1`, `scifb0` through `scifb3`, and `sdhi0` through `sdhi2`.

`r8a73a4_pin_to_portcr()` is the only executable helper in the file. It converts a pin number into a PORTCR register offset by indexing `r8a73a4_portcr_offsets[pin >> 5]` and adding the pin number. `r8a73a4_pfc_ops` connects this helper plus `rmobile_pinmux_get_bias` and `rmobile_pinmux_set_bias` to the core.

## Control Flow
At boot, `drivers/pinctrl/renesas/core.c` selects `r8a73a4_pinmux_info` for the matching compatible/platform entry. The generic `sh_pfc` core consumes the descriptor, creates the pinctrl functions and groups, registers GPIO ranges, and uses the register tables whenever consumers request a mux state, GPIO direction, data value, IRQ mapping, or pull-bias configuration.

There is no active probe logic in this file. The control path is table-driven: a pinctrl client selects a function/group, the core searches the function/group tables, maps group mux marks through `pinmux_data[]`, programs the matching `PORTn_FNx` selectors and MSEL bits in `pinmux_config_regs[]`, and then uses the data-register table for GPIO values. Bias control is delegated to the shared R-Mobile helpers, which use `pin_to_portcr` to find the port control byte.

## State and Persistence Behavior
All state is static, read-only SoC description data except for the hardware registers that the common core programs from these tables. Persistent hardware state lives in PORTCR registers, MSEL registers, and data registers at the listed physical addresses under the `0xe605....` PFC region. `pinmux_config_regs[]` lists every supported `PORTCR()` register plus MSEL registers; `pinmux_data_regs[]` lists grouped 32-bit data registers for port banks such as `PORTL031_000DR`, `PORTD127_096DR`, `PORTR223_192DR`, and `PORTU351_320DR`.

The descriptor covers sparse pin ranges rather than a dense 0-329 bank. Missing ports are represented by zero slots in data registers and omitted from `pinmux_pins[]`. The `r8a73a4_portcr_offsets[]` lookup relies on the sparse high bits of the pin number and assumes callers pass valid pins from the SoC descriptor.

## Dependencies and Integration Points
Depends on Linux IO/kernel headers, generic pinconf flags from `linux/pinctrl/pinconf-generic.h`, and Renesas-local macros/types in `sh_pfc.h`. Important local integration points are `PORTCR`, `PINMUX_DATA`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `PINMUX_DATA_REG`, `PINMUX_IRQ`, `SH_PFC_PIN_GROUP`, `BUS_DATA_PIN_GROUP`, `SH_PFC_FUNCTION`, and the shared R-Mobile bias helpers.

Peripheral integration is through named pinctrl functions. The file describes external interrupt pins IRQ0-IRQ57, MMCIF0/1 buses, serial ports SCIFA0/1 and SCIFB0-3 with alternate placements, SDHI0-2 data/control/card-detect/write-protect groups, LCD/display and video pins in the mark/data tables, memory bus pins, SIM, MSIOF, FSI, HSI, keypad, PDM, TPU, IRDA, and other SoC-specific alternate functions. Only a subset is promoted to named `sh_pfc_function` entries; other marks remain valid mux targets used internally by groups or platform data.

## Risks
The main risk is data-table drift. A wrong mark, function selector, MSEL dependency, register address, or pin order can make the kernel program an unrelated physical pad. MSEL conditions are especially fragile because several peripherals have alternate placements and require both the port function number and the correct mode-select bit. `r8a73a4_pin_to_portcr()` does not bounds-check its `pin >> 5` index, so correctness depends on callers using pins present in `pinmux_pins[]` and on the descriptor staying consistent with the sparse port layout.

IRQ risk is also high: `pinmux_irqs[]`, `IRQC_PINS_MUX()` group names, and `pinmux_data[]` IRQ marks must agree or GPIO IRQ routing can appear to register while the wrong pad is muxed. Bias support is broad but coarse; nearly every pin is declared pull-up/down capable, so board-level validation is needed before changing individual `SH_PFC_PIN_CFG_*` flags.

## Test Signals
Build-time signals include successful compilation with the Renesas PFC macros and no missing enum marks, groups, or function names. Runtime signals include PFC probe with `r8a73a4_pfc`, pinctrl state selection for MMCIF, SDHI, SCIFA/SCIFB, and IRQC consumers, GPIO input/output reads through all represented data-register banks, pull-up/down get/set through pinconf, and GPIO IRQ delivery for representative low, middle, and high IRQ pins such as IRQ0, IRQ20, IRQ40, IRQ50, and IRQ57. Hardware validation should exercise alternate serial and SDHI placements that rely on MSEL bits, plus suspend/resume or reboot persistence where boot firmware may leave MSEL/PORTCR registers in non-default states.
