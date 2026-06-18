# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f769.c

## Purpose

`pinctrl-stm32f769.c` describes the STM32F769 pin multiplexing matrix and registers the corresponding built-in platform driver. It is a full 168-pin PA0-PK7 table like F746, but with expanded F769-specific alternate functions. Notable additions and increases include CAN3, MDIOS, DFSDM, SDMMC2, additional UART4/UART5/UART7 routes, SPI6, DSI, broader LCD mappings, and more QuadSPI/FMC coverage.

The file is data-driven. It gives the common STM32 pinctrl core enough information to translate device-tree pinctrl states into hardware alternate-function numbers for the F769 family.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32f769_pins[]`: static F769 descriptor table with 168 pin entries.
- `STM32_PIN(PINCTRL_PIN(...), STM32_FUNCTION(...), ...)`: each entry binds a pin name/number to AF-slot names.
- `static struct stm32_pinctrl_match_data stm32f769_match_data`: references the descriptor table and array size.
- `static const struct of_device_id stm32f769_pctrl_match[]`: matches device-tree compatible `st,stm32f769-pinctrl`.
- `static struct platform_driver stm32f769_pinctrl_driver`: delegates probe to `stm32_pctl_probe`.
- `stm32f769_pinctrl_init()` and `arch_initcall`: early platform-driver registration.

Descriptor content includes common STM32 families and F769-oriented expansions: `DFSDM_*` appears widely, `SDMMC1_*` and `SDMMC2_*` coexist, `CAN3_*` appears in addition to CAN1/CAN2, `MDIOS_MDC/MDIO` is present, SPI6 mappings are broader, and display-related `LCD_*` and `DSI*` alternates are dense.

## Control Flow

The file follows the standard STM32 descriptor-driver sequence:

1. `arch_initcall` invokes `stm32f769_pinctrl_init()`.
2. The init function registers `stm32f769_pinctrl_driver`.
3. OF matching selects the driver for `st,stm32f769-pinctrl` nodes.
4. The common `stm32_pctl_probe()` reads `.data = &stm32f769_match_data`.
5. The common driver registers pinctrl entities and later programs pinmux state according to requests from board and peripheral drivers.

All device-specific branching is expressed through the descriptor table rather than local code.

## State and Persistence

This file contains immutable static metadata. It has no local dynamic state, no allocations, no refcounting, no locks, and no persistent storage. Hardware state and suspend/resume behavior are outside this file, in the common STM32 pinctrl core and platform power-management paths.

The match data does not enable package-specific filtering or newer security/I/O-control flags. All described pins are exposed to the common driver for this compatible.

## Dependencies and Integration Points

- Relies on Linux OF/platform driver infrastructure for binding.
- Relies on `pinctrl-stm32.h` for descriptor layout and `stm32_pctl_probe`.
- Integrates with DTS consumers through exact function strings such as `SDMMC2_D0`, `DFSDM_DATIN*`, `MDIOS_MDIO`, `CAN3_RX`, `QUADSPI_BK*`, `LCD_*`, and `FMC_*`.
- Feeds peripheral drivers for storage, audio, display/camera, memory, Ethernet/MDIO, USB, serial, timers, CAN, and debug/trace by making their pin states selectable.

## Risks and Edge Cases

- F769 has many more valid alternatives per pin than F746. Reviewers should avoid assuming sibling F7 AF numbers are interchangeable.
- DFSDM, SDMMC2, QuadSPI, FMC, DSI/LCD, and Ethernet/MDIOS share high-value pins; legal individual pin states can still conflict at board level.
- Combined labels for MII/RMII, timer channel/break, and serial signal variants are part of the ABI consumed by existing DTS files.
- Since the descriptor table is the only SoC-specific source of truth, typos in names or AF slots may not be caught until a specific peripheral route is tested on hardware.
- The lack of package masks can expose pins that are not bonded out on some package variants.

## Test Signals

- Build the kernel object and verify no macro/array issues.
- Boot an STM32F769 board DTS and confirm the `stm32f769-pinctrl` platform driver probes.
- Inspect pinctrl debugfs for 168 pins and expected F769-specific functions.
- Exercise routes for DFSDM, SDMMC2, CAN3, MDIOS, QuadSPI, DSI/LCD, FMC, Ethernet, and SPI6 on hardware or board tests.
- For descriptor edits, run DTS grep/build checks for affected function names and compare selector numbers against F769 reference documentation.
