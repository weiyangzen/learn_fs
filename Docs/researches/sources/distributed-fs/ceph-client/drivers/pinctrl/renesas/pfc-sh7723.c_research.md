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
