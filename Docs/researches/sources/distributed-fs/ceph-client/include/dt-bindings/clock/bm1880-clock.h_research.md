# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bm1880-clock.h

## Purpose
`bm1880-clock.h` defines the device-tree clock binding ABI for Bitmain BM1880 clock ids for PLL roots, CPU, memory, storage, Ethernet, GPIO, video, TPU, JPEG, AXI/APB, and UART trees. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BM1880_H`. The binding surface has 70 exported non-guard macros; macro families include BM1880_CLK_APB (14), BM1880_CLK_DIV (8), BM1880_CLK_AXI5 (4), BM1880_CLK_AXI4 (4), BM1880_CLK_AXI1 (3), BM1880_CLK_AHB (2), BM1880_CLK_100K (2), BM1880_CLK_500M (2). Representative ids include `BM1880_CLK_OSC`, `BM1880_CLK_MPLL`, `BM1880_CLK_SPLL`, `BM1880_CLK_FPLL`, `BM1880_CLK_DDRPLL`, `BM1880_CLK_A53`, `BM1880_CLK_50M_A53`, `BM1880_CLK_AHB_ROM`, .... explicit numeric ids span 0..69 across 70 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with the matching platform clock provider, Linux common-clock registration tables, and DTS consumers that use these numeric ids. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
