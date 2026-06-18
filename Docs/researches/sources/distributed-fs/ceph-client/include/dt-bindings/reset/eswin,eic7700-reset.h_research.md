# sources/distributed-fs/ceph-client/include/dt-bindings/reset/eswin,eic7700-reset.h

Purpose: `eswin,eic7700-reset.h` is a Devicetree binding header for a reset-controller provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 281 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are EIC7700 (281). Representative constants are
`EIC7700_RESET_NOC_NSP`, `EIC7700_RESET_NOC_CFG`, `EIC7700_RESET_RNOC_NSP`,
`EIC7700_RESET_SNOC_TCU`, `EIC7700_RESET_SNOC_U84`, `EIC7700_RESET_SNOC_PCIE_XSR`,
`EIC7700_RESET_SNOC_PCIE_XMR`, `EIC7700_RESET_SNOC_PCIE_PR`, `...`, `EIC7700_RESET_CNOC_D2D_CFG`,
`EIC7700_RESET_CNOC_CFG`, `EIC7700_RESET_CNOC_CLMM_CFG`, `EIC7700_RESET_CNOC_AON_CFG`,
`EIC7700_RESET_LNOC_CFG`, `EIC7700_RESET_LNOC_NPU_LLC`, `EIC7700_RESET_LNOC_DDRC1_P0`,
`EIC7700_RESET_LNOC_DDRC0_P0`. Function-like helpers are none. Value shape: literal numeric range
0..280 across 281 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_ESWIN_EIC7700_RESET_H__`; after preprocessing, DTS C-preprocessor users and C drivers see only
the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`EIC7700 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 298 lines long. Notable source comments include `All rights reserved. Device Tree
binding constants for EIC7700 reset controller. Authors: Yifeng Huang
<huangyifeng@eswincomputing.com> Xuyang Dong <dongxuyang@eswincomputing.com>`,
`__DT_ESWIN_EIC7700_RESET_H__`. Example value clusters are EIC7700: `EIC7700_RESET_NOC_NSP=0`,
`EIC7700_RESET_NOC_CFG=1`, `EIC7700_RESET_RNOC_NSP=2`, `EIC7700_RESET_SNOC_TCU=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`EIC7700_RESET_NOC_NSP`, `EIC7700_RESET_NOC_CFG`, `EIC7700_RESET_RNOC_NSP`,
`EIC7700_RESET_SNOC_TCU`, `EIC7700_RESET_SNOC_U84`, `EIC7700_RESET_SNOC_PCIE_XSR`,
`EIC7700_RESET_SNOC_PCIE_XMR`, `EIC7700_RESET_SNOC_PCIE_PR`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
