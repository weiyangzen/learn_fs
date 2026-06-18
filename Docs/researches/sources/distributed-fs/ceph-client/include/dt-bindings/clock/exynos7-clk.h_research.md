# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos7-clk.h

## Purpose
`exynos7-clk.h` defines the device-tree clock binding ABI for Samsung Exynos7 clock ids grouped by top/core/peripheral/audio/display/filesystem/MSCL domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS7_H`. The binding surface has 172 exported non-guard macros; macro families include CLK_SCLK (18), DOUT_SCLK (11), DOUT_ACLK (7), CLK_ACLK (4), ACLK_QE (4), PCLK_QE (4), ACLK_MSCL (3), SCLK_MFC (2). Representative ids include `DOUT_ACLK_PERIS`, `DOUT_SCLK_BUS0_PLL`, `DOUT_SCLK_BUS1_PLL`, `DOUT_SCLK_CC_PLL`, `DOUT_SCLK_MFC_PLL`, `DOUT_ACLK_CCORE_133`, `DOUT_ACLK_MSCL_532`, `ACLK_MSCL_532`, .... explicit numeric ids span 1..33 across 172 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `TOPC`, `TOP0`, `TOP1`, `CCORE`, `PERIC0`, `PERIC1`, `PERIS`, `FSYS0`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `DOUT_ACLK_PERIS`, `DOUT_ACLK_PERIC1`, `DOUT_ACLK_FSYS1_200`, `PCLK_RTC` share `1`; `DOUT_SCLK_BUS0_PLL`, `DOUT_ACLK_PERIC0`, `DOUT_ACLK_FSYS0_200`, `CCORE_NR_CLK` share `2`; `DOUT_SCLK_BUS1_PLL`, `CLK_SCLK_UART0`, `DOUT_SCLK_MMC2`, `PCLK_HSI2C0` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
