# sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec9-clk.h

## Purpose
`axis,artpec9-clk.h` defines the device-tree clock binding ABI for Axis ARTPEC-9 CMU clock ids for top, bus, CPU, media, filesystem, GPU, and peripheral domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_ARTPEC9_H`. The binding surface has 165 exported non-guard macros; macro families include CLK_GOUT (76), CLK_DOUT (65), CLK_MOUT (18), CLK_FOUT (6). Representative ids include `CLK_FOUT_SHARED0_PLL`, `CLK_DOUT_SHARED0_DIV2`, `CLK_DOUT_SHARED0_DIV3`, `CLK_DOUT_SHARED0_DIV4`, `CLK_FOUT_SHARED1_PLL`, `CLK_DOUT_SHARED1_DIV2`, `CLK_DOUT_SHARED1_DIV3`, `CLK_DOUT_SHARED1_DIV4`, .... explicit numeric ids span 1..41 across 165 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `CMU_CMU`, `CMU_BUS`, `CMU_CORE`, `CMU_CPUCL`, `CMU_FSYS0`, `CMU_FSYS1`, `CMU_IMEM`, `CMU_PERI`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_FOUT_SHARED0_PLL`, `CLK_MOUT_BUS_ACLK_USER`, `CLK_MOUT_CORE_ACLK_USER`, `CLK_FOUT_CPUCL_PLL0` share `1`; `CLK_DOUT_SHARED0_DIV2`, `CLK_MOUT_CPUCL_PLL0`, `CLK_MOUT_FSYS0_IP_USER`, `CLK_MOUT_FSYS1_SCAN0_USER` share `2`; `CLK_DOUT_SHARED0_DIV3`, `CLK_FOUT_CPUCL_PLL1`, `CLK_MOUT_FSYS0_MAIN_USER`, `CLK_MOUT_FSYS1_SCAN1_USER` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
