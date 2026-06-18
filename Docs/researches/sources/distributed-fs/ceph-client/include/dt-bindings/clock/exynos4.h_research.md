# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos4.h

## Purpose
`exynos4.h` defines the device-tree clock binding ABI for Samsung Exynos4 CMU clock ids for oscillator, PLL, bus, display, camera, multimedia, filesystem, peripheral, and gate domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS_4_H`. The binding surface has 248 exported non-guard macros; macro families include CLK_SCLK (55), CLK_ISP (30), CLK_MOUT (18), CLK_SMMU (15), CLK_DIV (8), CLK_OUT (5), CLK_FOUT (4), CLK_HDMI (2). Representative ids include `CLK_XXTI`, `CLK_XUSBXTI`, `CLK_FIN_PLL`, `CLK_FOUT_APLL`, `CLK_FOUT_MPLL`, `CLK_FOUT_EPLL`, `CLK_FOUT_VPLL`, `CLK_SCLK_APLL`, .... explicit numeric ids span 1..461 across 218 constants. Function-like helpers: none. Expression/string-style macros to review include `CLK_MOUT_MPLL_USER_T`, `CLK_MOUT_MPLL_USER_C`, `CLK_SCLK_MDNIE0`, `CLK_SCLK_SATA`, `CLK_SCLK_FIMD1`, `CLK_SCLK_MIPI1`, `CLK_SCLK_MIPIHSI`, `CLK_SCLK_PWM_ISP`. File section comments identify domains such as `core clocks`, `Exynos4x12 only`, `gate for special clocks (sclk)`, `Exynos4412 only`, `Exynos4210 only`, `gate clocks`, `mux clocks`, `gate clocks - ppmu`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_XXTI`, `CLK_ISP_FIMC_ISP` share `1`; `CLK_XUSBXTI`, `CLK_ISP_FIMC_DRC` share `2`; `CLK_FIN_PLL`, `CLK_ISP_FIMC_FD` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
