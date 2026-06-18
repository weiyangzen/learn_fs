# subset-b-005104 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779h0.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779h0.c

## Purpose

`pfc-r8a779h0.c` is the Renesas R-Car V4M (`R8A779H0`) pin function controller description consumed by the common `sh_pfc`/Renesas pinctrl core. It does not register a platform driver itself; instead it exports `r8a779h0_pinmux_info`, a `struct sh_pfc_soc_info` instance that describes all GPIO-capable pins, non-GPIO voltage-domain pins, multiplexed functions, register layouts, drive-strength controls, bias controls, and IO-voltage controls for this SoC.

The file is table-driven. Its main job is to convert SoC manual data into kernel pinctrl data structures: GPIO pins become `RCAR_GP_PIN()` IDs, alternate functions become `*_MARK` and `FN_*` enum entries, and GPSR/IPSR/MOD_SEL register bitfields become `struct pinmux_cfg_reg` descriptors. Higher-level consumers select groups such as `avb0_rgmii`, `qspi0_data4`, `scif1_data_a`, or `i2c2`, and the common PFC core programs the described registers.

## Important APIs, types, and data

- `CFG_FLAGS` combines drive strength and pull-up/down support; selected port ranges add `SH_PFC_PIN_CFG_IO_VOLTAGE_18_33`.
- `CPU_ALL_GP()` expands the SoC's sparse GPIO banks. It defines banks 0 through 7, with reserved holes in several banks, and marks banks 0, early bank 3, and early bank 4 as 1.8/3.3 V capable.
- `CPU_ALL_NOGP()` defines non-GPIO voltage-domain pseudo-pins `VDDQ_AVB0`, `VDDQ_AVB1`, and `VDDQ_AVB2` with 1.8/2.5 V IO-voltage control.
- `GPSR*`, `IP*SR*`, and `MOD_SEL4_*` macros define the function-option universe. The file repeatedly redefines `F_()` and `FM()` to use the same macro inventory for enum generation, pinmux marks, and register tables.
- `pinmux_data[]` maps each selectable function mark to the corresponding IPSR/GPSR field and, where needed, a module-select bit via `PINMUX_IPSR_MSEL()`.
- `pinmux_pins[]` is built from `PINMUX_GPIO_GP_ALL()` plus the non-GPIO pins.
- `pinmux_groups[]` and `pinmux_functions[]` provide the modern pinctrl grouping interface for device-tree pinctrl states.
- `pinmux_config_regs[]` describes GPSR0-7, IPSR registers for banks 0-7, and `MOD_SEL4`.
- `pinmux_drive_regs[]` describes per-pin drive-strength bitfields in DRVxCTRLy registers. Widths vary: many pins have 3-bit drive selectors, while some pins such as QSPI/RPC/PWM/error pins have 2-bit selectors.
- `pinmux_bias_regs[]` maps pull enable (`PUEN*`) and pull direction (`PUD*`) registers to pins, using `SH_PFC_PIN_NONE` for reserved bits.
- `pinmux_ioctrl_regs[]` lists POC registers used for IO-voltage selection.
- `r8a779h0_pin_to_pocctrl()` is the only custom function. It maps a pin ID to a POC register address and bit number, returning `-EINVAL` for pins without POC control.
- `r8a779h0_pin_ops` wires `pin_to_pocctrl`, `rcar_pinmux_get_bias`, and `rcar_pinmux_set_bias` into the common SoC operation hooks.

## Control flow

There is no local probe or interrupt flow. Runtime control is inverted through `r8a779h0_pinmux_info`: the common Renesas PFC driver receives a pinctrl or GPIO request, looks up a group/function/pin in these arrays, and writes the registers described here.

The generated flow is:

1. A consumer requests a named function/group, such as `avb1_rgmii` or `msiof2_txd`.
2. The common core finds the group in `pinmux_groups[]`, then applies the corresponding mux marks from the group `*_mux[]` array.
3. Each mark resolves through `pinmux_data[]` to GPSR/IPSR/MOD_SEL enum IDs.
4. Register descriptors in `pinmux_config_regs[]` tell the core which memory-mapped bitfield to update.
5. Optional pin configuration requests, such as drive strength, pull-up/down, or IO voltage, use `pinmux_drive_regs[]`, `pinmux_bias_regs[]`, and `r8a779h0_pin_to_pocctrl()`.

The function grouping is broad: audio clock; three Ethernet AVB instances; CAN FD 0-3 and CAN clock; HSCIF0-3; I2C0-3; external interrupts; MMC; MSIOF0-5; PCIe clock request; PWM0-4; QSPI0-1; SCIF0, SCIF1, SCIF3, SCIF4 and external SCIF clocks; SSI; and TPU outputs. AVB0/1 have both MII and RGMII groups; AVB2 has RGMII only. MMC and QSPI data groups use bus-width helper groups (`mmc_data1/4/8`, `qspi*_data2/4`).

## State and persistence behavior

The file has no mutable C state. Persistence is entirely hardware register state owned by the PFC block. The register descriptors point at memory-mapped PFC addresses in the `0xE605xxxx` and `0xE606xxxx` ranges. Once the common core writes GPSR/IPSR/MOD_SEL, drive, bias, or POC registers, that state persists in the controller until changed by another pinctrl/GPIO operation or reset. The `.unlock_reg = 0x1ff` field indicates the common R-Car PFC path must use the PMMR write-protection unlock sequence for protected registers.

## Dependencies and integration points

The file depends on `linux/errno.h`, `linux/io.h`, `linux/kernel.h`, and the local `sh_pfc.h` macro and type layer. Most behavior relies on the common Renesas PFC framework: macros such as `PORT_GP_CFG_*`, `PINMUX_CFG_REG`, `PINMUX_DRIVE_REG`, `PINMUX_BIAS_REG`, `SH_PFC_PIN_GROUP`, `BUS_DATA_PIN_GROUP`, and runtime helpers such as `rcar_pinmux_get_bias()`/`rcar_pinmux_set_bias()`.

The exported `r8a779h0_pinmux_info` is the integration point used by the SoC match table elsewhere in the Renesas pinctrl driver. Device-tree pinctrl states must use group and function names exactly matching the arrays in this file. GPIO numbering and pin configuration capabilities come from the generated pin tables and flags.

## Risks and edge cases

- The file is dense, macro-generated hardware data. A single wrong enum ordering, register address, bit offset, or group/mux pairing can silently configure the wrong physical pin.
- Sparse banks require care. Bank 2 omits pins 16 and 18, bank 4 has holes around 16-20 and 22, and multiple registers use `GROUP()` negative widths for reserved fields. Off-by-one mistakes in these reserved fields would misalign all following entries.
- `r8a779h0_pin_to_pocctrl()` supports only GP0[0:18], GP1[0:28], GP3[0:12], GP4[0:13], and the three AVB VDDQ pseudo-pins. Pins marked with IO voltage capability must stay aligned with this function, otherwise voltage configuration requests can fail with `-EINVAL` or hit the wrong POC bit.
- Some bias comments deserve review: in `PUEN5`, bit 1 maps `RCAR_GP_PIN(5, 1)` but the comment says `AVB0_AVTP_CAPTURE`; the surrounding bank 5 entries are AVB2 signals, so the comment appears inconsistent. This is comment-level unless generated documentation uses comments as truth.
- Shared pins are intentionally exposed under multiple logical groups, for example SCIF and HSCIF variants or PWM alternatives on CAN/I2C/audio pins. Board pinctrl states must avoid incompatible simultaneous selections.
- Non-GPIO VDDQ pins are configuration pseudo-pins, not normal GPIOs; users must not assume all `pinmux_pins[]` entries map to data registers.

## Test signals

Useful validation signals are compile-time and hardware/DT oriented. Build coverage should compile this file with the Renesas pinctrl driver enabled and catch enum or initializer mismatches. Static checks should verify that every group has matching pin and mux array lengths, every group named in a function exists, every `*_MARK` used in a mux appears in `pinmux_data[]`, and every pin with IO-voltage flags is accepted by `r8a779h0_pin_to_pocctrl()`. Runtime tests on R8A779H0 hardware should request representative pinctrl states for AVB0/1/2, QSPI, MMC, I2C, SCIF/HSCIF, CAN FD, bias, drive strength, and IO voltage, then confirm the expected GPSR/IPSR/MOD_SEL/DRV/PUEN/PUD/POC registers change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779h0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7203.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7264.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7264.c -->
