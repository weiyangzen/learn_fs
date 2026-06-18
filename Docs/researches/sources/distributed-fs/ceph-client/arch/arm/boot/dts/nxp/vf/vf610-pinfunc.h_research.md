# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/vf/vf610-pinfunc.h

Purpose: this binding header defines Vybrid VF610 pin-function IDs for device-tree pinctrl groups.

Important API surface: it defines `ALT0` through `ALT7` and 831 `VF610_PAD_*` macros. The documented tuple shape is `<mux_reg input_reg mux_mode input_val>`. Pad banks include PTA, PTB, PTC, PTD, PTE, and DDR pads. Function coverage includes GPIO, RMII/ENET, DCU display, LCD, VIU, UART, I2C, DSPI, QSPI, SAI/ESAI, FTM timers, CAN, USB control pins, NAND/FB, SRC boot straps, debug outputs, watchdog/NMI, and DDR signals.

Control flow: no runtime code. DTS preprocessing converts symbolic pin names into tuples; the VF610/NXP pinctrl implementation programs mux and input-select registers while applying pinctrl states.

State and persistence: constants only. The generated DTB stores mux tuples that persist as board hardware configuration at boot and during pinctrl state switches.

Dependencies and integration: integrated with VF610 board DTS files, `CONFIG_SOC_VF610` DTB builds, and the pinctrl driver parser that recognizes `ALT*` mux modes and input daisy values.

Risks and test signals: risks include inconsistent macro naming, wrong input register for shared signals, and DDR pad changes that may affect early hardware assumptions. Test `make dtbs` for VF610 boards, then hardware smoke-test UART console, Ethernet, display, storage, and I2C/SPI pins.
