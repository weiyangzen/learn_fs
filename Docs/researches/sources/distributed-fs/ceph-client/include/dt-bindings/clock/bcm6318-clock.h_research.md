# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6318-clock.h

## Purpose
`bcm6318-clock.h` defines the device-tree clock binding ABI for Broadcom BCM6318 clock ids for ASB bridges, CPU bus, ADSL/SAR, PCIe, USB, SPI, AFE, and packet processors. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM6318_H`. The binding surface has 34 exported non-guard macros; macro families include BCM6318_CLK_ADSL (2), BCM6318_CLK_MIPS (2), BCM6318_CLK_PCIE (2), BCM6318_CLK_PHYMIPS (2), BCM6318_CLK_SDR (2), BCM6318_CLK_USB (1), BCM6318_CLK_ROBOSW (1), BCM6318_CLK_SAR (1). Representative ids include `BCM6318_CLK_ADSL_ASB`, `BCM6318_CLK_USB_ASB`, `BCM6318_CLK_MIPS_ASB`, `BCM6318_CLK_PCIE_ASB`, `BCM6318_CLK_PHYMIPS_ASB`, `BCM6318_CLK_ROBOSW_ASB`, `BCM6318_CLK_SAR_ASB`, `BCM6318_CLK_SDR_ASB`, .... explicit numeric ids span 0..30 across 34 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM6318_CLK_ADSL_ASB`, `BCM6318_UCLK_ADSL` share `0`; `BCM6318_CLK_USB_ASB`, `BCM6318_UCLK_ARB` share `1`; `BCM6318_CLK_MIPS_ASB`, `BCM6318_UCLK_MIPS` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
