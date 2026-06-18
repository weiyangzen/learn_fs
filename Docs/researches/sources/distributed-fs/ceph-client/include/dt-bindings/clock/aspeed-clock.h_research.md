# sources/distributed-fs/ceph-client/include/dt-bindings/clock/aspeed-clock.h

## Purpose
`aspeed-clock.h` defines the device-tree clock binding ABI for legacy Aspeed clock-gate, root-clock, and reset identifiers shared by older BMC device trees and clock/reset drivers. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_ASPEED_CLOCK_H`. The binding surface has 50 exported non-guard macros; macro families include ASPEED_CLK_GATE (24), ASPEED_CLK (14), ASPEED_RESET (12). Representative ids include `ASPEED_CLK_GATE_ECLK`, `ASPEED_CLK_GATE_GCLK`, `ASPEED_CLK_GATE_MCLK`, `ASPEED_CLK_GATE_VCLK`, `ASPEED_CLK_GATE_BCLK`, `ASPEED_CLK_GATE_DCLK`, `ASPEED_CLK_GATE_REFCLK`, `ASPEED_CLK_GATE_USBPORT2CLK`, .... explicit numeric ids span 0..37 across 50 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `ASPEED_CLK_GATE_ECLK`, `ASPEED_RESET_XDMA` share `0`; `ASPEED_CLK_GATE_GCLK`, `ASPEED_RESET_MCTP` share `1`; `ASPEED_CLK_GATE_MCLK`, `ASPEED_RESET_ADC` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Aspeed SCU clock/reset drivers and BMC DTS files that request gates, PLL-derived clocks, and resets by these ids. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
