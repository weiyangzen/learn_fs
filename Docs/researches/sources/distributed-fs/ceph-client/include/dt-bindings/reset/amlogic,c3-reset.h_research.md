# sources/distributed-fs/ceph-client/include/dt-bindings/reset/amlogic,c3-reset.h

Purpose: `amlogic,c3-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 76 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_BRG (11), RESET_CVE (7), RESET_PWM (7),
RESET_ISP (6), RESET_UART (6), RESET_I2C (5), RESET_VC9000E (3), RESET_SD (3), RESET_MIPI (2),
RESET_DOS (2). Representative constants are `RESET_USBCTRL`, `RESET_USBPHY20`, `RESET_USB2DRD`,
`RESET_MIPI_DSI_HOST`, `RESET_MIPI_DSI_PHY`, `RESET_GE2D`, `RESET_DWAP`, `RESET_AUDIO`, `...`,
`RESET_BRG_NIC_VAPB`, `RESET_BRG_NIC_SDIO_B`, `RESET_BRG_NIC_SDIO_A`, `RESET_BRG_NIC_EMMC`,
`RESET_BRG_NIC_DSU`, `RESET_BRG_NIC_SYSCLK`, `RESET_BRG_NIC_MAIN`, `RESET_BRG_NIC_ALL`. Function-
like helpers are none. Value shape: literal numeric range 4..191 across 76 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_AMLOGIC_C3_RESET_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`RESET0`, `0-3`, `5-7`, `13-20`, `23-31`, `RESET1`, `33-34`, `39-46`, `54-63`, `RESET2`, `68-72`,
`76-79`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 119 lines long. Notable source comments include `RESET0`, `0-3`, `5-7`, `9`, `13-20`,
`23-31`. Example value clusters are RESET_BRG: `RESET_BRG_NIC_NNA=173`,
`RESET_BRG_MUX_NIC_MAIN=174`, `RESET_BRG_AO_NIC_ALL=175`, `RESET_BRG_NIC_VAPB=184`; RESET_CVE:
`RESET_CVE_NIC_GPV=104`, `RESET_CVE_NIC_MAIN=105`, `RESET_CVE_NIC_GE2D=106`, `RESET_CVE_NIC_DW=106`;
RESET_PWM: `RESET_PWM_AB=129`, `RESET_PWM_CD=130`, `RESET_PWM_EF=131`, `RESET_PWM_GH=132`;
RESET_ISP: `RESET_ISP=49`, `RESET_ISP_NIC_GPV=96`, `RESET_ISP_NIC_MAIN=97`, `RESET_ISP_NIC_VCLK=98`;
RESET_UART: `RESET_UART_A=138`, `RESET_UART_B=139`, `RESET_UART_C=140`, `RESET_UART_D=141`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_USBCTRL`,
`RESET_USBPHY20`, `RESET_USB2DRD`, `RESET_MIPI_DSI_HOST`, `RESET_MIPI_DSI_PHY`, `RESET_GE2D`,
`RESET_DWAP`, `RESET_AUDIO`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
