# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-pericfg.h

Purpose: `mediatek,mt6735-pericfg.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (23). Representative constants are
`MT6735_PERI_RST0_UART0`, `MT6735_PERI_RST0_UART1`, `MT6735_PERI_RST0_UART2`,
`MT6735_PERI_RST0_UART3`, `MT6735_PERI_RST0_UART4`, `MT6735_PERI_RST0_BTIF`,
`MT6735_PERI_RST0_DISP_PWM_PERI`, `MT6735_PERI_RST0_PWM`, `...`, `MT6735_PERI_RST0_MSDC0`,
`MT6735_PERI_RST0_MSDC1`, `MT6735_PERI_RST0_I2C0`, `MT6735_PERI_RST0_I2C1`, `MT6735_PERI_RST0_I2C2`,
`MT6735_PERI_RST0_I2C3`, `MT6735_PERI_RST0_USB`, `MT6735_PERI_RST1_SPI0`. Function-like helpers are
none. Value shape: literal numeric range 0..22 across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MT6735_PERICFG_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 31 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_PERI_RST0_UART0=0`, `MT6735_PERI_RST0_UART1=1`, `MT6735_PERI_RST0_UART2=2`,
`MT6735_PERI_RST0_UART3=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6735_PERI_RST0_UART0`, `MT6735_PERI_RST0_UART1`, `MT6735_PERI_RST0_UART2`,
`MT6735_PERI_RST0_UART3`, `MT6735_PERI_RST0_UART4`, `MT6735_PERI_RST0_BTIF`,
`MT6735_PERI_RST0_DISP_PWM_PERI`, `MT6735_PERI_RST0_PWM`. Test signals include DTS compile checks,
reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
