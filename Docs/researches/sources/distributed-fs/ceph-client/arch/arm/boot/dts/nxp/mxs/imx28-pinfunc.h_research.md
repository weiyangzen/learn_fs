# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/mxs/imx28-pinfunc.h

Purpose: this header provides i.MX28 pad/function IDs for MXS device-tree pinctrl bindings and includes the shared `mxs-pinfunc.h` electrical constants.

Important API surface: it exports 486 `MX28_PAD_*__*` macros. Covered pad groups include GPMI, LCD, SSP0 through SSP3, AUART0 through AUART3, PWM, SAIF, I2C0, SPDIF, ENET0/ENET clock, JTAG, and EMI address/data/control pins. GPIO alternatives cover GPIO banks 0 through 4. The values are compact MXS encodings such as `0x0000`, `0x0001`, and `0x0003`, with low bits indicating mux selection.

Control flow: no executable control flow. The header participates in C-preprocessed DTS compilation; the pinctrl driver later decodes the numeric values.

State and persistence: no mutable state. The constants form a stable DT binding contract for generated DTBs and board hardware routing.

Dependencies and integration: depends on the MXS pinctrl binding, the shared MXS electrical property constants, and the i.MX28 board DTS files selected by the `nxp/mxs/Makefile`.

Risks and test signals: risks include wrong mux value for Ethernet/SAIF/SSP alternatives, confusing similarly named `ENET0` and `ENET1` timestamp functions, and GPIO bank numbering mistakes. Test all i.MX28 DTBs and run hardware smoke tests for Ethernet, LCD, NAND, UART, and storage on representative boards.
