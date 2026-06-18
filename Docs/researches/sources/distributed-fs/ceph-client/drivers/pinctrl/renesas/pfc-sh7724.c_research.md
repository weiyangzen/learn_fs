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
