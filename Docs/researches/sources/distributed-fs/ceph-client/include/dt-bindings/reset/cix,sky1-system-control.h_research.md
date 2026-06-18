# sources/distributed-fs/ceph-client/include/dt-bindings/reset/cix,sky1-system-control.h

Purpose: `cix,sky1-system-control.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 29 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are SW_I3C0 (3), SW_I3C1 (3), SW_UART0 (2), SW_UART1
(2), SW_UART2 (2), SW_UART3 (2), SW_XSPI (2), SW_TIMER (1), SW_DMA (1), SW_SPI0 (1). Representative
constants are `SW_I3C0_RST_FUNC_G_N`, `SW_I3C0_RST_FUNC_I_N`, `SW_I3C1_RST_FUNC_G_N`,
`SW_I3C1_RST_FUNC_I_N`, `SW_UART0_RST_FUNC_N`, `SW_UART1_RST_FUNC_N`, `SW_UART2_RST_FUNC_N`,
`SW_UART3_RST_FUNC_N`, `...`, `SW_I2C3_RST_APB_N`, `SW_I2C4_RST_APB_N`, `SW_I2C5_RST_APB_N`,
`SW_I2C6_RST_APB_N`, `SW_I2C7_RST_APB_N`, `SW_GPIO_RST_APB_N`, `SW_XSPI_REG_RST_N`,
`SW_XSPI_SYS_RST_N`. Function-like helpers are none. Value shape: literal numeric range 0..28 across
29 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_CIX_SKY1_SYSTEM_CONTROL_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `func reset for sky1 fch`, `apb reset for sky1 fch`, `fch rst for xspi`, which is the
intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 41 lines long. Notable source comments include `func reset for sky1 fch`, `apb reset for
sky1 fch`, `fch rst for xspi`. Example value clusters are SW_I3C0: `SW_I3C0_RST_FUNC_G_N=0`,
`SW_I3C0_RST_FUNC_I_N=1`, `SW_I3C0_RST_APB_N=9`; SW_I3C1: `SW_I3C1_RST_FUNC_G_N=2`,
`SW_I3C1_RST_FUNC_I_N=3`, `SW_I3C1_RST_APB_N=10`; SW_UART0: `SW_UART0_RST_FUNC_N=4`,
`SW_UART0_RST_APB_N=12`; SW_UART1: `SW_UART1_RST_FUNC_N=5`, `SW_UART1_RST_APB_N=13`; SW_UART2:
`SW_UART2_RST_FUNC_N=6`, `SW_UART2_RST_APB_N=14`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `SW_I3C0_RST_FUNC_G_N`,
`SW_I3C0_RST_FUNC_I_N`, `SW_I3C1_RST_FUNC_G_N`, `SW_I3C1_RST_FUNC_I_N`, `SW_UART0_RST_FUNC_N`,
`SW_UART1_RST_FUNC_N`, `SW_UART2_RST_FUNC_N`, `SW_UART3_RST_FUNC_N`. Test signals include DTS
compile checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization
after module or runtime-PM cycles.
