# Research: subset-b-005103

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779f0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779f0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779g0.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779g0.c

## Purpose
This file is the Renesas R-Car V4H / R8A779G0 SoC pin function controller description consumed by the common SuperH/R-Car PFC driver. It exports `r8a779g0_pinmux_info`, which describes a much larger pin surface than R8A779F0: GPIO banks 0 through 8, non-GPIO VDDQ voltage-domain pins for AVB/TSN, mux functions for serial, storage, Ethernet, CAN-FD, PWM, TPU, audio, and QSPI/RPC, plus register tables for mux, drive, pull, and POC voltage control.

The file is declarative apart from one SoC callback. Its job is to encode the datasheet's pin tables into the generic Renesas pinctrl format so device-tree pinctrl states can ask for stable group/function names instead of raw PFC register writes.

## Important APIs, Types, And Functions
`const struct sh_pfc_soc_info r8a779g0_pinmux_info` is the exported integration object. It references all static pin, group, function, mux, drive, bias, and IO-control tables and installs `r8a779g0_pin_ops`.

`CPU_ALL_GP()` declares GPIO banks 0-8 with per-bank configuration flags. Banks 0, 1, 3, and 8 support 1.8/3.3 V IO voltage selection, while the AVB/TSN voltage domains are represented by non-GPIO pins from `CPU_ALL_NOGP()` with 1.8/2.5 V voltage configuration flags. `pinmux_pins[]` includes both `PINMUX_GPIO_GP_ALL()` and `PINMUX_NOGP_ALL()`, unlike the smaller R8A779F0 file.

The macro-generated mux layers are `GPSR0` through `GPSR8`, many `IP*SR*` field macros, and `MOD_SEL8_*` module-select bits. `pinmux_data[]` binds each mark to its GPSR/IPSR choice and, for I2C-capable bank-8 pins, to the appropriate MOD_SEL8 selector. The visible group/function surface includes audio clock, AVB0/1/2, CANFD0-7 and CAN clock, HSCIF0-3 with A/B alternates on some channels, I2C0-5, external IRQ A/B groups, MMC, MSIOF0-5, PCIe clock request, PWM0-9, QSPI0/1, SCIF0/1/3/4, SCIF clock and SCIF clock2, SSI, TPU outputs, and TSN0.

`r8a779g0_pin_to_pocctrl()` maps supported pins to POC registers. It handles banks 0, 1 up to pin 22, bank 3 up to pin 12, bank 8, and the non-GPIO `PIN_VDDQ_TSN0`, `PIN_VDDQ_AVB2`, `PIN_VDDQ_AVB1`, and `PIN_VDDQ_AVB0` pins. Unsupported pins return `-EINVAL`.

## Control Flow
The runtime flow is inherited from the generic Renesas PFC core. During SoC probe, the common driver selects `r8a779g0_pinmux_info`, registers all pinctrl groups/functions, and exposes generic pinconf capabilities based on the pin flags and register tables. Function selection resolves from a group name to an array of physical pins and mark IDs, then the PFC core writes GPSR and IPSR fields; I2C pin selections also program MOD_SEL8 bits.

Peripheral grouping is deliberately split to match common board usage. Ethernet blocks have sideband groups such as link, magic, phy interrupt, MDIO, RGMII, reference clock, and AVTP timestamp signals. Storage blocks expose MMC data bus widths and QSPI data2/data4 bus widths. Serial blocks separate data, clock, and hardware-flow-control groups. Several functions expose alternate routes, such as CANFD5 A/B, HSCIF1 A/B, HSCIF3 A/B, SCIF1 A/B, SCIF3 A/B, PWM1 A/B, PWM3 A/B, TPU A/B, and external IRQ A/B.

Pin configuration requests take a parallel path. Drive strength uses `pinmux_drive_regs[]`, where most pins have 3-bit drive fields and QSPI/RPC pins use 2-bit fields. Pull configuration uses `pinmux_bias_regs[]` with PUEN/PUD register pairs for each bank. IO-voltage requests call the POCCTRL callback and then the common R-Car PFC code writes the relevant POC register.

## State And Persistence
There is no mutable file-local state. All software state is static table data, and all runtime persistence is in the PFC hardware registers. GPSR/IPSR/MOD_SEL8 hold mux state, DRV registers hold drive strength, PUEN/PUD hold pull enable and pull direction, and POC registers hold voltage-domain selection. The file has no suspend/resume hooks; any save/restore behavior belongs to the common pinctrl driver or platform firmware.

The POC mapping intentionally does not cover every GPIO bank. AVB/TSN voltage selection is represented through non-GPIO VDDQ pins rather than each AVB/TSN signal pin, so consumers must request voltage configuration on those domain pins rather than expecting POC support on all bank 4-7 pins.

## Dependencies And Integration Points
The file depends on `sh_pfc.h` for macro expansion and shared table types, and on common R-Car helpers `rcar_pinmux_get_bias()` and `rcar_pinmux_set_bias()`. It integrates with the Renesas pinctrl/PFC core through `r8a779g0_pinmux_info.name = "r8a779g0_pfc"` and `unlock_reg = 0x1ff`.

External integration is through device-tree pinctrl states that reference group and function names. Network drivers consume AVB0/1/2 and TSN0 groups, CAN drivers consume CANFD group names and `can_clk`, serial drivers use HSCIF/SCIF/MSIOF groups, storage drivers use MMC/QSPI/RPC-related groups, and board control logic may use PCIe clock request, audio clock/SSI, PWM, TPU, AVS, or IRQ groups.

## Risks And Test Signals
The highest risk is register-table drift from the hardware manual. This file has many more bank offsets than R8A779F0, including address ranges under both `0xE605` and `0xE606`; a wrong base, bit position, field width, or group order can produce valid-looking pinctrl states that program the wrong pad. Alternate-route groups are another risk because A/B variants often share function names but use different banks and IPSR values. The non-GPIO VDDQ pins are important for voltage control and can be missed by tests that only enumerate GPIO-backed pins.

Useful test signals include successful probe and pinctrl debugfs enumeration of GPIO and non-GPIO pins, group/function counts matching expectations, mux tests for every A/B alternate route, MOD_SEL8 verification for I2C0-5 versus bank-8 alternate serial usage, RGMII group selection for AVB0/1/2 and TSN0, CANFD0-7 plus CAN clock selection, MMC data1/data4/data8 and QSPI data2/data4 selection, bias get/set across PUEN0-PUEN8, drive-strength get/set on 2-bit QSPI/RPC and 3-bit Ethernet/CAN/serial pins, POC voltage operations on banks 0/1/3/8 and VDDQ_* pins, and expected `-EINVAL` for unsupported POC pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-r8a779g0.c -->
