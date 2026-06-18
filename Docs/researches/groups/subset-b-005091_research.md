# subset-b-005091 Research

Work item: `subset-b-005091`

Sources:
- `sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77470.c`
- `sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7778.c`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77470.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77470.c

## Purpose

`pfc-r8a77470.c` is the Renesas RZ/G1C / R8A77470 pin-function-controller description consumed by the shared `sh_pfc` pinctrl driver. It does not implement a standalone driver probe path. Instead, it exports `r8a77470_pinmux_info` under `CONFIG_PINCTRL_PFC_R8A77470`, describing all package pins, GPIO-capable pins, non-GPIO pins, pin mux alternatives, named pin groups, logical functions, register bit layouts, bias registers, and the small SoC-specific POC voltage hook required by the common PFC core.

The file is mostly declarative hardware data. Its correctness determines whether device tree pinctrl states select the intended peripheral functions and whether generic pin configuration requests such as pull-up, pull-down, and I/O voltage changes touch the right PFC registers.

## Important APIs, Types, And Data

- `CPU_ALL_GP(fn, sfx)` expands the GPIO-capable pin inventory. It covers bank 0 partial pins, banks 1 and 2, selected bank 3 pins, bank 4 partial pins, and bank 5. Many SD/MMC-oriented pins include `SH_PFC_PIN_CFG_IO_VOLTAGE_18_33`; most pins include `SH_PFC_PIN_CFG_PULL_UP`.
- `CPU_ALL_NOGP(fn)` describes non-GPIO package pins such as `ASEBRK#/ACK`, `NMI`, `PRESETOUT#`, and JTAG pins with pull capability metadata.
- The primary anonymous `enum` builds the common `sh_pfc` numeric namespace: `PINMUX_DATA_*`, `PINMUX_FUNCTION_*`, GPSR function selectors, IPSR function selectors, MOD_SEL selector values, and `PINMUX_MARK_*` symbols.
- `pinmux_data[]` links visible mux marks to the GPSR/IPSR/MOD_SEL selector symbols. It uses `PINMUX_SINGLE()`, `PINMUX_IPSR_GPSR()`, and `PINMUX_IPSR_MSEL()` to encode whether a mark is a simple GPSR function or also needs a mode-select bitfield.
- `pinmux_pins[]` is produced from `PINMUX_GPIO_GP_ALL()` plus `PINMUX_NOGP_ALL()`.
- Per-function pin arrays and mux arrays define groups for AVB, DU0/DU1 display, I2C0-4, MMC, QSPI0/1, SCIF0-5, SCIF clocks, SDHI0-2, USB0/1, and VIN0/1.
- `pinmux_groups[]` exposes the group catalog to the pinctrl core. It includes bus-width variants through `BUS_DATA_PIN_GROUP()`, SDHI aliases/subsets for the MMC-backed SDHI1 pins, and VIN data-width variants.
- `pinmux_functions[]` maps function names, such as `avb`, `du0`, `i2c3`, `sdhi2`, or `vin1`, to the group-name arrays consumed by pinctrl.
- `pinmux_config_regs[]` maps the hardware GPSR, IPSR, and MOD_SEL registers to function IDs. R8A77470 uses PFC/PMMR around `0xe6060000`, GPSR0-5 at `0xe6060004` through `0xe6060018`, IPSR0-17 at `0xe6060040` through `0xe6060084`, and MOD_SEL0-2 at `0xe60600c0` through `0xe60600c8`.
- `r8a77470_pin_to_pocctrl()` maps selected pins to POCCTRL bits for 1.8 V / 3.3 V I/O voltage control.
- `pinmux_bias_regs[]` maps pull-up and pull-down capability to PUPR registers at `0xe6060100` through `0xe6060114`.
- `r8a77470_pfc_ops` installs the SoC hook set: `.pin_to_pocctrl`, `.get_bias = rcar_pinmux_get_bias`, and `.set_bias = rcar_pinmux_set_bias`.
- `r8a77470_pinmux_info` is the exported `struct sh_pfc_soc_info` binding all tables to the common core.

## Control Flow

This file has no local probe or interrupt flow. Runtime control is driven by the shared Renesas PFC core after platform matching selects `r8a77470_pinmux_info`.

1. The common PFC driver receives a pinctrl request from device tree or from the Linux pinctrl subsystem.
2. Function/group selection resolves a function name through `pinmux_functions[]`, then resolves a group through `pinmux_groups[]`.
3. The group mux marks are looked up in `pinmux_data[]`, which indicates the GPSR/IPSR function code and any MOD_SEL sideband selector needed for alternate pin routes.
4. The shared core writes the relevant register fields described by `pinmux_config_regs[]`. The `unlock_reg` value `0xe6060000` identifies PMMR, which must be paired with protected PFC register writes.
5. Pin configuration requests for pull bias use `r8a77470_pfc_ops.get_bias` and `.set_bias`, which delegate to common R-Car helpers and consult `pinmux_bias_regs[]`.
6. I/O voltage requests use the SoC-specific `.pin_to_pocctrl` hook. Only pins in ranges `GP0_5..GP0_10`, `GP0_13..GP0_22`, and `GP4_14..GP4_19` are accepted; all others return `-EINVAL` through the negative bit value.

## State And Persistence

The source contains only static const descriptions plus the small pure mapping helper. It does not allocate memory, persist state, schedule work, or store runtime state across calls. Hardware state persists in PFC registers after the common driver writes them:

- GPSR registers choose GPIO vs peripheral function for each pin.
- IPSR registers choose among multiplexed peripheral alternatives.
- MOD_SEL registers choose shared alternate routes for functions such as AVB, I2C, SCIF, HSCIF, MSIOF, SSI, TMU, and CAN.
- PUPR registers hold pull-up and pull-down configuration.
- POCCTRL controls voltage domain selection for a small set of dual-voltage pins.

The static arrays must remain internally consistent because they are the persistent source of truth for all runtime register writes.

## Dependencies And Integration Points

- Includes `<linux/errno.h>` for `-EINVAL`, `<linux/kernel.h>` for kernel helpers, and local `"sh_pfc.h"` for all PFC macros and data structures.
- Depends on the shared Renesas PFC infrastructure for parsing `struct sh_pfc_soc_info`, resolving `PINMUX_*` data, writing protected registers, and applying bias/voltage pinconf.
- Integrates with Linux pinctrl through group and function names referenced by Renesas board/device-tree pinctrl states.
- Integrates with GPIO through `PINMUX_GPIO_GP_ALL()` and the GPIO bank/pin numbering encoded by `RCAR_GP_PIN()`.
- Integrates with peripheral drivers indirectly: Ethernet AVB, display unit, I2C, MMC/SDHI, QSPI, SCIF serial, USB, and VIN drivers rely on matching group names and mux settings.

## Risks And Review Notes

- Table drift is the dominant risk. A wrong `RCAR_GP_PIN()` entry, mux mark, IPSR selector, or MOD_SEL selector silently routes a board pin to the wrong peripheral.
- `pinmux_data[]` and `pinmux_config_regs[]` must agree. A mark exposed in a group but missing from `pinmux_data[]` will fail selection; a selector present in `pinmux_data[]` but absent or misplaced in a register table can program the wrong bits.
- `r8a77470_pin_to_pocctrl()` intentionally accepts only three pin ranges. If CPU pin capability metadata and this hook diverge, generic I/O voltage pinconf may be advertised but fail, or worse, touch the wrong POCCTRL bit.
- Reserved fields in `PINMUX_CFG_REG_VAR()` and zero entries in IPSR groups protect hardware-reserved encodings. Off-by-one field widths are high impact because every following selector shifts.
- SDHI1 reuses MMC pins through subset/alias groups. That sharing must match board-level usage because two logical functions contend for the same physical pins.
- Bias register arrays include `SH_PFC_PIN_NONE` holes and non-GPIO pins. Incorrect holes may expose pull configuration for pins with no hardware support or hide valid pull support.
- The `#ifdef CONFIG_PINCTRL_PFC_R8A77470` guard means the exported SoC info exists only when the Kconfig symbol is enabled. Build coverage should include that configuration.

## Test Signals

- Build signal: compile with `CONFIG_PINCTRL_PFC_R8A77470=y` or `m` and warnings enabled; macro-generated tables catch many missing enum/mark references at compile time.
- Static consistency signal: every group mux mark should resolve through `pinmux_data[]`, and every referenced function ID should appear in the correct GPSR/IPSR/MOD_SEL register field.
- Device-tree signal: board DTS pinctrl states using groups such as `sdhi0_data4`, `sdhi1_ctrl`, `avb_mii_tx_rx`, `du0_rgb888`, `scif*_data_*`, and `vin*_data*` should bind without unknown group/function errors.
- Runtime signal: inspect pinctrl debugfs for expected pins, groups, functions, mux owner, and pinconf state after applying board pinctrl states.
- Electrical signal: verify pull-up/pull-down and 1.8 V / 3.3 V pinconf only succeeds on pins described as supporting those options, especially SD/MMC pins covered by POCCTRL.
- Hardware smoke signal: boot on R8A77470/RZ/G1C hardware and exercise SDHI/MMC, serial consoles, AVB or Ethernet pins, display output, USB power/overcurrent pins, and VIN inputs that rely on these tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a77470.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7778.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7778.c

## Purpose

`pfc-r8a7778.c` is the Renesas R-Car M1A / R8A7778 pin-function-controller description for the shared `sh_pfc` driver. It exports `r8a7778_pinmux_info`, which describes package pins, GPIO banks, non-GPIO chip-select/clock pins, mux functions, named pin groups, function-to-group mappings, protected PFC register fields, and pull-up registers.

Like other Renesas PFC SoC files, the source is a declarative hardware contract rather than an active driver. The shared PFC core uses these tables to translate pinctrl group/function names into GPSR, IPSR, MOD_SEL, and PUPR register writes.

## Important APIs, Types, And Data

- `CPU_ALL_GP(fn, sfx)` describes five GPIO banks: four full 32-pin banks and bank 4 with 27 pins. All GPIO-capable pins are marked with `SH_PFC_PIN_CFG_PULL_UP`.
- `CPU_ALL_NOGP(fn)` describes non-GPIO package pins `CLKOUT`, `CS0`, and `CS1_A26`.
- The primary anonymous `enum` builds the `sh_pfc` pinmux namespace, including data values, function values, GPSR selectors, IPSR selectors, MOD_SEL selectors, and mux marks.
- `pinmux_data[]` ties marks to function selectors with `PINMUX_SINGLE()`, `PINMUX_IPSR_GPSR()`, `PINMUX_IPSR_MSEL()`, `PINMUX_IPSR_NOGP()`, and `PINMUX_IPSR_NOGM()`. The `NOGP`/`NOGM` entries are important because some functions live on package pins that are not GPIO-capable.
- `pinmux_pins[]` exposes all GPIO and non-GPIO pins to the shared core.
- Helper macros `SH_PFC_PINS()` and `SH_PFC_MUX*()` generate the many `*_pins[]` and `*_mux[]` arrays. Domain-specific wrappers define groups for audio clocks, CAN, Ethernet RMII, HSCIF, HSPI, I2C, local bus state controller, MMC, SCIF, SDHI, SSI, USB, and VIN.
- `pinmux_groups[]` registers all named groups, including bus-width variants for MMC and SDHI through `BUS_DATA_PIN_GROUP()`.
- Function group-name arrays and `pinmux_functions[]` expose logical functions: `audio_clk`, `can0`, `can1`, `ether`, `hscif0`, `hscif1`, `hspi0`, `hspi1`, `hspi2`, `i2c1`, `i2c2`, `i2c3`, `lbsc`, `mmc`, `scif_clk`, `scif0` through `scif5`, `sdhi0` through `sdhi2`, `ssi`, `usb0`, `usb1`, `vin0`, and `vin1`.
- `pinmux_config_regs[]` maps PFC registers at base `0xfffc0000`: GPSR0-4, IPSR0-10, and MOD_SEL0-1.
- `pinmux_bias_regs[]` maps pull-up capability through PUPR0-5 at `0xfffc0100` through `0xfffc0114`.
- `r8a7778_pfc_ops` provides bias operations via `rcar_pinmux_get_bias` and `rcar_pinmux_set_bias`.
- `r8a7778_pinmux_info` binds the data arrays and protected-write PMMR address into a `struct sh_pfc_soc_info`.

## Control Flow

Runtime flow is owned by the common PFC core:

1. Platform matching selects `r8a7778_pinmux_info`.
2. Pinctrl requests identify a function and group by string name from device tree or pinctrl consumers.
3. The core resolves the group in `pinmux_groups[]`, then uses that group's mux mark array.
4. Each mark maps through `pinmux_data[]` to GPSR/IPSR and, where needed, MOD_SEL selector values.
5. Register writes are generated from `pinmux_config_regs[]` and protected via PMMR at `0xfffc0000`.
6. Pull bias pinconf calls use `r8a7778_pfc_ops` and `pinmux_bias_regs[]`.

There is no SoC-specific voltage-control hook in this file. Compared with R8A77470, R8A7778 only wires bias get/set operations into the common helpers.

## State And Persistence

The C file itself stores no mutable runtime state. All state is either compile-time constant table data or hardware state written by the shared PFC driver:

- GPSR0-4 select GPIO/function mode for GPIO banks.
- IPSR0-10 select alternate function encodings for multiplexed pins.
- MOD_SEL0-1 select shared route variants such as SCIF, SSI, VIN, SDHI, IRQ, DMA request, CAN, HSCIF, HSPI, GPS, FM, TSIF, and I2C alternatives.
- PUPR0-5 hold pull-up configuration for supported pins.

Because all runtime decisions are table-driven, persistence risk is primarily in register mapping accuracy rather than algorithmic state management.

## Dependencies And Integration Points

- Includes `<linux/io.h>`, `<linux/kernel.h>`, `<linux/pinctrl/pinconf-generic.h>`, and local `"sh_pfc.h"`.
- Depends on the Renesas `sh_pfc` common code for `struct sh_pfc_soc_info`, register programming, PMMR unlock handling, group/function registration, and generic pinconf integration.
- Integrates with Linux pinctrl by exposing stable group/function names used from device tree.
- Integrates indirectly with drivers for audio/SSI, CAN, Ethernet RMII, HSCIF/SCIF serial, HSPI, I2C, local bus, MMC/SDHI, USB power/over-current, and VIN capture.
- Non-GPIO pins (`CLKOUT`, `CS0`, `CS1_A26`) are first-class pinctrl resources for LBSC, HSPI, SSI, I2C, and SCIF alternatives.

## Risks And Review Notes

- The file uses a dense macro style. Compile-time type checks are limited; a wrong pin number or wrong mux mark can compile but route a physical pin incorrectly.
- Several groups share the same physical pins across functions. Examples include serial/HSCIF/HSPI overlaps, SDHI/MMC overlaps, and non-GPIO pins reused by LBSC, I2C, HSPI, SSI, and SCIF alternatives. Board pinctrl states must avoid incompatible simultaneous use.
- `PINMUX_IPSR_NOGP()` and `PINMUX_IPSR_NOGM()` entries are easy to mishandle because they refer to non-GPIO package pins. Missing these paths would break muxing for `CLKOUT`, `CS0`, and `CS1_A26` alternatives.
- Register field widths in `PINMUX_CFG_REG_VAR()` must match hardware exactly. R8A7778 mixes 1-, 2-, 3-, and 4-bit IPSR fields with reserved gaps; one width error corrupts all following fields in the same register descriptor.
- `pinmux_groups[]`, function group arrays, and generated `*_pins[]`/`*_mux[]` arrays must remain in sync. A group omitted from the function array is unreachable from normal pinctrl selection even if its pin and mux arrays exist.
- Bias metadata is pull-up only in the register descriptors; there is no pull-down register coverage. Generic pinconf requests for unsupported bias modes should fail cleanly through common helpers.
- The file has no `#ifdef CONFIG_PINCTRL_PFC_R8A7778` guard around the exported info, unlike some neighboring SoC files. Build integration relies on the compilation unit selection in Kconfig/Makefile.

## Test Signals

- Build signal: compile the Renesas pinctrl driver with R8A7778 support and warning checks; unresolved marks or enum values should fail at compile time.
- Static table signal: verify every group mux mark resolves in `pinmux_data[]` and every selector appears in the expected GPSR/IPSR/MOD_SEL register field.
- Device-tree signal: validate DTS pinctrl states for groups such as `ether_rmii`, `sdhi*_data4_*`, `mmc_data8`, `scif*_data_*`, `hspi*_a/b`, `i2c*_a/b/c`, `lbsc_*`, and `ssi*`.
- Runtime debugfs signal: inspect registered pins, groups, functions, selected mux owners, and pinconf state under pinctrl debugfs on R8A7778 hardware.
- Hardware smoke signal: exercise serial console, SDHI/MMC, Ethernet RMII, USB PENC/OVC pins, SSI/audio clocks, local bus chip selects, and VIN paths used by the board.
- Negative pinconf signal: unsupported bias or voltage configuration should fail rather than silently writing unrelated registers; this is especially important because no POC voltage hook is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a7778.c -->
