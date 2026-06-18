# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-emev2.c

## Purpose
`pfc-emev2.c` is the SoC-specific pinmux data table for the Renesas Emma Mobile EV2 PFC. It describes pins, data marks, mux groups, functions, and PFC configuration registers, then exports `emev2_pinmux_info` for the common `sh-pfc` core.

## Important Data And Macros
- `CPU_ALL_PORT()` and `CPU_ALL_NOGP()` expand repeated GPIO-capable and no-GPIO pin lists.
- The large enum defines `PINMUX_DATA_*`, `PINMUX_FUNCTION_*`, and `PINMUX_MARK_*` IDs for data, function selector, and mux mark spaces.
- `pinmux_pins[]` lists GPIO-capable `PORT#` pins plus no-GPIO LCD pins.
- `pinmux_data[]` maps marks to one or more enum IDs used by `sh_pfc_config_mux()`.
- `EMEV_MUX_PIN()` creates single-pin group arrays.
- Many `*_pins[]` and `*_mux[]` arrays describe peripheral groups for external bus, camera, CompactFlash, DTV, IIC, JTAG, LCD/YUV, NTSC, PWM, SD/SDIO, TP33, UART, USB, and USI.
- `pinmux_groups[]` collects groups, including bus-width variants created by `BUS_DATA_PIN_GROUP()`.
- `pinmux_functions[]` maps user-visible function names to group lists.
- `pinmux_config_regs[]` describes GPSR and CHG_PINSEL registers at physical addresses around `0xe0140200` to `0xe01402a8`.
- `emev2_pinmux_info` publishes all data to the common PFC core.

## Control Flow And Integration
This file has no probe function. It is linked when `CONFIG_PINCTRL_PFC_EMEV2` is enabled. `core.c` includes `emev2_pinmux_info` in its OF match table for `renesas,pfc-emev2`. At runtime the common core receives this static table, registers pins/groups/functions, and uses `pinmux_data[]` plus `pinmux_config_regs[]` to program register fields when a pinctrl state requests one of the groups/functions.

Mux application uses the common flow: a pinctrl group chooses marks from a `*_mux[]` array, the core resolves each mark in `pinmux_data[]`, and then writes the corresponding GPSR/CHG_PINSEL fields from `pinmux_config_regs[]`.

## State And Persistence
All file-local data is immutable. Hardware state persists in EMEV2 PFC registers. The exported `sh_pfc_soc_info` does not include GPIO `data_regs`, drive, bias, or custom ops in this file, so this table primarily drives mux selection and pin/group/function enumeration.

## Dependencies
The file depends on local `sh_pfc.h` macros and types such as `SH_PFC_PIN_CFG`, `PINMUX_DATA`, `PINMUX_SINGLE`, `PINMUX_IPSR_NOFN`, `PINMUX_CFG_REG`, `PINMUX_CFG_REG_VAR`, `SH_PFC_PIN_GROUP`, `SH_PFC_FUNCTION`, and bus-data group helpers. It integrates with `core.c`, `pinctrl.c`, and the Kconfig/Makefile entries for `PINCTRL_PFC_EMEV2`.

## Risks And Review Notes
- This is dense hand-maintained SoC metadata. A wrong pin number, mark, enum selector, or register bit can route a peripheral to the wrong pad.
- Some no-GPIO LCD pins are represented by synthetic `PIN_NOGP` entries and mixed into LCD/YUV/TP33 groups. Group definitions must preserve the intended order and mux correspondence.
- `pinmux_data[]` contains multi-step mappings for alternate functions that combine GPSR function selection with CHG_PINSEL selector values. Missing either side causes partial mux programming.
- Register descriptions use both fixed-width and variable-width fields. The common DEBUG validator can catch some enum/register conflicts but not board-level electrical mistakes.
- EMEV2 selects `PINCTRL_SH_PFC` but not GPIO support in Kconfig, so consumers expecting GPIO chips from this table would be disappointed unless configuration changes add data-register support.

## Test Signals
Build with `CONFIG_PINCTRL_PFC_EMEV2` and, preferably, `DEBUG` to run the common PFC table checker. Boot on an EMEV2 DT with `renesas,pfc-emev2` and inspect pinctrl debugfs for the expected groups/functions. Hardware validation should apply representative states for LCD/YUV, SDIO, IIC, UART, external bus/CF, USI, and camera paths and confirm both GPSR and CHG_PINSEL fields.
