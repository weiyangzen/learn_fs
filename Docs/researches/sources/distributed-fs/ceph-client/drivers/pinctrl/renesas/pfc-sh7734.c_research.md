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
