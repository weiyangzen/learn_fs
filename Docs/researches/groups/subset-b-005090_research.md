# subset-b-005090 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a73a4.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a73a4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7740.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7740.c

## Purpose
Provides the complete Renesas R-Mobile A1/R8A7740 pin-function-controller description for the shared `sh_pfc` driver. It maps the SoC's 212 GPIO-capable ports and alternate functions to the Linux pinctrl model, including per-pin capabilities, valid mux marks, pin groups, function names, configuration registers, GPIO data registers, IRQ pin mappings, and the exported `r8a7740_pinmux_info` descriptor.

## Important APIs, Types, and Functions
The exported API is `const struct sh_pfc_soc_info r8a7740_pinmux_info`, selected by the Renesas PFC core and declared in `sh_pfc.h`. It references the SoC operation table `r8a7740_pfc_ops` and all static descriptor arrays: `pinmux_pins`, `pinmux_groups`, `pinmux_functions`, `pinmux_config_regs`, `pinmux_data_regs`, `pinmux_data`, and `pinmux_irqs`.

The top-level enum creates all internal IDs for GPIO data/input/output, function selectors `FN0` through `FN7`, mode-select bits in `MSEL1CR`, `MSEL3CR`, `MSEL4CR`, and `MSEL5CR`, and hundreds of function marks. `CPU_ALL_PORT()` declares a dense port range 0-211. `IRQC_PIN_MUX()` and `IRQC_PINS_MUX()` generate interrupt pin groups, including alternate IRQ locations such as IRQ0 on ports 2 or 13 and IRQ31 on ports 41 or 167.

`pinmux_data[]` is the authoritative validity table. It maps each mark to the port function selector and any mode-select bits needed to reach that signal. `pinmux_pins[]` uses `SH_PFC_PIN_CFG()` wrappers to encode each pin's input/output and pull-up/pull-down support, matching the hardware table comment. `pinmux_groups[]` and the group-name arrays expose named pinctrl groups for the bus state controller, CEU camera interfaces, FSI audio, Gigabit Ethernet, HDMI, interrupt controller, LCD0/1, MMCIF, SCIFA0-7, SCIFB, SDHI0-2, and TPU0. `r8a7740_pin_to_portcr()` maps a pin to a PORTCR offset by scanning `r8a7740_portcr_offsets[]`; it returns `-1` for pins outside the supported ranges.

## Control Flow
During platform/PFC probe, `core.c` matches the R8A7740 SoC and passes `r8a7740_pinmux_info` to the generic `sh_pfc` infrastructure. The common core registers the described pins, groups, and functions with pinctrl and uses the register descriptors to perform future mux, GPIO, IRQ, and pinconf operations.

Muxing is entirely data-driven. A pinctrl client selects a function and group, the core resolves that group to a pins array and mux marks array, finds each mark in `pinmux_data[]`, then writes the required `PORTn_FNx` selector and MSEL state into registers from `pinmux_config_regs[]`. GPIO reads/writes use `pinmux_data_regs[]`, while GPIO IRQ support uses `pinmux_irqs[]` and the interrupt groups. Bias get/set calls are routed through `rmobile_pinmux_get_bias` and `rmobile_pinmux_set_bias`, which use `r8a7740_pin_to_portcr()`.

## State and Persistence Behavior
The file contains static descriptor data only; live state persists in PFC hardware registers programmed by the shared driver. The configuration register table lists each `PORTCR()` byte from port 0 to 211 across several address windows and variable-width MSEL registers for global function choices. The data register table divides GPIO data storage into port banks such as `PORTL031_000DR`, `PORTD095_064DR`, `PORTR159_128DR`, and `PORTU223_192DR`, with zero slots for holes or unsupported bits.

Mode-selection state is persistent hardware state. Many functions require both a port function number and one or more MSEL bits, for example SCIFA3/4/5 placements, LCD0 24-bit data placement, SDHI2 card-detect/write-protect placement, MMCIF placement, SIM data placement, CEU VIO data placement, and trace/debug source selection. `r8a7740_pin_to_portcr()` is more defensive than the R8A73A4 variant because it scans end-pin groups and returns failure for out-of-range pins.

## Dependencies and Integration Points
Depends on Linux IO/kernel headers, generic pinconf flags, and Renesas `sh_pfc.h` macros/types. It integrates with the common Renesas pinctrl core through `sh_pfc_soc_info` and `sh_pfc_soc_operations`, with pinconf through R-Mobile bias helpers, and with GPIO IRQ handling through the `pinmux_irq` table.

Peripheral integration is broad. Named functions expose BSC/FLCTL/PCMCIA-style external bus groups, CEU0/1 camera input, FSIA/FSIB audio pins, GEther RMII/MII/GMII plus PHY interrupt/link/WOL pins, HDMI HPD/CEC, INTC IRQ0-31 alternate pins, LCD0 and LCD1 RGB/system/display groups, two alternate MMCIF pinouts under the single `mmc0` function, SCIFA0-7, SCIFB, SDHI0-2, and TPU timer outputs. The mark table also covers debug/trace, VIO, MEMC, USB, BBIF, IRDA, ATAPI/IDE, DMA request/acknowledge, reset pull behavior, and SD encoder selections.

## Risks
This descriptor is highly coupling-sensitive. The same physical pads are shared between unrelated peripherals, so a wrong MSEL dependency or group pin order can silently route a board function to a conflicting signal. Several group names encode alternate placements with suffixes (`_0`, `_1`, `_2`) and must stay aligned with both the mux marks and the MSEL bit values. The `pinmux_irqs[]` table and generated interrupt groups must agree with the `PINMUX_DATA()` entries; otherwise users can request an IRQ group that does not actually select the matching pad.

Register address errors are hard to diagnose because `PORTCR()` entries are byte-addressed and split across windows at ports 84, 115, and 210. Pinconf risks are significant as well: `pinmux_pins[]` captures detailed pull-up/pull-down capabilities, and changing those flags may expose invalid bias settings to board DTS/platform users. The descriptor includes comments such as "needs fixup", question marks, and shared FLCTL/PCMCIA annotations, indicating areas where hardware documentation or board validation matters.

## Test Signals
Build signals include successful compilation and resolution of every mark, group, and function name generated by the Renesas macros. Runtime validation should include PFC probe with name `r8a7740_pfc`, pinctrl selection for each major function family, GPIO direction/value testing across low/mid/high banks, pinconf bias get/set on pins with pull-up/down variants, and GPIO IRQ delivery for single and alternate IRQ mappings such as IRQ0, IRQ12, IRQ16, IRQ26, and IRQ31.

Board-level tests should focus on mux alternatives: LCD0 24-bit data on both placements, SCIFA3/4/5 alternate data and clock pins, CEU0 upper data alternatives, MMCIF placement 0 versus 1, SDHI2 CD/WP alternatives, GEther RMII/MII/GMII width choices, and BSC bus-width subsets. Suspend/resume or reboot tests should verify that MSEL and PORTCR state is restored consistently by pinctrl consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7740.c -->
