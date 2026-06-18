# sources/distributed-fs/ceph-client/include/dt-bindings/clock/en7523-clk.h

## Purpose
`en7523-clk.h` defines the device-tree clock binding ABI for Airoha/EcoNet EN7523 and EN7581 clock ids for switch, EMI, bus, SLIC, SPI, NPU, crypto, PCIe, and eMMC. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_AIROHA_EN7523_H_`. The binding surface has 9 exported non-guard macros; macro families include EN7523_CLK_GSW (1), EN7523_CLK_EMI (1), EN7523_CLK_BUS (1), EN7523_CLK_SLIC (1), EN7523_CLK_SPI (1), EN7523_CLK_NPU (1), EN7523_CLK_CRYPTO (1), EN7523_CLK_PCIE (1). Representative ids include `EN7523_CLK_GSW`, `EN7523_CLK_EMI`, `EN7523_CLK_BUS`, `EN7523_CLK_SLIC`, `EN7523_CLK_SPI`, `EN7523_CLK_NPU`, `EN7523_CLK_CRYPTO`, `EN7523_CLK_PCIE`, .... explicit numeric ids span 0..8 across 9 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with EcoNet/Airoha SCU or clock drivers and networking SoC DTS files. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
