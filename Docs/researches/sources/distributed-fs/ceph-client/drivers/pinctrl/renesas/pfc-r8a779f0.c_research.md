# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779f0.c

## Purpose
This file is the Renesas R-Car S4-8 / R8A779F0 SoC pin function controller description for the shared SuperH/R-Car PFC core. It does not implement a standalone platform driver; instead it exports `r8a779f0_pinmux_info`, a dense `struct sh_pfc_soc_info` table set that lets the generic Renesas pinctrl driver enumerate pins, groups, functions, mux register fields, drive-strength registers, pull-up/down registers, and voltage-domain control.

The hardware surface is compact compared with larger R-Car Gen4 parts: four GPIO banks are described, with bank 0 for serial/MSIOF/IRQ/TSN alternate pins, bank 1 for MMC and I2C-capable pins, bank 2 for RPC/QSPI/PCIe pins, and bank 3 for TSN sideband pins. Two non-GPIO pins are declared by `CPU_ALL_NOGP()` but only GPIO pins are exposed in `pinmux_pins`.

## Important APIs, Types, And Functions
The central exported object is `const struct sh_pfc_soc_info r8a779f0_pinmux_info`. It points at `pinmux_pins`, `pinmux_groups`, `pinmux_functions`, `pinmux_config_regs`, `pinmux_drive_regs`, `pinmux_bias_regs`, `pinmux_ioctrl_regs`, and `pinmux_data`.

`CPU_ALL_GP()` defines the per-port pin inventory and pin configuration flags. Banks 0, 1, and 3 include `SH_PFC_PIN_CFG_IO_VOLTAGE_18_33`; bank 2 has drive and bias only. `CFG_FLAGS` enables drive strength plus pull-up/down support. `CPU_ALL_NOGP()` declares `PRESETOUT0_N` and `EXTALR` as non-GPIO pins with pull configuration metadata.

The `GPSR*`, `IP*SR*`, `MOD_SEL1_*`, `PINMUX_GPSR`, `PINMUX_IPSR`, `PINMUX_MOD_SELS`, and `PINMUX_PHYS` macros are reused under different definitions of `F_()` and `FM()` to generate function IDs, mux marks, and configuration-register value arrays. `pinmux_data[]` ties logical marks to IPSR/GPSR selectors and contains the special I2C handling where GP1_0 through GP1_9 require MOD_SEL1 values that disable the physical I2C function.

`pinmux_groups[]` lists the consumer-visible pin groups. `pinmux_functions[]` maps those groups into pinctrl functions for HSCIF0-3, I2C0-5, external IRQs, MMC, MSIOF0-3, PCIe clock request pins, QSPI0/1, SCIF0/1/3/4, SCIF clock, and TSN0/1/2 sideband groups. `r8a779f0_pin_to_pocctrl()` is the only executable SoC-specific callback; it maps GPIO pins in banks 0, 1, and 3 to POC voltage-control registers and rejects unsupported pins with `-EINVAL`.

## Control Flow
At build time the macro blocks expand into static tables. At runtime the generic Renesas PFC probe path selects `r8a779f0_pinmux_info` from the SoC match table in another file, then uses these tables to register pinctrl groups/functions and pin configuration operations. A consumer selecting a function group is routed by the PFC core through `pinmux_data[]` to one or more GPSR/IPSR/MOD_SEL register writes.

The typical mux flow is: a DT pinctrl state names a function and group; the core finds the `struct sh_pfc_function` and `struct sh_pfc_pin_group`; each group's mux marks are looked up in `pinmux_data[]`; GPSR selects GPIO-versus-function mode; IPSR selects one of the alternate functions for multiplexed pins; MOD_SEL1 selects physical I2C routing for I2C0-5. Drive-strength requests are resolved through `pinmux_drive_regs[]`, bias requests through `pinmux_bias_regs[]`, and IO-voltage requests call `r8a779f0_pin_to_pocctrl()`.

## State And Persistence
The file has no mutable driver-private state, no allocation, and no suspend/resume logic. All state is either static read-only table data or hardware state in PFC registers after the shared core programs them. Mux state persists in GPSR/IPSR/MOD_SEL registers, drive settings persist in DRV registers, pull enable/direction persist in PUEN/PUD registers, and voltage-domain selection persists in POC registers until reset or later kernel/firmware writes.

The POCCTRL callback only supports banks 0, 1, and 3. Bank 2 pins are in the GPIO inventory and bias/drive tables but are not voltage-switchable through this callback, matching the absence of `SH_PFC_PIN_CFG_IO_VOLTAGE_18_33` on bank 2 in `CPU_ALL_GP()`.

## Dependencies And Integration Points
The file depends on `sh_pfc.h` for all table macros and for the shared types (`struct sh_pfc_pin`, `struct sh_pfc_pin_group`, `struct sh_pfc_function`, `struct pinmux_cfg_reg`, `struct pinmux_drive_reg`, `struct pinmux_bias_reg`, `struct pinmux_ioctrl_reg`, and `struct sh_pfc_soc_info`). It also depends on Renesas helper callbacks `rcar_pinmux_get_bias()` and `rcar_pinmux_set_bias()` supplied by the common R-Car PFC code.

Integration points are the Linux pinctrl, pinmux, and pinconf frameworks through the common Renesas PFC driver, plus board device trees that request function/group names such as `mmc_data8`, `qspi0_data4`, `msiof2_rxd`, `i2c5`, or `tsn0_mdio_a`. The exported SoC info name is `r8a779f0_pfc`, and `unlock_reg = 0x1ff` describes the PMMR unlock mask required by the register-write path.

## Risks And Test Signals
Risk is concentrated in table correctness. A wrong GPSR/IPSR mapping can silently select the wrong peripheral, and a wrong group pin order can break bus-style groups such as MMC data widths or QSPI data2/data4. The I2C MOD_SEL1 handling is subtle: using GP1_0 through GP1_9 as GPIO or alternate functions requires specific module-select values, while the physical I2C marks use the alternate MOD_SEL value. The POCCTRL callback must keep its supported banks aligned with the voltage flags in `CPU_ALL_GP()`.

Useful test signals include boot-time PFC probe with `r8a779f0_pfc`, pinctrl debugfs enumeration of all groups/functions, selecting every serial/MSIOF/I2C/MMC/QSPI/TSN function used by board DTs, bias get/set on all PUEN/PUD banks, drive-strength get/set across 2-bit QSPI/RPC pins and 3-bit GPIO pins, IO-voltage get/set rejection for bank 2 and success for banks 0/1/3, and regression checks that `mmc_data1`, `mmc_data4`, `mmc_data8`, `qspi*_data2`, and `qspi*_data4` expose the expected pin counts.
