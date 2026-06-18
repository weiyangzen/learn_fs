# sources/distributed-fs/ceph-client/include/dt-bindings/clock/fsd-clk.h

## Purpose
`fsd-clk.h` defines the device-tree clock binding ABI for Samsung FSD clock ids for CMU, CPU cluster, PERIC, FSYS0/1, IMEM, MFC, and CAM_CSI domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_FSD_H`. The binding surface has 127 exported non-guard macros; macro families include DOUT_CMU (13), PERIC_EQOS_TOP (5), FSYS0_EQOS_TOP0 (5), PCIE_SUBCTRL_INST0 (4), PCIE_LINK0_IPCLKPORT (4), PCIE_LINK1_IPCLKPORT (4), PERIC_MCAN0_IPCLKPORT (2), PERIC_MCAN1_IPCLKPORT (2). Representative ids include `DOUT_CMU_PLL_SHARED0_DIV4`, `DOUT_CMU_PERIC_SHARED1DIV36`, `DOUT_CMU_PERIC_SHARED0DIV3_TBUCLK`, `DOUT_CMU_PERIC_SHARED0DIV20`, `DOUT_CMU_PERIC_SHARED1DIV4_DMACLK`, `DOUT_CMU_PLL_SHARED0_DIV6`, `DOUT_CMU_FSYS0_SHARED1DIV4`, `DOUT_CMU_FSYS0_SHARED0DIV4`, .... explicit numeric ids span 1..45 across 127 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `CMU`, `PERIC`, `FSYS0`, `FSYS1`, `IMEM`, `MFC`, `CAM_CSI`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `DOUT_CMU_PLL_SHARED0_DIV4`, `PERIC_SCLK_UART0`, `UFS0_MPHY_REFCLK_IXTAL24`, `PCIE_LINK0_IPCLKPORT_DBI_ACLK` share `1`; `DOUT_CMU_PERIC_SHARED1DIV36`, `PERIC_PCLK_UART0`, `UFS0_MPHY_REFCLK_IXTAL26`, `PCIE_LINK0_IPCLKPORT_AUX_ACLK` share `2`; `DOUT_CMU_PERIC_SHARED0DIV3_TBUCLK`, `PERIC_SCLK_UART1`, `UFS1_MPHY_REFCLK_IXTAL24`, `PCIE_LINK0_IPCLKPORT_MSTR_ACLK` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
