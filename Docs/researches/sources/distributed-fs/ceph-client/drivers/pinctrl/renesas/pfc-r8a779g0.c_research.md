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
