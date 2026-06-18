# sources/distributed-fs/ceph-client/include/dt-bindings/reset/airoha,en7581-reset.h

Purpose: `airoha,en7581-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 53 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EN7581 (53). Representative constants are
`EN7581_XPON_PHY_RST`, `EN7581_CPU_TIMER2_RST`, `EN7581_HSUART_RST`, `EN7581_UART4_RST`,
`EN7581_UART5_RST`, `EN7581_I2C2_RST`, `EN7581_XSI_MAC_RST`, `EN7581_XSI_PHY_RST`, `...`,
`EN7581_USB_HOST_P0_RST`, `EN7581_GSW_RST`, `EN7581_SFC2_PCM_RST`, `EN7581_PCIE0_RST`,
`EN7581_PCIE1_RST`, `EN7581_CPU_TIMER_RST`, `EN7581_PCIE_HB_RST`, `EN7581_XPON_MAC_RST`. Function-
like helpers are none. Value shape: literal numeric range 0..52 across 53 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_RESET_CONTROLLER_AIROHA_EN7581_H_`; after preprocessing, DTS C-preprocessor users and
C drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RST_CTRL2`, `RST_CTRL1`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 66 lines long. Notable source comments include `RST_CTRL2`, `RST_CTRL1`,
`__DT_BINDINGS_RESET_CONTROLLER_AIROHA_EN7581_H_`. Example value clusters are EN7581:
`EN7581_XPON_PHY_RST=0`, `EN7581_CPU_TIMER2_RST=1`, `EN7581_HSUART_RST=2`, `EN7581_UART4_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `EN7581_XPON_PHY_RST`,
`EN7581_CPU_TIMER2_RST`, `EN7581_HSUART_RST`, `EN7581_UART4_RST`, `EN7581_UART5_RST`,
`EN7581_I2C2_RST`, `EN7581_XSI_MAC_RST`, `EN7581_XSI_PHY_RST`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
