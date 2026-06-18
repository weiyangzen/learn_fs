# subset-b-005106 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7722.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7722.c

## Purpose

This file is the Renesas SuperH SH7722 PFC/GPIO hardware description consumed by the generic `sh-pfc` core. It is almost entirely declarative: it names SH7722 port pins, maps GPIO data/input/output/function symbols to mux data, exposes function GPIO names for board code, and describes the PFC register layout used to select GPIO direction, peripheral muxes, high-impedance behavior, and GPIO data bits.

The exported integration object is `sh7722_pinmux_info`, a `const struct sh_pfc_soc_info` named `sh7722_pfc`. There is no probe routine or local runtime algorithm in this file; the common Renesas PFC driver performs all registration and register programming from these tables.

## Important APIs, Types, and Data

- The top-level enum defines all selector IDs used by the core: `PINMUX_DATA_*`, `PINMUX_INPUT_*`, `PINMUX_OUTPUT_*`, peripheral marks, port function selectors, PSEL/HIZ/MSEL alternatives, and sentinels.
- `pinmux_data[]` binds port data symbols and peripheral marks to the selector IDs required to make that function active. It includes 377 `PINMUX_DATA` occurrences covering GPIO direction/data and muxed functions.
- `pinmux_pins[]` is the SH7722 GPIO pin list. It contains 149 `PINMUX_GPIO(...)` entries for sparse PTA-PTZ ports; zero entries in the data-register tables mark package/reserved holes such as missing PTC, PTE, PTF, PTG, PTJ, PTK, PTQ, PTR, PTS, PTT, PTU, PTV, PTW, PTX, PTY, and PTZ bits.
- `pinmux_func_gpios[]` exposes 228 `GPIO_FN(...)` function entries. The board-facing function surface covers SCIF0-2, SIO, CEU/VIO capture, LCDC main/sub LCD RGB and SYS modes, BSC, SBSC, IRQ0-7, SDHI, SIU ports A/B, audio, DMAC, VOU/DV output, CPG status, SIOF0/1, SIM, TSIF, IrDA, TPU, FLCTL/NAND, and KEYSC.
- `pinmux_config_regs[]` describes the control registers `PACR` through `PZCR`, `PSELA` through `PSELE`, `HIZCRA` through `HIZCRC`, and `MSELCRB` at the SH7722 PFC MMIO addresses. The mix of `PINMUX_CFG_REG` and `PINMUX_CFG_REG_VAR` records represents fixed 2-bit per-port control fields, variable selector fields, reserved holes, high-impedance options, LCD RGB/SYS selection, and VIO/VIO2 selection.
- `pinmux_data_regs[]` maps `PADR` through `PZDR` data registers to the corresponding port data IDs so GPIO value read/write paths can address the correct bit positions.
- `sh7722_pinmux_info` wires `.input`, `.output`, `.function`, `.pins`, `.func_gpios`, `.cfg_regs`, `.data_regs`, and `.pinmux_data` into the core.

## Control Flow

Initialization begins outside this file when the SH7722 platform selects `sh7722_pinmux_info`. The generic `sh-pfc` core registers the pin list and function GPIO namespace, then uses the enum ranges and table pointers in the SoC descriptor for all later operations.

For GPIO use, the core resolves a `PINMUX_GPIO` pin to the relevant CR entry for input/output/function selection and to the matching DR entry for data. For peripheral use, board or platform code requests a `GPIO_FN(...)` name; the core walks `pinmux_data[]` to determine which port control field, PSEL field, HIZ field, or MSEL field must be programmed. There is no local branching or callback here; control is table-driven through the common macros in `sh_pfc.h`.

## State and Persistence Behavior

All file-local data is static and read-only after boot. Runtime state is held in the PFC hardware registers and the generic PFC core, not in this file.

Configured CR/PSEL/HIZ/MSEL bits and GPIO DR values persist in hardware until reset, suspend/resume restoration, or another pinctrl/GPIO request changes them. The high-impedance registers are especially stateful because a wrong HIZ selection can disconnect an otherwise correctly muxed peripheral. This file defines no locking, allocation, caching, or suspend/resume policy.

## Dependencies and Integration Points

The file depends on `<linux/kernel.h>`, `<cpu/sh7722.h>`, and `sh_pfc.h`. The CPU header provides SH7722 GPIO numbering/name definitions, while `sh_pfc.h` provides `struct sh_pfc_soc_info`, `struct sh_pfc_pin`, `struct pinmux_func`, `struct pinmux_cfg_reg`, `struct pinmux_data_reg`, `PINMUX_*` construction macros, and `GPIO_FN`.

It integrates with the legacy SuperH board/platform pin setup model through function GPIO names rather than the newer pin-group/function arrays used by many R-Car descriptors. Downstream users include serial, LCD, camera, storage, NAND, keypad, audio, DMA handshake, IrDA, and bus-interface platform devices that request these mux names through the common SH PFC layer.

## Risks and Maintenance Notes

- Table ordering is the core risk. The enum ordering, `pinmux_data[]` selectors, and register field order must agree exactly with SH7722 hardware documentation.
- Reserved holes are represented as zeros in register groups. Accidentally filling a reserved bit or shifting later entries would route unrelated pads or touch undefined hardware bits.
- Several pads have multi-stage selection through port CR plus PSEL/HIZ/MSEL fields. A correct peripheral mark can still fail if one selector alternative is omitted or paired with the wrong option.
- LCD and video routing has overlapping RGB/SYS and VIO/VIO2 choices; board setup must choose a coherent set across LCDC, CEU, VOU, and `MSELCRB`.
- There are no compile-time semantic checks for electrical validity, package presence, or board-level conflicts. The macros catch some table shape problems but not wrong mux choices.

## Test Signals

Useful validation signals include building with SH7722 PFC support enabled, boot logs showing registration of `sh7722_pfc`, and pinmux debug output listing the expected PTA-PTZ GPIOs and 228 function GPIOs. Runtime smoke tests should exercise SCIF, LCD RGB/SYS, CEU/VIO, SDHI, FLCTL/NAND, KEYSC, SIOF, SIU audio, and IRQ pins on representative boards. GPIO tests should confirm input/output direction and data reads for sparse ports, while board tests should check that HIZ and LCD/VIO module selection bits do not leave requested peripherals disconnected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7723.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7723.c

## Purpose

This file is the SH7723-specific Renesas SuperH PFC pinmux table. It describes the GPIO-capable PTA-PTZ pins, alternate peripheral functions, selector registers, and GPIO data registers for the generic `sh-pfc` core. Like the adjacent SH7722 descriptor, it is a static hardware description rather than an active driver.

The exported object is `sh7723_pinmux_info`, named `sh7723_pfc`. It lets the common core register the SoC's GPIO pins and function GPIOs, then program SH7723 PFC registers when legacy board code requests a GPIO or peripheral mux.

## Important APIs, Types, and Data

- The top-level enum defines GPIO data/input/output IDs, GPIO function IDs for ports PTA-PTZ, PSEL alternative symbols, peripheral marks, and range sentinels.
- `pinmux_data[]` contains 479 `PINMUX_DATA` mappings. These connect each port's GPIO data path and each peripheral mark to the required port-function selector and PSEL alternative.
- `pinmux_pins[]` contains 170 sparse `PINMUX_GPIO(...)` entries. SH7723 has more complete PTA-PTZ coverage than SH7722, with holes still represented in pin/data tables for missing bits such as upper PTE, PG, PJ, PQ, PT, and PU variants.
- `pinmux_func_gpios[]` exposes 309 function GPIO names. Major surfaces include SCIF0-5 with alternative port placements, CEU/VIO, LCDC RGB/SYS, IRQ0-7, audio, SDHI0 on either PTD or PTS, SDHI1, SIUA/SIUB, IrDA, VOU/DV output, KEYSC, MSIOF0 on PTF or PTT/PTX, MSIOF1, TSIF, FLCTL/NAND, DMAC, ADC pins, CPG status, TPU outputs, BSC, and ATAPI.
- `pinmux_config_regs[]` describes `PACR` through `PZCR`, plus `PSELA`, `PSELB`, `PSELC`, and `PSELD`. The port CR registers select GPIO input/output/function on 2-bit fields; PSEL registers select among peripheral alternatives that share the same physical pin or module.
- `pinmux_data_regs[]` maps `PADR` through `PZDR` data registers to the GPIO data enum IDs.
- `sh7723_pinmux_info` provides the common core with the input/output/function enum ranges and table pointers for pins, function GPIOs, config registers, data registers, and mux data.

## Control Flow

At boot, the platform PFC registration path passes `sh7723_pinmux_info` to the common `sh-pfc` infrastructure. The core uses `.pins` and `.func_gpios` to publish GPIO and function names, and uses `.cfg_regs`, `.data_regs`, and `.pinmux_data` to convert pin requests into MMIO updates.

GPIO direction requests program the corresponding port CR field and data operations use the matching `P?DR` table entry. Peripheral mux requests resolve a `GPIO_FN(...)` mark through `pinmux_data[]`; the resulting selector sequence can include both a port function field and a PSEL field. This is important for duplicated functions such as SCIF and SDHI0 where the same controller can appear on multiple port groups.

## State and Persistence Behavior

The descriptor itself is immutable. Persistent state lives in hardware: CR fields determine whether pads are GPIO or peripheral functions, PSEL fields choose alternate routes, and DR bits hold GPIO output values or sampled input data. These hardware settings remain until reset or later reconfiguration by the PFC/GPIO core. There are no local caches, locks, workqueues, or save/restore callbacks in this file.

## Dependencies and Integration Points

The file includes `<linux/kernel.h>`, `<cpu/sh7723.h>`, and `sh_pfc.h`. It relies on CPU-specific GPIO constants and the shared PFC macros/types. Its public integration point is the `sh7723_pinmux_info` descriptor, which is selected by SH7723 platform code and consumed by the generic Renesas/SuperH PFC driver.

Peripheral integration is legacy function-GPIO based. Board code and platform devices request names such as `SCIF*_PT*_*`, `SDHI0*_PTD`, `SDHI0*_PTS`, `MSIOF0_PTF_*`, `MSIOF0_PTT_*`, `LCDC`, `VIO`, `ATAPI`, `FLCTL`, or `KEYSC` pins; the PFC core performs the corresponding register writes.

## Risks and Maintenance Notes

- Alternate placement is a major source of mistakes. SCIF, SDHI0, and MSIOF0 each have multiple route variants whose selector fields must match the chosen port pins.
- The 2-bit PSEL fields include reserved encodings represented by `0`. Any insertion or deletion can shift later fields and silently program wrong alternatives.
- ATAPI, BSC, LCDC, and VOU share many wide bus-style pins. Board-level requests must avoid conflicts that the static table cannot prevent by itself.
- Sparse ports and reserved data bits must remain aligned between `pinmux_pins[]`, `pinmux_data[]`, CR registers, and DR registers.
- The file has no dedicated bias, drive-strength, or voltage-control tables, so consumers expecting newer pinconf features will not find them here.

## Test Signals

Validation should include compile coverage for SH7723 PFC, successful boot-time registration of `sh7723_pfc`, and debug inspection of the 170 GPIO pins plus 309 function GPIOs. Runtime tests should cover both route alternatives for SCIF, SDHI0 PTD versus PTS, MSIOF0 PTF versus PTT/PTX, LCDC RGB/SYS pins, CEU/VIO capture, VOU output, FLCTL/NAND, ATAPI, ADC trigger/input pins, KEYSC matrix pins, and GPIO direction/data on sparse ports. Regression testing should include pin conflict scenarios where board files choose overlapping wide buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7723.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7724.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7724.c

## Purpose

This file is the SH7724 Renesas SuperH PFC descriptor, derived from the SH7723 style and extended for the SH7724 peripheral set. It gives the generic `sh-pfc` core the static map from PTA-PTZ pins to GPIO modes, peripheral function marks, selector registers, and GPIO data registers.

The exported `sh7724_pinmux_info` descriptor is named `sh7724_pfc`. It is the only runtime-facing object in the file and is consumed by common PFC code selected by SH7724 platform support.

## Important APIs, Types, and Data

- The top-level enum defines GPIO data/input/output IDs, per-port function IDs, PSEL alternatives (`PSA*` through `PSE*`), peripheral marks, and sentinels.
- `pinmux_data[]` contains 487 `PINMUX_DATA` mappings. It joins GPIO data symbols, function marks, and PSEL alternatives into the sequences the core writes for each mux request.
- `pinmux_pins[]` contains 180 `PINMUX_GPIO(...)` entries, covering a wider SH7724 PTA-PTZ GPIO surface than SH7723. Reserved package holes remain explicit as zeros in the register/data tables.
- `pinmux_func_gpios[]` exposes 307 function GPIO names. The board-facing surface covers BSC, KEYSC, ATAPI, TPU, LCDC, SCIF0-5, FSI, AUD, VIO/VIO0/VIO1, RMII Ethernet, system status, VOU/DV output, MSIOF0/1, DMAC, SDHI0/1, MMC, IrDA, TSIF, and INTC IRQ0-7.
- `pinmux_config_regs[]` describes `PACR` through `PZCR` and `PSELA` through `PSELE`. These 16-bit registers encode GPIO direction/function state and module/route alternatives for the expanded SH7724 pin set.
- `pinmux_data_regs[]` maps `PADR` through `PZDR` data registers to the corresponding GPIO data symbols.
- `sh7724_pinmux_info` provides the generic core with enum ranges and pointers to all static tables.

## Control Flow

There is no local executable control path beyond static initialization. SH7724 platform setup selects `sh7724_pinmux_info`; the common `sh-pfc` core then registers GPIOs and function GPIOs and services requests.

When a GPIO is requested, the core uses the CR register tables to set input/output mode and the DR table for data access. When a peripheral function is requested, the core resolves the function mark through `pinmux_data[]`; the result can require both the port function setting and a PSEL field. The control path is therefore a data-driven lookup from requested symbol to one or more register-field writes.

## State and Persistence Behavior

The file contains static read-only descriptor data and no mutable software state. Hardware register state persists across normal operation until reset or reconfiguration. PSEL fields persist route choices for shared controllers such as SCIF, FSI/audio, video, SDHI/MMC, Ethernet, and ATAPI; GPIO data registers persist output values for configured output pins. Suspend/resume and synchronization are responsibilities of the shared PFC/GPIO infrastructure.

## Dependencies and Integration Points

The file includes `<linux/kernel.h>`, `<cpu/sh7724.h>`, and `sh_pfc.h`. It depends on SH7724 CPU GPIO definitions and common Renesas PFC macros such as `PINMUX_GPIO`, `GPIO_FN`, `PINMUX_DATA`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, and `PINMUX_DATA_REG`.

Integration occurs through the legacy function-GPIO namespace. Board files and platform devices select named functions for external memory, ATAPI, LCD, video capture/output, RMII Ethernet, serial ports, FSI/audio, SDHI/MMC, MSIOF, interrupts, and keypad hardware. The common PFC core translates those names into MMIO writes using this descriptor.

## Risks and Maintenance Notes

- SH7724 has many mutually exclusive wide interfaces. BSC, ATAPI, LCDC, VIO, VOU, Ethernet, SDHI, MMC, and FSI routes can overlap physically, so board-level configuration must be coherent.
- PSEL register alignment is fragile. `PSELA`-`PSELE` encode many one-bit and two-bit choices; incorrect ordering causes valid-looking function names to select the wrong route.
- Function naming distinguishes similar peripherals and routes, such as VIO0 versus VIO1, SCIF2_L versus SCIF2_V, and SCIF3_V versus SCIF3_I. Renaming or collapsing these names would break legacy board users.
- Sparse GPIO holes in ports PG, PJ, PS, and others must remain zeros in CR/DR tables. Filling them can expose unavailable pins or program reserved bits.
- There are no local pinconf tables for bias, drive strength, or voltage switching; support is limited to mux, GPIO direction, and data register behavior.

## Test Signals

Useful tests include building SH7724 PFC support, booting a board that registers `sh7724_pfc`, and checking debug output for 180 GPIO pins and 307 function GPIOs. Hardware smoke tests should cover external bus pins, ATAPI, LCDC, VIO0/VIO1 capture, VOU output, RMII Ethernet, FSI/AUD audio, SCIF route variants, SDHI0/1, MMC, MSIOF0/1, IrDA, TSIF, KEYSC, and IRQ lines. GPIO tests should verify CR direction changes and DR reads/writes for ports with reserved holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7734.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7734.c

## Purpose

This file is the Renesas SH7734 PFC hardware description for the generic `sh-pfc` core. Compared with the older SH7722/SH7723/SH7724 files, it uses the later GP-bank/GPSR/IPSR/MOD_SEL style: GPIO pins are generated as banks `GP_0_0` through `GP_5_11`, GPSR selects GPIO versus peripheral function, IPSR selects alternate pin functions, and MOD_SEL selects module-level route alternatives.

The exported object is `sh7734_pinmux_info`, named `sh7734_pfc`. It includes an `.unlock_reg` of `0xFFFC0000`, indicating that writes to the PFC block require the common PMMR-style unlock handling.

## Important APIs, Types, and Data

- `CPU_ALL_GP`, `_GP_DATA`, `_GP_INOUTSEL`, `_GP_INDT`, `GP_INOUTSEL`, and `GP_INDT` generate repetitive banked GPIO definitions for five full 32-pin banks and one 12-pin bank.
- The enum defines data/input/output/function IDs for all GP pins, GPSR selector symbols, IPSR symbols for alternate functions, and MOD_SEL symbols for module route selection.
- `pinmux_data[]` starts with generated GPIO data mappings via `PINMUX_DATA_GP_ALL()` and then maps hundreds of peripheral marks to GPSR/IPSR/MOD_SEL selector combinations.
- `pinmux_pins[]` is generated with `PINMUX_GPIO_GP_ALL()`, giving the core the banked GPIO pin list.
- `pinmux_func_gpios[]` exposes 609 `GPIO_FN(...)` occurrences. The function surface includes address/data bus and chip-select pins, LCD data/control alternatives, SDHI0/1/2 and MMC, FLCTL/NAND, RSPI/QSPI, Ethernet ET0 and RMII0, VI0/VI1 video input, DU0 display output, SCIF and HSCIF variants, HSPI, SSI/audio clocks, CAN, I2C pins, USB overcurrent, interrupt alternatives, host interface pins, IEBUS, MLB, timer/MTU2/TPU signals, DMA request/acknowledge, and system clocks/status.
- `pinmux_config_regs[]` describes `GPSR0`-`GPSR5`, `IPSR0`-`IPSR11`, `MOD_SEL1`, `MOD_SEL2`, and GPIO `INOUTSEL0`-`INOUTSEL5`. `INOUTSEL5` is variable-width because only bank 5 pins 0-11 exist.
- `pinmux_data_regs[]` maps `INDT0`-`INDT5` data registers to banked GPIO data symbols, with bank 5 upper bits reserved.
- `sh7734_pinmux_info` supplies the core with the unlock register, enum ranges, generated pins, function GPIOs, config/data registers, and mux data.

## Control Flow

Platform initialization selects `sh7734_pinmux_info` and hands it to the common `sh-pfc` driver. The core unlocks PFC writes through `.unlock_reg`, registers the generated GPIO pins and function GPIO namespace, and uses the table set for later mux and GPIO operations.

Peripheral mux requests resolve a `GPIO_FN(...)` mark into GPSR/IPSR and, where needed, MOD_SEL writes. GPSR chooses whether a pin is GPIO or function; IPSR chooses the function encoded on that pin; MOD_SEL chooses between module route alternatives such as SCIF, SDHI, Ethernet, HSPI, HSCIF, CAN, LCDC, VIN, SSI, MMC, FLCTL, and timer variants. GPIO direction uses `INOUTSELn`, and GPIO data uses `INDTn`.

## State and Persistence Behavior

The file has no mutable software state. Register state persists in hardware: GPSR/IPSR/MOD_SEL define mux routing, `INOUTSELn` defines GPIO direction, and `INDTn` holds output or sampled input values. The unlock register is an integration detail for protected writes, not a cached state field. Any suspend/resume preservation, locking, and conflict handling is done by the shared `sh-pfc` core.

## Dependencies and Integration Points

The file depends on `<linux/kernel.h>`, `<cpu/sh7734.h>`, and `sh_pfc.h`. It uses the shared GP-bank macros and the common SH PFC data structures. The descriptor integrates with legacy SH platform pin setup through function GPIO names, and with the common core's GPSR/IPSR/MOD_SEL machinery.

Board and peripheral integrations include external memory, LCD/DU display, video input, Ethernet/RMII, SD/MMC, serial ports, SPI/HSPI/QSPI, audio SSI, CAN, I2C, USB overcurrent, host interface, timers, DMA, interrupts, and MediaLB. Because many functions have `_A`, `_B`, `_C`, `_D`, or `_E` alternatives, MOD_SEL fields are part of the public contract even though callers request only the function name.

## Risks and Maintenance Notes

- The GPSR/IPSR/MOD_SEL relationship is fragile. A function mark must include every required selector; otherwise the pin can be switched to function mode but still route the wrong peripheral instance.
- `MOD_SEL1` and `MOD_SEL2` contain many route selectors with reserved encodings. Incorrect widths or ordering can corrupt unrelated modules.
- Bank 5 is only 12 pins wide. Generated helpers and register groups must keep upper bits reserved in `INOUTSEL5` and `INDT5`.
- The `.unlock_reg` is mandatory for protected PFC writes. Removing or changing it can make otherwise correct table entries fail at runtime.
- The function GPIO table is large and dense; similar names such as SD0/SD1/SD2, ET0/RMII0, VI0/VI1, SCIF/HSCIF, HSPI variants, and LCD A/B alternatives are easy to mix up.
- There are no local bias, drive-strength, or voltage-control descriptors, so pinconf support is limited to what the generic core can infer from mux/GPIO tables.

## Test Signals

Validation should include a build with SH7734 PFC enabled, successful registration of `sh7734_pfc`, and confirmation that protected writes through `0xFFFC0000` succeed. Debug inspection should show GP banks 0-4 with 32 pins and bank 5 with 12 pins, plus the expected function GPIO namespace. Hardware smoke tests should cover representative GPSR/IPSR/MOD_SEL combinations: SDHI/MMC, Ethernet/RMII, SCIF/HSCIF, HSPI/RSPI/QSPI, LCD/DU, VI0/VI1, SSI/audio, CAN, I2C, USB overcurrent, IRQ alternatives, host interface, DMA, and bank-5 GPIO direction/data behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7734.c -->
