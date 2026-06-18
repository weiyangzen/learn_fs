# sources/distributed-fs/ceph-client/include/dt-bindings/reset/imx7-reset.h

Purpose: `imx7-reset.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 27 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are IMX7 (27). Representative constants are
`IMX7_RESET_A7_CORE_POR_RESET0`, `IMX7_RESET_A7_CORE_POR_RESET1`, `IMX7_RESET_A7_CORE_RESET0`,
`IMX7_RESET_A7_CORE_RESET1`, `IMX7_RESET_A7_DBG_RESET0`, `IMX7_RESET_A7_DBG_RESET1`,
`IMX7_RESET_A7_ETM_RESET0`, `IMX7_RESET_A7_ETM_RESET1`, `...`, `IMX7_RESET_MIPI_PHY_SRST`,
`IMX7_RESET_PCIEPHY`, `IMX7_RESET_PCIEPHY_PERST`, `IMX7_RESET_PCIE_CTRL_APPS_EN`,
`IMX7_RESET_DDRC_PRST`, `IMX7_RESET_DDRC_CORE_RST`, `IMX7_RESET_PCIE_CTRL_APPS_TURNOFF`,
`IMX7_RESET_NUM`. Function-like helpers are none. Value shape: literal numeric range 0..26 across 27
macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDING_RESET_IMX7_H`; after preprocessing, DTS C-preprocessor users and C drivers see only the
constants and any packing helpers. Comment-delimited groups or observed macro clusters are `IMX7
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 53 lines long. Notable source comments include `IMX7_RESET_PCIEPHY is a logical reset
line combining PCIEPHY_BTN and PCIEPHY_G_RST`, `IMX7_RESET_PCIE_CTRL_APPS_EN is not strictly a reset
line, but it can be used to inhibit PCIe LTTSM, so, in a way, it can be thoguht of as one`. Example
value clusters are IMX7: `IMX7_RESET_A7_CORE_POR_RESET0=0`, `IMX7_RESET_A7_CORE_POR_RESET1=1`,
`IMX7_RESET_A7_CORE_RESET0=2`, `IMX7_RESET_A7_CORE_RESET1=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`IMX7_RESET_A7_CORE_POR_RESET0`, `IMX7_RESET_A7_CORE_POR_RESET1`, `IMX7_RESET_A7_CORE_RESET0`,
`IMX7_RESET_A7_CORE_RESET1`, `IMX7_RESET_A7_DBG_RESET0`, `IMX7_RESET_A7_DBG_RESET1`,
`IMX7_RESET_A7_ETM_RESET0`, `IMX7_RESET_A7_ETM_RESET1`. Test signals include DTS compile checks,
reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
