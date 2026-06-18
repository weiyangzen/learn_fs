# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-cygnus.h

## Purpose
`bcm-cygnus.h` defines the device-tree clock binding ABI for Broadcom Cygnus iProc PLL, channel, ASIU, and keypad/ADC/PWM clock ids. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_CLOCK_BCM_CYGNUS_H`. The binding surface has 28 exported non-guard macros; macro families include BCM_CYGNUS_GENPLL (7), BCM_CYGNUS_LCPLL0 (7), BCM_CYGNUS_MIPIPLL (7), BCM_CYGNUS_AUDIOPLL (4), BCM_CYGNUS_ASIU (3). Representative ids include `BCM_CYGNUS_GENPLL`, `BCM_CYGNUS_GENPLL_AXI21_CLK`, `BCM_CYGNUS_GENPLL_250MHZ_CLK`, `BCM_CYGNUS_GENPLL_IHOST_SYS_CLK`, `BCM_CYGNUS_GENPLL_ENET_SW_CLK`, `BCM_CYGNUS_GENPLL_AUDIO_125_CLK`, `BCM_CYGNUS_GENPLL_CAN_CLK`, `BCM_CYGNUS_LCPLL0`, .... explicit numeric ids span 0..6 across 28 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `GENPLL clock ID`, `LCPLL0 clock ID`, `MIPI PLL clock ID`, `ASIU clock ID`, `AUDIO clock ID`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM_CYGNUS_GENPLL`, `BCM_CYGNUS_LCPLL0`, `BCM_CYGNUS_MIPIPLL`, `BCM_CYGNUS_ASIU_KEYPAD_CLK` share `0`; `BCM_CYGNUS_GENPLL_AXI21_CLK`, `BCM_CYGNUS_LCPLL0_PCIE_PHY_REF_CLK`, `BCM_CYGNUS_MIPIPLL_CH0_UNUSED`, `BCM_CYGNUS_ASIU_ADC_CLK` share `1`; `BCM_CYGNUS_GENPLL_250MHZ_CLK`, `BCM_CYGNUS_LCPLL0_DDR_PHY_CLK`, `BCM_CYGNUS_MIPIPLL_CH1_LCD`, `BCM_CYGNUS_ASIU_PWM_CLK` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
