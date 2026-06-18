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
