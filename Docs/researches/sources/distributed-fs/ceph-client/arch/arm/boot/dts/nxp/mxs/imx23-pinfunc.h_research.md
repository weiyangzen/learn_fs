# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx23-pinfunc.h

Purpose: this MXS pinctrl binding header defines i.MX23 pad/function constants for DTS pin groups. It includes `mxs-pinfunc.h` for shared electrical configuration constants.

Important API surface: it exports 313 `MX23_PAD_*__*` macros. The packed numeric values use the MXS pad encoding where the high nibbles identify bank/pin position and the low bits encode mux function. Banks/functions include GPMI NAND, LCD, SSP1/SSP2, EMI, AUART, I2C, PWM, rotary, ETM/JTAG, SAIF, SPDIF, and GPIO aliases. GPIO alternatives cover GPIO banks 0 through 2.

Control flow: no runtime logic exists. DTS preprocessing replaces readable pad names with packed constants that the MXS pinctrl driver decodes.

State and persistence: constants are immutable source data. Once built into DTBs, they persist as the hardware pad selection for board pinctrl states.

Dependencies and integration: depends on `mxs-pinfunc.h` for `MXS_DRIVE_*`, `MXS_VOLTAGE_*`, and `MXS_PULL_*` values used alongside the function IDs. Board DTS files combine these function constants with electrical properties in MXS pinctrl nodes.

Risks and test signals: errors in the packed low mux value can select a valid but wrong alternate function. The dense GPIO alias section also risks bank/pin mismatch. Test by compiling all i.MX23 DTBs and validating boot-time pinctrl, especially NAND, LCD, UART, I2C, and MMC-style SSP pins.
