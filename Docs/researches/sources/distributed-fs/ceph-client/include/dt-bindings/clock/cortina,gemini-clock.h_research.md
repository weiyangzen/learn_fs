# sources/distributed-fs/ceph-client/include/dt-bindings/clock/cortina,gemini-clock.h

## Purpose
`cortina,gemini-clock.h` defines the device-tree clock binding ABI for Cortina Gemini base clocks and gate ids for AHB/APB/CPU, PCI, TVC, UART, GMAC, SATA, USB, IDE, DDR, flash, and boot gates. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_CORTINA_GEMINI_CLOCK_H`. The binding surface has 22 exported non-guard macros; macro families include GEMINI_CLK_GATE (13), GEMINI_NUM_CLKS (1), GEMINI_CLK_RTC (1), GEMINI_CLK_AHB (1), GEMINI_CLK_APB (1), GEMINI_CLK_CPU (1), GEMINI_CLK_PCI (1), GEMINI_CLK_TVC (1). Representative ids include `GEMINI_NUM_CLKS`, `GEMINI_CLK_RTC`, `GEMINI_CLK_AHB`, `GEMINI_CLK_APB`, `GEMINI_CLK_CPU`, `GEMINI_CLK_PCI`, `GEMINI_CLK_TVC`, `GEMINI_CLK_UART`, .... explicit numeric ids span 0..20 across 22 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `RTC, AHB, APB, CPU, PCI, TVC, UART clocks and 13 gates`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `GEMINI_CLK_GATES`, `GEMINI_CLK_GATE_SECURITY` share `7`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with the matching platform clock provider, Linux common-clock registration tables, and DTS consumers that use these numeric ids. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
