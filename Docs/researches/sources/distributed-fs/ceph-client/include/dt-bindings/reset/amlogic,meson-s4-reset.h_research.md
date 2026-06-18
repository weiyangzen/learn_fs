# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,meson-s4-reset.h

Purpose: `amlogic,meson-s4-reset.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 81 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_BRG (16), RESET_I2C (6), RESET_PWM (5),
RESET_UART (5), RESET_USB (4), RESET_VID (2), RESET_MALI (2), RESET_DDR (2), RESET_DOS (2),
RESET_TEMPSENSOR (2). Representative constants are `RESET_USB_DDR0`, `RESET_USB_DDR1`,
`RESET_USB_DDR2`, `RESET_USB_DDR3`, `RESET_USBCTRL`, `RESET_USBPHY20`, `RESET_USBPHY21`,
`RESET_HDMITX_APB`, `...`, `RESET_BRG_HEVCF_PIPL1`, `RESET_BRG_HEVCB_PIPL1`, `RESET_RAMA`,
`RESET_BRG_NIC_VAPB`, `RESET_BRG_NIC_DSU`, `RESET_BRG_NIC_SYSCLK`, `RESET_BRG_NIC_MAIN`,
`RESET_BRG_NIC_ALL`. Function-like helpers are none. Value shape: literal numeric range 0..191
across 81 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_MESON_S4_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `RESET0`, `5-7`, `10-15`, `RESET1`, `39-47`, `49-51`, `53-63`, `RESET2`, `68-71`, `76-79`,
`83-87`, `92-95`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 125 lines long. Notable source comments include `RESET0`, `5-7`, `10-15`, `RESET1`,
`39-47`, `49-51`. Example value clusters are RESET_BRG: `RESET_BRG_VCBUS_DEC=17`,
`RESET_BRG_VDEC_PIPL0=160`, `RESET_BRG_HEVCF_PIPL0=161`, `RESET_BRG_HCODEC_PIPL0=163`; RESET_I2C:
`RESET_I2C_S_A=144`, `RESET_I2C_M_A=145`, `RESET_I2C_M_B=146`, `RESET_I2C_M_C=147`; RESET_PWM:
`RESET_PWM_AB=132`, `RESET_PWM_CD=133`, `RESET_PWM_EF=134`, `RESET_PWM_GH=135`; RESET_UART:
`RESET_UART_A=138`, `RESET_UART_B=139`, `RESET_UART_C=140`, `RESET_UART_D=141`; RESET_USB:
`RESET_USB_DDR0=0`, `RESET_USB_DDR1=1`, `RESET_USB_DDR2=2`, `RESET_USB_DDR3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_USB_DDR0`,
`RESET_USB_DDR1`, `RESET_USB_DDR2`, `RESET_USB_DDR3`, `RESET_USBCTRL`, `RESET_USBPHY20`,
`RESET_USBPHY21`, `RESET_HDMITX_APB`. Test signals include DTS compile checks, reset-controller
probe, driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM
cycles.
