# subset-b-005815 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/aspeed,ast2700-scu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/aspeed,ast2700-scu.h

## Purpose
`aspeed,ast2700-scu.h` defines the device-tree clock binding ABI for AST2700 SCU0/SCU1 clock and gate identifiers for the two-system Aspeed clock controller. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_AST2700_H`. The binding surface has 148 exported non-guard macros; macro families include SCU1 (88), SCU0 (60). Representative ids include `SCU0_CLKIN`, `SCU0_CLK_24M`, `SCU0_CLK_192M`, `SCU0_CLK_UART`, `SCU0_CLK_UART_DIV13`, `SCU0_CLK_PSP`, `SCU0_CLK_HPLL`, `SCU0_CLK_HPLL_DIV2`, .... explicit numeric ids span 0..87 across 148 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `SOC0 clk`, `SOC0 clk-gate`, `SOC1 clk`, `SOC1 clk gate`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `SCU0_CLKIN`, `SCU1_CLKIN` share `0`; `SCU0_CLK_24M`, `SCU1_CLK_HPLL` share `1`; `SCU0_CLK_192M`, `SCU1_CLK_APLL` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Aspeed SCU clock/reset drivers and BMC DTS files that request gates, PLL-derived clocks, and resets by these ids. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/aspeed,ast2700-scu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/aspeed-clock.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/aspeed-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ast2600-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ast2600-clock.h

## Purpose
`ast2600-clock.h` defines the device-tree clock binding ABI for AST2600 clock-gate, generated-clock, and reset identifiers, including MAC, UART, I3C, FSI, and PCIe reset domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_AST2600_CLOCK_H`. The binding surface has 107 exported non-guard macros; macro families include ASPEED_CLK_GATE (44), ASPEED_RESET (36), ASPEED_CLK (27). Representative ids include `ASPEED_CLK_GATE_ECLK`, `ASPEED_CLK_GATE_GCLK`, `ASPEED_CLK_GATE_MCLK`, `ASPEED_CLK_GATE_VCLK`, `ASPEED_CLK_GATE_BCLK`, `ASPEED_CLK_GATE_DCLK`, `ASPEED_CLK_GATE_LCLK`, `ASPEED_CLK_GATE_LHCCLK`, .... explicit numeric ids span 0..72 across 107 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `Only list resets here that are not part of a clock gate + reset pair`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `ASPEED_CLK_GATE_ECLK`, `ASPEED_RESET_SDRAM` share `0`; `ASPEED_CLK_GATE_GCLK`, `ASPEED_RESET_AHB` share `1`; `ASPEED_CLK_GATE_BCLK`, `ASPEED_RESET_HACE` share `4`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Aspeed SCU clock/reset drivers and BMC DTS files that request gates, PLL-derived clocks, and resets by these ids. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ast2600-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/at91.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/at91.h

## Purpose
`at91.h` defines the device-tree clock binding ABI for Microchip/Atmel AT91 PMC clock type, clock id, status-bit, and slow-clock constants used by PMC bindings. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLK_AT91_H`. The binding surface has 42 exported non-guard macros; macro families include PMC_TYPE_CORE (1), PMC_TYPE_SYSTEM (1), PMC_TYPE_PERIPHERAL (1), PMC_TYPE_GCK (1), PMC_TYPE_PROGRAMMABLE (1), PMC_SLOW (1), PMC_MCK (1), PMC_UTMI (1). Representative ids include `PMC_TYPE_CORE`, `PMC_TYPE_SYSTEM`, `PMC_TYPE_PERIPHERAL`, `PMC_TYPE_GCK`, `PMC_TYPE_PROGRAMMABLE`, `PMC_SLOW`, `PMC_MCK`, `PMC_UTMI`, .... explicit numeric ids span 0..10 across 18 constants. Function-like helpers: `AT91_PMC_PCKRDY`. Expression/string-style macros to review include `PMC_CPUPLL`, `PMC_SYSPLL`, `PMC_DDRPLL`, `PMC_IMGPLL`, `PMC_BAUDPLL`, `PMC_AUDIOPMCPLL`, `PMC_AUDIOIOPLL`, `PMC_ETHPLL`. File section comments identify domains such as `SAMA7G5`, `SAM9X7`, `SAMA7D65`, `MOSCS Flag`, `PLLA Lock`, `PLLB Lock`, `Master Clock`, `UPLL Lock`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `PMC_TYPE_CORE`, `PMC_SLOW`, `SCKC_MD_SLCK` share `0`; `PMC_TYPE_SYSTEM`, `PMC_MCK`, `SCKC_TD_SLCK` share `1`; `PMC_TYPE_PERIPHERAL`, `PMC_UTMI` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with the matching platform clock provider, Linux common-clock registration tables, and DTS consumers that use these numeric ids. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/at91.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ath79-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ath79-clk.h

## Purpose
`ath79-clk.h` defines the device-tree clock binding ABI for Atheros ATH79 CPU, DDR, AHB, reference, and MDIO clock ids. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_ATH79_CLK_H`. The binding surface has 6 exported non-guard macros; macro families include ATH79_CLK_CPU (1), ATH79_CLK_DDR (1), ATH79_CLK_AHB (1), ATH79_CLK_REF (1), ATH79_CLK_MDIO (1), ATH79_CLK_END (1). Representative ids include `ATH79_CLK_CPU`, `ATH79_CLK_DDR`, `ATH79_CLK_AHB`, `ATH79_CLK_REF`, `ATH79_CLK_MDIO`, `ATH79_CLK_END`. explicit numeric ids span 0..5 across 6 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/ath79-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-aoclkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-aoclkc.h

## Purpose
`axg-aoclkc.h` defines the device-tree clock binding ABI for Amlogic Meson AXG always-on clock controller ids for AO peripherals and low-frequency derived clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_CLOCK_AMLOGIC_MESON_AXG_AOCLK`. The binding surface has 17 exported non-guard macros; macro families include CLKID_AO (17). Representative ids include `CLKID_AO_REMOTE`, `CLKID_AO_I2C_MASTER`, `CLKID_AO_I2C_SLAVE`, `CLKID_AO_UART1`, `CLKID_AO_UART2`, `CLKID_AO_IR_BLASTER`, `CLKID_AO_SAR_ADC`, `CLKID_AO_CLK81`, .... explicit numeric ids span 0..16 across 17 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Amlogic Meson clock-controller drivers and DTS `clocks`/`assigned-clocks` specifiers for AO, audio, or main HIU domains. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-aoclkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-audio-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-audio-clkc.h

## Purpose
`axg-audio-clkc.h` defines the device-tree clock binding ABI for Amlogic AXG audio clock controller ids for TDM, SPDIF, PDM, DDR audio DMA, mclk/sclk/lrclk trees, and later audio blocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__AXG_AUDIO_CLKC_BINDINGS_H`. The binding surface has 155 exported non-guard macros; macro families include AUD_CLKID (155). Representative ids include `AUD_CLKID_DDR_ARB`, `AUD_CLKID_PDM`, `AUD_CLKID_TDMIN_A`, `AUD_CLKID_TDMIN_B`, `AUD_CLKID_TDMIN_C`, `AUD_CLKID_TDMIN_LB`, `AUD_CLKID_TDMOUT_A`, `AUD_CLKID_TDMOUT_B`, .... explicit numeric ids span 29..184 across 155 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Amlogic Meson clock-controller drivers and DTS `clocks`/`assigned-clocks` specifiers for AO, audio, or main HIU domains. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-audio-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-clkc.h

## Purpose
`axg-clkc.h` defines the device-tree clock binding ABI for Amlogic Meson AXG main clock tree ids for PLLs, muxes, dividers, gates, video, CPU, GPU, and peripheral clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__AXG_CLKC_H`. The binding surface has 136 exported non-guard macros; macro families include CLKID (131), CLKID_AO (5). Representative ids include `CLKID_SYS_PLL`, `CLKID_FIXED_PLL`, `CLKID_FCLK_DIV2`, `CLKID_FCLK_DIV3`, `CLKID_FCLK_DIV4`, `CLKID_FCLK_DIV5`, `CLKID_FCLK_DIV7`, `CLKID_GP0_PLL`, .... explicit numeric ids span 0..136 across 136 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Amlogic Meson clock-controller drivers and DTS `clocks`/`assigned-clocks` specifiers for AO, audio, or main HIU domains. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axg-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec6-clkctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec6-clkctrl.h

## Purpose
`axis,artpec6-clkctrl.h` defines the device-tree clock binding ABI for Axis ARTPEC-6 clock controller ids for CPU, NAND, Ethernet, DMA, SD, I2S, UART, I2C, SPI, timer, and debug clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_CLK_ARTPEC6_CLKCTRL_H`. The binding surface has 21 exported non-guard macros; macro families include ARTPEC6_CLK_CPU (2), ARTPEC6_CLK_NAND (2), ARTPEC6_CLK_SD (2), ARTPEC6_CLK_UART (2), ARTPEC6_CLK_SPI (2), ARTPEC6_CLK_ETH (1), ARTPEC6_CLK_DMA (1), ARTPEC6_CLK_PTP (1). Representative ids include `ARTPEC6_CLK_CPU`, `ARTPEC6_CLK_CPU_PERIPH`, `ARTPEC6_CLK_NAND_CLKA`, `ARTPEC6_CLK_NAND_CLKB`, `ARTPEC6_CLK_ETH_ACLK`, `ARTPEC6_CLK_DMA_ACLK`, `ARTPEC6_CLK_PTP_REF`, `ARTPEC6_CLK_SD_PCLK`, .... explicit numeric ids span 0..20 across 21 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `This must be the highest clock index plus one`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec6-clkctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec8-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec8-clk.h

## Purpose
`axis,artpec8-clk.h` defines the device-tree clock binding ABI for Axis ARTPEC-8 CMU clock ids patterned after Samsung-style PLL, divider, mux, and gate domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_ARTPEC8_H`. The binding surface has 141 exported non-guard macros; macro families include CLK_DOUT (70), CLK_GOUT (47), CLK_MOUT (19), CLK_FOUT (5). Representative ids include `CLK_FOUT_SHARED0_PLL`, `CLK_DOUT_SHARED0_DIV2`, `CLK_DOUT_SHARED0_DIV3`, `CLK_DOUT_SHARED0_DIV4`, `CLK_FOUT_SHARED1_PLL`, `CLK_DOUT_SHARED1_DIV2`, `CLK_DOUT_SHARED1_DIV3`, `CLK_DOUT_SHARED1_DIV4`, .... explicit numeric ids span 1..46 across 141 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `CMU_CMU`, `CMU_BUS`, `CMU_CORE`, `CMU_CPUCL`, `CMU_FSYS`, `CMU_IMEM`, `CMU_PERI`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_FOUT_SHARED0_PLL`, `CLK_MOUT_BUS_ACLK_USER`, `CLK_MOUT_CORE_ACLK_USER`, `CLK_FOUT_CPUCL_PLL` share `1`; `CLK_DOUT_SHARED0_DIV2`, `CLK_MOUT_BUS_DLP_USER`, `CLK_MOUT_CORE_DLP_USER`, `CLK_MOUT_CPUCL_PLL` share `2`; `CLK_DOUT_SHARED0_DIV3`, `CLK_DOUT_BUS_PCLK`, `CLK_DOUT_CORE_PCLK`, `CLK_MOUT_CPUCL_SWITCH_USER` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec8-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec9-clk.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/axis,artpec9-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-cygnus.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-cygnus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-ns2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-ns2.h

## Purpose
`bcm-ns2.h` defines the device-tree clock binding ABI for Broadcom Northstar2 iProc PLL and peripheral clock ids for SCR, switch, DDR, ports, and ASIU domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_CLOCK_BCM_NS2_H`. The binding surface has 28 exported non-guard macros; macro families include BCM_NS2_GENPLL (14), BCM_NS2_LCPLL (14). Representative ids include `BCM_NS2_GENPLL_SCR`, `BCM_NS2_GENPLL_SCR_SCR_CLK`, `BCM_NS2_GENPLL_SCR_FS_CLK`, `BCM_NS2_GENPLL_SCR_AUDIO_CLK`, `BCM_NS2_GENPLL_SCR_CH3_UNUSED`, `BCM_NS2_GENPLL_SCR_CH4_UNUSED`, `BCM_NS2_GENPLL_SCR_CH5_UNUSED`, `BCM_NS2_GENPLL_SW`, .... explicit numeric ids span 0..6 across 28 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `GENPLL SCR clock channel ID`, `GENPLL SW clock channel ID`, `LCPLL DDR clock channel ID`, `LCPLL PORTS clock channel ID`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM_NS2_GENPLL_SCR`, `BCM_NS2_GENPLL_SW`, `BCM_NS2_LCPLL_DDR`, `BCM_NS2_LCPLL_PORTS` share `0`; `BCM_NS2_GENPLL_SCR_SCR_CLK`, `BCM_NS2_GENPLL_SW_RPE_CLK`, `BCM_NS2_LCPLL_DDR_PCIE_SATA_USB_CLK`, `BCM_NS2_LCPLL_PORTS_WAN_CLK` share `1`; `BCM_NS2_GENPLL_SCR_FS_CLK`, `BCM_NS2_GENPLL_SW_250_CLK`, `BCM_NS2_LCPLL_DDR_DDR_CLK`, `BCM_NS2_LCPLL_PORTS_RGMII_CLK` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-ns2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-nsp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-nsp.h

## Purpose
`bcm-nsp.h` defines the device-tree clock binding ABI for Broadcom Northstar Plus PLL/channel ids for PHY, Ethernet, USB, SATA, PCIe, SDIO, and DDR clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_CLOCK_BCM_NSP_H`. The binding surface has 11 exported non-guard macros; macro families include BCM_NSP_GENPLL (7), BCM_NSP_LCPLL0 (4). Representative ids include `BCM_NSP_GENPLL`, `BCM_NSP_GENPLL_PHY_CLK`, `BCM_NSP_GENPLL_ENET_SW_CLK`, `BCM_NSP_GENPLL_USB_PHY_REF_CLK`, `BCM_NSP_GENPLL_IPROCFAST_CLK`, `BCM_NSP_GENPLL_SATA1_CLK`, `BCM_NSP_GENPLL_SATA2_CLK`, `BCM_NSP_LCPLL0`, .... explicit numeric ids span 0..6 across 11 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `GENPLL clock channel ID`, `LCPLL0 clock channel ID`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM_NSP_GENPLL`, `BCM_NSP_LCPLL0` share `0`; `BCM_NSP_GENPLL_PHY_CLK`, `BCM_NSP_LCPLL0_PCIE_PHY_REF_CLK` share `1`; `BCM_NSP_GENPLL_ENET_SW_CLK`, `BCM_NSP_LCPLL0_SDIO_CLK` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-nsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-sr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-sr.h

## Purpose
`bcm-sr.h` defines the device-tree clock binding ABI for Broadcom Stingray PLL/channel clock ids covering PCIe, NIC, NITRO, HSLS, SDIO, CCN, NOC, crypto, and SATA domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_CLOCK_BCM_SR_H`. The binding surface has 49 exported non-guard macros; macro families include BCM_SR_GENPLL0 (7), BCM_SR_GENPLL2 (7), BCM_SR_GENPLL4 (6), BCM_SR_LCPLL0 (5), BCM_SR_GENPLL5 (4), BCM_SR_LCPLL1 (4), BCM_SR_GENPLL1 (3), BCM_SR_GENPLL3 (3). Representative ids include `BCM_SR_GENPLL0`, `BCM_SR_GENPLL0_125M_CLK`, `BCM_SR_GENPLL0_SCR_CLK`, `BCM_SR_GENPLL0_250M_CLK`, `BCM_SR_GENPLL0_PCIE_AXI_CLK`, `BCM_SR_GENPLL0_PAXC_AXI_X2_CLK`, `BCM_SR_GENPLL0_PAXC_AXI_CLK`, `BCM_SR_GENPLL1`, .... explicit numeric ids span 0..6 across 49 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `GENPLL 0 clock channel ID SCR HSLS FS PCIE`, `GENPLL 1 clock channel ID MHB PCIE NITRO`, `GENPLL 2 clock channel ID NITRO MHB`, `GENPLL 3 HSLS clock channel ID`, `GENPLL 4 SCR clock channel ID`, `GENPLL 5 FS4 clock channel ID`, `GENPLL 6 NITRO clock channel ID`, `LCPLL0 clock channel ID`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM_SR_GENPLL0`, `BCM_SR_GENPLL1`, `BCM_SR_GENPLL2`, `BCM_SR_GENPLL3` share `0`; `BCM_SR_GENPLL0_125M_CLK`, `BCM_SR_GENPLL1_PCIE_TL_CLK`, `BCM_SR_GENPLL2_NIC_CLK`, `BCM_SR_GENPLL3_HSLS_CLK` share `1`; `BCM_SR_GENPLL0_SCR_CLK`, `BCM_SR_GENPLL1_MHB_APB_CLK`, `BCM_SR_GENPLL2_TS_500_CLK`, `BCM_SR_GENPLL3_SDIO_CLK` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm-sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm21664.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm21664.h

## Purpose
`bcm21664.h` defines the device-tree clock binding ABI for Broadcom BCM21664 CCU compatible strings and per-CCU clock ids/counts for root, AON, master, and slave controllers. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_CLOCK_BCM21664_H`. The binding surface has 25 exported non-guard macros; macro families include BCM21664_MASTER_CCU (9), BCM21664_SLAVE_CCU (8), BCM21664_ROOT_CCU (2), BCM21664_AON_CCU (2), BCM21664_DT_ROOT (1), BCM21664_DT_AON (1), BCM21664_DT_MASTER (1), BCM21664_DT_SLAVE (1). Representative ids include `BCM21664_DT_ROOT_CCU_COMPAT`, `BCM21664_DT_AON_CCU_COMPAT`, `BCM21664_DT_MASTER_CCU_COMPAT`, `BCM21664_DT_SLAVE_CCU_COMPAT`, `BCM21664_ROOT_CCU_FRAC_1M`, `BCM21664_ROOT_CCU_CLOCK_COUNT`, `BCM21664_AON_CCU_HUB_TIMER`, `BCM21664_AON_CCU_CLOCK_COUNT`, .... explicit numeric ids span 0..8 across 21 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `bcm21664 CCU device tree "compatible" strings`, `root CCU clock ids`, `aon CCU clock ids`, `master CCU clock ids`, `slave CCU clock ids`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM21664_ROOT_CCU_FRAC_1M`, `BCM21664_AON_CCU_HUB_TIMER`, `BCM21664_MASTER_CCU_SDIO1`, `BCM21664_SLAVE_CCU_UARTB` share `0`; `BCM21664_ROOT_CCU_CLOCK_COUNT`, `BCM21664_AON_CCU_CLOCK_COUNT`, `BCM21664_MASTER_CCU_SDIO2`, `BCM21664_SLAVE_CCU_UARTB2` share `1`; `BCM21664_MASTER_CCU_SDIO3`, `BCM21664_SLAVE_CCU_UARTB3` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm21664.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm281xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm281xx.h

## Purpose
`bcm281xx.h` defines the device-tree clock binding ABI for Broadcom BCM281xx CCU compatible strings and per-CCU clock ids/counts for root, AON, hub, master, and slave controllers. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_CLOCK_BCM281XX_H`. The binding surface has 32 exported non-guard macros; macro families include BCM281XX_SLAVE_CCU (11), BCM281XX_MASTER_CCU (8), BCM281XX_AON_CCU (4), BCM281XX_ROOT_CCU (2), BCM281XX_HUB_CCU (2), BCM281XX_DT_ROOT (1), BCM281XX_DT_AON (1), BCM281XX_DT_HUB (1). Representative ids include `BCM281XX_DT_ROOT_CCU_COMPAT`, `BCM281XX_DT_AON_CCU_COMPAT`, `BCM281XX_DT_HUB_CCU_COMPAT`, `BCM281XX_DT_MASTER_CCU_COMPAT`, `BCM281XX_DT_SLAVE_CCU_COMPAT`, `BCM281XX_ROOT_CCU_FRAC_1M`, `BCM281XX_ROOT_CCU_CLOCK_COUNT`, `BCM281XX_AON_CCU_HUB_TIMER`, .... explicit numeric ids span 0..10 across 27 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `root CCU clock ids`, `aon CCU clock ids`, `hub CCU clock ids`, `master CCU clock ids`, `slave CCU clock ids`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM281XX_ROOT_CCU_FRAC_1M`, `BCM281XX_AON_CCU_HUB_TIMER`, `BCM281XX_HUB_CCU_TMON_1M`, `BCM281XX_MASTER_CCU_SDIO1` share `0`; `BCM281XX_ROOT_CCU_CLOCK_COUNT`, `BCM281XX_AON_CCU_PMU_BSC`, `BCM281XX_HUB_CCU_CLOCK_COUNT`, `BCM281XX_MASTER_CCU_SDIO2` share `1`; `BCM281XX_AON_CCU_PMU_BSC_VAR`, `BCM281XX_MASTER_CCU_SDIO3`, `BCM281XX_SLAVE_CCU_UARTB3` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm281xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm2835-aux.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm2835-aux.h

## Purpose
`bcm2835-aux.h` defines the device-tree clock binding ABI for Raspberry Pi BCM2835 auxiliary UART/SPI clock ids and count. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `BCM2835_AUX_CLOCK_UART`. The binding surface has 4 exported non-guard macros; macro families include BCM2835_AUX_CLOCK (4). Representative ids include `BCM2835_AUX_CLOCK_UART`, `BCM2835_AUX_CLOCK_SPI1`, `BCM2835_AUX_CLOCK_SPI2`, `BCM2835_AUX_CLOCK_COUNT`. explicit numeric ids span 0..3 across 4 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm2835-aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm2835.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm2835.h

## Purpose
`bcm2835.h` defines the device-tree clock binding ABI for Raspberry Pi BCM2835 core PLL, PLL-channel, and peripheral clock ids. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `BCM2835_PLLA`. The binding surface has 52 exported non-guard macros; macro families include BCM2835_CLOCK (30), BCM2835_PLL (21), BCM2711_CLOCK_EMMC2 (1). Representative ids include `BCM2835_PLLA`, `BCM2835_PLLB`, `BCM2835_PLLC`, `BCM2835_PLLD`, `BCM2835_PLLH`, `BCM2835_PLLA_CORE`, `BCM2835_PLLA_PER`, `BCM2835_PLLB_ARM`, .... explicit numeric ids span 0..51 across 52 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm2835.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm3368-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm3368-clock.h

## Purpose
`bcm3368-clock.h` defines the device-tree clock binding ABI for Broadcom BCM3368 clock gate ids for cable/DSL networking, USB, SPI, PCM, Ethernet, and PHY blocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM3368_H`. The binding surface has 17 exported non-guard macros; macro families include BCM3368_CLK_ACP (2), BCM3368_CLK_MAC (1), BCM3368_CLK_TC (1), BCM3368_CLK_US (1), BCM3368_CLK_DS (1), BCM3368_CLK_ACM (1), BCM3368_CLK_SPI (1), BCM3368_CLK_USBS (1). Representative ids include `BCM3368_CLK_MAC`, `BCM3368_CLK_TC`, `BCM3368_CLK_US_TOP`, `BCM3368_CLK_DS_TOP`, `BCM3368_CLK_ACM`, `BCM3368_CLK_SPI`, `BCM3368_CLK_USBS`, `BCM3368_CLK_BMU`, .... explicit numeric ids span 3..21 across 17 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm3368-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6318-clock.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6318-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm63268-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm63268-clock.h

## Purpose
`bcm63268-clock.h` defines the device-tree clock binding ABI for Broadcom BCM63268 clock and timer-clock ids for VDSL, WLAN, FAP, SAR, switch, USB, PCIe, GMAC, NAND, and EPHY domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM63268_H`. The binding surface has 35 exported non-guard macros; macro families include BCM63268_CLK_VDSL (3), BCM63268_TCLK_WAKEON (2), BCM63268_TCLK_UTO (2), BCM63268_CLK_DIS (1), BCM63268_CLK_MIPS (1), BCM63268_CLK_WLAN (1), BCM63268_CLK_DECT (1), BCM63268_CLK_FAP0 (1). Representative ids include `BCM63268_CLK_DIS_GLESS`, `BCM63268_CLK_VDSL_QPROC`, `BCM63268_CLK_VDSL_AFE`, `BCM63268_CLK_VDSL`, `BCM63268_CLK_MIPS`, `BCM63268_CLK_WLAN_OCP`, `BCM63268_CLK_DECT`, `BCM63268_CLK_FAP0`, .... explicit numeric ids span 0..31 across 35 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `BCM63268_CLK_DIS_GLESS`, `BCM63268_TCLK_EPHY1` share `0`; `BCM63268_CLK_VDSL_QPROC`, `BCM63268_TCLK_EPHY2` share `1`; `BCM63268_CLK_VDSL_AFE`, `BCM63268_TCLK_EPHY3` share `2`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm63268-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6328-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6328-clock.h

## Purpose
`bcm6328-clock.h` defines the device-tree clock binding ABI for Broadcom BCM6328 clock ids for PHY MIPS, ADSL, MIPS, SAR, PCM, USB, SPI, PCIe, and switch blocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM6328_H`. The binding surface has 12 exported non-guard macros; macro families include BCM6328_CLK_ADSL (3), BCM6328_CLK_PHYMIPS (1), BCM6328_CLK_MIPS (1), BCM6328_CLK_SAR (1), BCM6328_CLK_PCM (1), BCM6328_CLK_USBD (1), BCM6328_CLK_USBH (1), BCM6328_CLK_HSSPI (1). Representative ids include `BCM6328_CLK_PHYMIPS`, `BCM6328_CLK_ADSL_QPROC`, `BCM6328_CLK_ADSL_AFE`, `BCM6328_CLK_ADSL`, `BCM6328_CLK_MIPS`, `BCM6328_CLK_SAR`, `BCM6328_CLK_PCM`, `BCM6328_CLK_USBD`, .... explicit numeric ids span 0..11 across 12 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6328-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6358-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6358-clock.h

## Purpose
`bcm6358-clock.h` defines the device-tree clock binding ABI for Broadcom BCM6358 clock ids for Ethernet, ADSL PHY, PCM, SPI, USB, SAR, and embedded USB/EPHY blocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM6358_H`. The binding surface has 11 exported non-guard macros; macro families include BCM6358_CLK_ENET (1), BCM6358_CLK_ADSLPHY (1), BCM6358_CLK_PCM (1), BCM6358_CLK_SPI (1), BCM6358_CLK_USBS (1), BCM6358_CLK_SAR (1), BCM6358_CLK_EMUSB (1), BCM6358_CLK_ENET0 (1). Representative ids include `BCM6358_CLK_ENET`, `BCM6358_CLK_ADSLPHY`, `BCM6358_CLK_PCM`, `BCM6358_CLK_SPI`, `BCM6358_CLK_USBS`, `BCM6358_CLK_SAR`, `BCM6358_CLK_EMUSB`, `BCM6358_CLK_ENET0`, .... explicit numeric ids span 4..21 across 11 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6358-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6362-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6362-clock.h

## Purpose
`bcm6362-clock.h` defines the device-tree clock binding ABI for Broadcom BCM6362 clock ids for ADSL, MIPS, WLAN, USB/SAR packet switching, IPsec, SPI, PCIe, FAP, and NAND. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM6362_H`. The binding surface has 19 exported non-guard macros; macro families include BCM6362_CLK_ADSL (3), BCM6362_CLK_SWPKT (2), BCM6362_CLK_MIPS (1), BCM6362_CLK_WLAN (1), BCM6362_CLK_SAR (1), BCM6362_CLK_ROBOSW (1), BCM6362_CLK_PCM (1), BCM6362_CLK_USBD (1). Representative ids include `BCM6362_CLK_ADSL_QPROC`, `BCM6362_CLK_ADSL_AFE`, `BCM6362_CLK_ADSL`, `BCM6362_CLK_MIPS`, `BCM6362_CLK_WLAN_OCP`, `BCM6362_CLK_SWPKT_USB`, `BCM6362_CLK_SWPKT_SAR`, `BCM6362_CLK_SAR`, .... explicit numeric ids span 1..20 across 19 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6362-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6368-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6368-clock.h

## Purpose
`bcm6368-clock.h` defines the device-tree clock binding ABI for Broadcom BCM6368 clock ids for VDSL, PHY MIPS, USB/SAR packet switching, SPI, UTOPIA, PCM, NAND, and IPsec. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BCM6368_H`. The binding surface has 17 exported non-guard macros; macro families include BCM6368_CLK_VDSL (4), BCM6368_CLK_SWPKT (2), BCM6368_CLK_PHYMIPS (1), BCM6368_CLK_SPI (1), BCM6368_CLK_USBD (1), BCM6368_CLK_SAR (1), BCM6368_CLK_ROBOSW (1), BCM6368_CLK_UTOPIA (1). Representative ids include `BCM6368_CLK_VDSL_QPROC`, `BCM6368_CLK_VDSL_AFE`, `BCM6368_CLK_VDSL_BONDING`, `BCM6368_CLK_VDSL`, `BCM6368_CLK_PHYMIPS`, `BCM6368_CLK_SWPKT_USB`, `BCM6368_CLK_SWPKT_SAR`, `BCM6368_CLK_SPI`, .... explicit numeric ids span 2..18 across 17 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Broadcom CCU/iProc/BCM clock drivers and DTS clock specifiers; some headers also export compatible-string helpers or per-controller count constants. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bcm6368-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/berlin2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/berlin2.h

## Purpose
`berlin2.h` defines the device-tree clock binding ABI for Marvell Berlin2 clock ids for system, CPU, graphics, video, audio, storage, and peripheral domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `CLKID_SYS`. The binding surface has 41 exported non-guard macros; macro families include CLKID (41). Representative ids include `CLKID_SYS`, `CLKID_CPU`, `CLKID_DRMFIGO`, `CLKID_CFG`, `CLKID_GFX`, `CLKID_ZSP`, `CLKID_PERIF`, `CLKID_PCUBE`, .... explicit numeric ids span 0..40 across 41 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/berlin2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/berlin2q.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/berlin2q.h

## Purpose
`berlin2q.h` defines the device-tree clock binding ABI for Marvell Berlin2Q clock ids for system, graphics, video, SDIO, Ethernet, SATA, USB, PCIe bridge, NFC, and smart-card domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `CLKID_SYS`. The binding surface has 28 exported non-guard macros; macro families include CLKID (28). Representative ids include `CLKID_SYS`, `CLKID_DRMFIGO`, `CLKID_CFG`, `CLKID_GFX2D`, `CLKID_ZSP`, `CLKID_PERIF`, `CLKID_PCUBE`, `CLKID_VSCOPE`, .... explicit numeric ids span 0..27 across 28 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/berlin2q.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bm1880-clock.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/bm1880-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/boston-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/boston-clock.h

## Purpose
`boston-clock.h` defines the device-tree clock binding ABI for MIPS Boston board input, system, and CPU clock ids. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_BOSTON_CLOCK_H__`. The binding surface has 3 exported non-guard macros; macro families include BOSTON_CLK_INPUT (1), BOSTON_CLK_SYS (1), BOSTON_CLK_CPU (1). Representative ids include `BOSTON_CLK_INPUT`, `BOSTON_CLK_SYS`, `BOSTON_CLK_CPU`. explicit numeric ids span 0..2 across 3 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/boston-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cirrus,cs2000-cp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/cirrus,cs2000-cp.h

## Purpose
`cirrus,cs2000-cp.h` defines the device-tree clock binding ABI for Cirrus CS2000-CP auxiliary output clock selection constants. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CS2000CP_CLK_H`. The binding surface has 4 exported non-guard macros; macro families include CS2000CP_AUX_OUTPUT (4). Representative ids include `CS2000CP_AUX_OUTPUT_REF_CLK`, `CS2000CP_AUX_OUTPUT_CLK_IN`, `CS2000CP_AUX_OUTPUT_CLK_OUT`, `CS2000CP_AUX_OUTPUT_PLL_LOCK`. explicit numeric ids span 0..3 across 4 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Cirrus/EP93xx/CLPS711x clock or syscon drivers and board DTS files. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cirrus,cs2000-cp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cirrus,ep9301-syscon.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/cirrus,ep9301-syscon.h

## Purpose
`cirrus,ep9301-syscon.h` defines the device-tree clock binding ABI for Cirrus EP93xx syscon clock ids and reset ids for PLLs, buses, DMA, UART, I2S, video, key matrix, and touchscreen. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_CIRRUS_EP93XX_CLOCK_H`. The binding surface has 31 exported non-guard macros; macro families include EP93XX_CLK (31). Representative ids include `EP93XX_CLK_PLL1`, `EP93XX_CLK_PLL2`, `EP93XX_CLK_FCLK`, `EP93XX_CLK_HCLK`, `EP93XX_CLK_PCLK`, `EP93XX_CLK_UART`, `EP93XX_CLK_SPI`, `EP93XX_CLK_PWM`, .... explicit numeric ids span 0..30 across 31 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Cirrus/EP93xx/CLPS711x clock or syscon drivers and board DTS files. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cirrus,ep9301-syscon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cix,sky1.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/cix,sky1.h

## Purpose
`cix,sky1.h` defines the device-tree clock binding ABI for CIX Sky1 clock tree ids spanning CPU/DSU, CSI, display, GPU, NPU, PCIe, audio, storage, Ethernet, and peripheral domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLK_CIX_SKY1_H`. The binding surface has 268 exported non-guard macros; macro families include CLK_TREE (268). Representative ids include `CLK_TREE_CPU_GICxCLK`, `CLK_TREE_CPU_PPUCLK`, `CLK_TREE_CPU_PERIPHCLK`, `CLK_TREE_DSU_CLK`, `CLK_TREE_DSU_PCLK`, `CLK_TREE_CPU_CLK_BC0`, `CLK_TREE_CPU_CLK_BC1`, `CLK_TREE_CPU_CLK_BC2`, .... explicit numeric ids span 0..272 across 268 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `267~271 not used by AP, skip`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cix,sky1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/clps711x-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/clps711x-clock.h

## Purpose
`clps711x-clock.h` defines the device-tree clock binding ABI for Cirrus/CLPS711x clock ids for CPU, bus, PLL, timers, PWM, SPI, UART, tick, and maximum id. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLOCK_CLPS711X_H`. The binding surface has 13 exported non-guard macros; macro families include CLPS711X_CLK_DUMMY (1), CLPS711X_CLK_CPU (1), CLPS711X_CLK_BUS (1), CLPS711X_CLK_PLL (1), CLPS711X_CLK_TIMERREF (1), CLPS711X_CLK_TIMER1 (1), CLPS711X_CLK_TIMER2 (1), CLPS711X_CLK_PWM (1). Representative ids include `CLPS711X_CLK_DUMMY`, `CLPS711X_CLK_CPU`, `CLPS711X_CLK_BUS`, `CLPS711X_CLK_PLL`, `CLPS711X_CLK_TIMERREF`, `CLPS711X_CLK_TIMER1`, `CLPS711X_CLK_TIMER2`, `CLPS711X_CLK_PWM`, .... explicit numeric ids span 0..12 across 13 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Cirrus/EP93xx/CLPS711x clock or syscon drivers and board DTS files. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/clps711x-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cortina,gemini-clock.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/cortina,gemini-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/dm814.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/dm814.h

## Purpose
`dm814.h` defines the device-tree clock binding ABI for TI DM814 clockctrl offsets for USB, UART, GPIO, I2C, watchdog, SPI, GPMC, MPU, RTC, DMA, MMC, Ethernet, and security modules. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLK_DM814_H`. The binding surface has 27 exported non-guard macros; macro families include DM814_ETHERNET_CLKCTRL (2), DM814_CLKCTRL_OFFSET (1), DM814_CLKCTRL_INDEX (1), DM814_USB_OTG (1), DM814_UART1_CLKCTRL (1), DM814_UART2_CLKCTRL (1), DM814_UART3_CLKCTRL (1), DM814_GPIO1_CLKCTRL (1). Representative ids include `DM814_CLKCTRL_OFFSET`, `DM814_CLKCTRL_INDEX`, `DM814_USB_OTG_HS_CLKCTRL`, `DM814_UART1_CLKCTRL`, `DM814_UART2_CLKCTRL`, `DM814_UART3_CLKCTRL`, `DM814_GPIO1_CLKCTRL`, `DM814_GPIO2_CLKCTRL`, .... explicit numeric ids span 0..468 across 2 constants. Function-like helpers: `DM814_CLKCTRL_INDEX`, `DM814_ETHERNET_CLKCTRL_INDEX`. Expression/string-style macros to review include `DM814_USB_OTG_HS_CLKCTRL`, `DM814_UART1_CLKCTRL`, `DM814_UART2_CLKCTRL`, `DM814_UART3_CLKCTRL`, `DM814_GPIO1_CLKCTRL`, `DM814_GPIO2_CLKCTRL`, `DM814_I2C1_CLKCTRL`, `DM814_I2C2_CLKCTRL`. File section comments identify domains such as `default clocks`, `alwon clocks`, `alwon_ethernet clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with TI clockctrl data and DTS module clock nodes where offsets select PRCM clock-control registers. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/dm814.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/dm816.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/dm816.h

## Purpose
`dm816.h` defines the device-tree clock binding ABI for TI DM816 clockctrl offsets for USB, UART, GPIO, I2C, timers, watchdog, SPI, mailbox, MMC, GPMC, MDIO, EMAC, and security modules. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLK_DM816_H`. The binding surface has 32 exported non-guard macros; macro families include DM816_CLKCTRL_OFFSET (1), DM816_CLKCTRL_INDEX (1), DM816_USB_OTG (1), DM816_UART1_CLKCTRL (1), DM816_UART2_CLKCTRL (1), DM816_UART3_CLKCTRL (1), DM816_GPIO1_CLKCTRL (1), DM816_GPIO2_CLKCTRL (1). Representative ids include `DM816_CLKCTRL_OFFSET`, `DM816_CLKCTRL_INDEX`, `DM816_USB_OTG_HS_CLKCTRL`, `DM816_UART1_CLKCTRL`, `DM816_UART2_CLKCTRL`, `DM816_UART3_CLKCTRL`, `DM816_GPIO1_CLKCTRL`, `DM816_GPIO2_CLKCTRL`, .... explicit numeric ids span 0..0 across 1 constants. Function-like helpers: `DM816_CLKCTRL_INDEX`. Expression/string-style macros to review include `DM816_USB_OTG_HS_CLKCTRL`, `DM816_UART1_CLKCTRL`, `DM816_UART2_CLKCTRL`, `DM816_UART3_CLKCTRL`, `DM816_GPIO1_CLKCTRL`, `DM816_GPIO2_CLKCTRL`, `DM816_I2C1_CLKCTRL`, `DM816_I2C2_CLKCTRL`. File section comments identify domains such as `default clocks`, `alwon clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with TI clockctrl data and DTS module clock nodes where offsets select PRCM clock-control registers. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/dm816.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/dra7.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/dra7.h

## Purpose
`dra7.h` defines the device-tree clock binding ABI for TI DRA7 clockctrl offsets across MPU, DSP, IPU, RTC, camera, VPE, core, L4, DSS, GPU, IVA, L3, and wakeup domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__DT_BINDINGS_CLK_DRA7_H`. The binding surface has 152 exported non-guard macros; macro families include DRA7_L3INIT_USB (4), DRA7_IPU_CLKCTRL (2), DRA7_VPE_CLKCTRL (2), DRA7_COREAON_SMARTREFLEX (2), DRA7_ATL_CLKCTRL (2), DRA7_L3INSTR_L3 (2), DRA7_PCIE_CLKCTRL (2), DRA7_GMAC_CLKCTRL (2). Representative ids include `DRA7_CLKCTRL_OFFSET`, `DRA7_CLKCTRL_INDEX`, `DRA7_MPU_MPU_CLKCTRL`, `DRA7_DSP1_MMU0_DSP1_CLKCTRL`, `DRA7_IPU1_MMU_IPU1_CLKCTRL`, `DRA7_IPU_CLKCTRL_OFFSET`, `DRA7_IPU_CLKCTRL_INDEX`, `DRA7_IPU_MCASP1_CLKCTRL`, .... explicit numeric ids span 0..416 across 10 constants. Function-like helpers: `DRA7_CLKCTRL_INDEX`, `DRA7_IPU_CLKCTRL_INDEX`, `DRA7_VPE_CLKCTRL_INDEX`, `DRA7_ATL_CLKCTRL_INDEX`, `DRA7_PCIE_CLKCTRL_INDEX`, `DRA7_GMAC_CLKCTRL_INDEX`, `DRA7_L4PER_CLKCTRL_INDEX`, `DRA7_L4SEC_CLKCTRL_INDEX`, `DRA7_L4PER2_CLKCTRL_INDEX`, `DRA7_L4PER3_CLKCTRL_INDEX`. Expression/string-style macros to review include `DRA7_MPU_MPU_CLKCTRL`, `DRA7_DSP1_MMU0_DSP1_CLKCTRL`, `DRA7_IPU1_MMU_IPU1_CLKCTRL`, `DRA7_IPU_MCASP1_CLKCTRL`, `DRA7_IPU_TIMER5_CLKCTRL`, `DRA7_IPU_TIMER6_CLKCTRL`, `DRA7_IPU_TIMER7_CLKCTRL`, `DRA7_IPU_TIMER8_CLKCTRL`. File section comments identify domains such as `mpu clocks`, `dsp1 clocks`, `ipu1 clocks`, `ipu clocks`, `dsp2 clocks`, `rtc clocks`, `vip clocks`, `vpe clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `DRA7_MPU_MPU_CLKCTRL`, `DRA7_DSP1_MMU0_DSP1_CLKCTRL`, `DRA7_IPU1_MMU_IPU1_CLKCTRL`, `DRA7_DSP2_MMU0_DSP2_CLKCTRL` share `DRA7_CLKCTRL_INDEX(0x20)`; `DRA7_CAM_VIP2_CLKCTRL`, `DRA7_COREAON_SMARTREFLEX_MPU_CLKCTRL`, `DRA7_L3MAIN1_GPMC_CLKCTRL`, `DRA7_L4CFG_SPINLOCK_CLKCTRL` share `DRA7_CLKCTRL_INDEX(0x28)`; `DRA7_CAM_VIP3_CLKCTRL`, `DRA7_L4CFG_MAILBOX1_CLKCTRL`, `DRA7_DSS_BB2D_CLKCTRL`, `DRA7_L3INIT_MMC2_CLKCTRL` share `DRA7_CLKCTRL_INDEX(0x30)`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with TI clockctrl data and DTS module clock nodes where offsets select PRCM clock-control registers. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/dra7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/econet,en751221-scu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/econet,en751221-scu.h

## Purpose
`econet,en751221-scu.h` defines the device-tree clock binding ABI for EcoNet EN751221 SCU clock ids for PCIe, SPI, bus, CPU, and GSW clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_ECONET_EN751221_SCU_H_`. The binding surface has 5 exported non-guard macros; macro families include EN751221_CLK_PCIE (1), EN751221_CLK_SPI (1), EN751221_CLK_BUS (1), EN751221_CLK_CPU (1), EN751221_CLK_GSW (1). Representative ids include `EN751221_CLK_PCIE`, `EN751221_CLK_SPI`, `EN751221_CLK_BUS`, `EN751221_CLK_CPU`, `EN751221_CLK_GSW`. explicit numeric ids span 0..4 across 5 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/econet,en751221-scu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/en7523-clk.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/en7523-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/eswin,eic7700-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/eswin,eic7700-clock.h

## Purpose
`eswin,eic7700-clock.h` defines the device-tree clock binding ABI for ESWIN EIC7700 clock ids for PLL roots, CPU/DSP/D2D, NoC, media, storage, NPU, peripheral, and always-on domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_ESWIN_EIC7700_CLOCK_H_`. The binding surface has 268 exported non-guard macros; macro families include EIC7700_CLK_GATE (159), EIC7700_CLK_DIV (52), EIC7700_CLK_MUX (28), EIC7700_CLK_FIXED (10), EIC7700_CLK_SPLL0 (3), EIC7700_CLK_SPLL1 (3), EIC7700_CLK_SPLL2 (3), EIC7700_CLK_VPLL (3). Representative ids include `EIC7700_CLK_XTAL_32K`, `EIC7700_CLK_PLL_CPU`, `EIC7700_CLK_SPLL0_FOUT1`, `EIC7700_CLK_SPLL0_FOUT2`, `EIC7700_CLK_SPLL0_FOUT3`, `EIC7700_CLK_SPLL1_FOUT1`, `EIC7700_CLK_SPLL1_FOUT2`, `EIC7700_CLK_SPLL1_FOUT3`, .... explicit numeric ids span 0..267 across 268 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/eswin,eic7700-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos-audss-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos-audss-clk.h

## Purpose
`exynos-audss-clk.h` defines the device-tree clock binding ABI for Samsung Exynos AUDSS clock ids for audio muxes, dividers, SRP/I2S/PCM clocks, ADMA, and max count. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLK_EXYNOS_AUDSS_H`. The binding surface has 12 exported non-guard macros; macro families include EXYNOS_MOUT_AUDSS (1), EXYNOS_MOUT_I2S (1), EXYNOS_DOUT_SRP (1), EXYNOS_DOUT_AUD (1), EXYNOS_DOUT_I2S (1), EXYNOS_SRP_CLK (1), EXYNOS_I2S_BUS (1), EXYNOS_SCLK_I2S (1). Representative ids include `EXYNOS_MOUT_AUDSS`, `EXYNOS_MOUT_I2S`, `EXYNOS_DOUT_SRP`, `EXYNOS_DOUT_AUD_BUS`, `EXYNOS_DOUT_I2S`, `EXYNOS_SRP_CLK`, `EXYNOS_I2S_BUS`, `EXYNOS_SCLK_I2S`, .... explicit numeric ids span 0..11 across 12 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos-audss-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos3250.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos3250.h

## Purpose
`exynos3250.h` defines the device-tree clock binding ABI for Samsung Exynos3250 CMU clock ids for PLLs, muxes, dividers, gates, UART/SPI/MMC, camera, display, ISP, and power domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_SAMSUNG_EXYNOS3250_CLOCK_H`. The binding surface has 282 exported non-guard macros; macro families include CLK_DIV (59), CLK_MOUT (52), CLK_SCLK (27), CLK_QE (10), CLK_SMMU (8), CLK_FOUT (6), CLK_ASYNC (6), CLK_BLOCK (4). Representative ids include `CLK_OSCSEL`, `CLK_FIN_PLL`, `CLK_FOUT_APLL`, `CLK_FOUT_VPLL`, `CLK_FOUT_UPLL`, `CLK_FOUT_MPLL`, `CLK_ARM_CLK`, `CLK_MOUT_MPLL_USER_L`, .... explicit numeric ids span 1..249 across 282 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `Muxes`, `Dividers`, `Gates`, `Special clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_OSCSEL`, `CLK_FOUT_BPLL`, `CLK_DIV_ISP1` share `1`; `CLK_FIN_PLL`, `CLK_FOUT_EPLL`, `CLK_DIV_ISP0` share `2`; `CLK_FOUT_APLL`, `CLK_DIV_MCUISP1` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos3250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos4.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5250.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5250.h

## Purpose
`exynos5250.h` defines the device-tree clock binding ABI for Samsung Exynos5250 CMU clock ids for PLLs, ARM, special clocks, gates, display, GSCL, MMC, SPI, audio, and peripheral blocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS_5250_H`. The binding surface has 160 exported non-guard macros; macro families include CLK_SCLK (30), CLK_SMMU (25), CLK_FOUT (7), CLK_MOUT (7), CLK_DIV (4), CLK_SATA (3), CLK_CMU (3), CLK_GSCL (2). Representative ids include `CLK_FIN_PLL`, `CLK_FOUT_APLL`, `CLK_FOUT_MPLL`, `CLK_FOUT_BPLL`, `CLK_FOUT_GPLL`, `CLK_FOUT_CPLL`, `CLK_FOUT_EPLL`, `CLK_FOUT_VPLL`, .... explicit numeric ids span 1..1030 across 160 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `core clocks`, `gate for special clocks (sclk)`, `gate clocks`, `mux clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5260-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5260-clk.h

## Purpose
`exynos5260-clk.h` defines the device-tree clock binding ABI for Samsung Exynos5260 multi-CMU clock ids grouped by top, PERI, EPLL, KFC, MIF, EGL, ISP, G2D, MFC, GSCL, FSYS, and display domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLK_EXYNOS5260_H`. The binding surface has 388 exported non-guard macros; macro families include TOP_DOUT_SCLK (28), TOP_DOUT_ACLK (20), TOP_MOUT_SCLK (19), DISP_MOUT_PHYCLK (11), TOP_MOUT_ACLK (9), GSCL_CLK_SMMU3 (7), PHYCLK_DPTX_PHY (6), ISP_CLK_SMMU (6). Representative ids include `TOP_FOUT_DISP_PLL`, `TOP_FOUT_AUD_PLL`, `TOP_MOUT_AUDTOP_PLL_USER`, `TOP_MOUT_AUD_PLL`, `TOP_MOUT_DISP_PLL`, `TOP_MOUT_BUSTOP_PLL_USER`, `TOP_MOUT_MEMTOP_PLL_USER`, `TOP_MOUT_MEDIATOP_PLL_USER`, .... explicit numeric ids span 1..124 across 388 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `Clock names: <cmu><type><IP>`, `List Of Clocks For CMU_TOP`, `List Of Clocks For CMU_EGL`, `List Of Clocks For CMU_KFC`, `List Of Clocks For CMU_MIF`, `List Of Clocks For CMU_G3D`, `List Of Clocks For CMU_AUD`, `List Of Clocks For CMU_MFC`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `TOP_FOUT_DISP_PLL`, `EGL_FOUT_EGL_PLL`, `KFC_FOUT_KFC_PLL`, `MIF_FOUT_MEM_PLL` share `1`; `TOP_FOUT_AUD_PLL`, `EGL_FOUT_EGL_DPLL`, `KFC_MOUT_KFC_PLL`, `MIF_FOUT_MEDIA_PLL` share `2`; `TOP_MOUT_AUDTOP_PLL_USER`, `EGL_MOUT_EGL_B`, `KFC_MOUT_KFC`, `MIF_FOUT_BUS_PLL` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5260-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5410.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5410.h

## Purpose
`exynos5410.h` defines the device-tree clock binding ABI for Samsung Exynos5410 clock ids for PLLs, UART/MMC/USB/PWM special clocks, peripheral gates, and display/media gates. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS_5410_H`. The binding surface has 46 exported non-guard macros; macro families include CLK_SCLK (12), CLK_FOUT (6), CLK_FIN (1), CLK_UART0 (1), CLK_UART1 (1), CLK_UART2 (1), CLK_UART3 (1), CLK_I2C0 (1). Representative ids include `CLK_FIN_PLL`, `CLK_FOUT_APLL`, `CLK_FOUT_CPLL`, `CLK_FOUT_MPLL`, `CLK_FOUT_BPLL`, `CLK_FOUT_KPLL`, `CLK_FOUT_EPLL`, `CLK_SCLK_UART0`, .... explicit numeric ids span 1..471 across 46 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `core clocks`, `gate for special clocks (sclk)`, `gate clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5420.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5420.h

## Purpose
`exynos5420.h` defines the device-tree clock binding ABI for Samsung Exynos5420 clock ids for PLLs, ARM/KFC, special clocks, display, MAU, filesystem, peripheral, GSCL, MSCL, and gate domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS_5420_H`. The binding surface has 251 exported non-guard macros; macro families include CLK_SCLK (41), CLK_DOUT (31), CLK_MOUT (27), CLK_SMMU (20), CLK_FOUT (11), CLK_ACLK (6), CLK_FIMC (4), CLK_PCLK (4). Representative ids include `CLK_FIN_PLL`, `CLK_FOUT_APLL`, `CLK_FOUT_CPLL`, `CLK_FOUT_DPLL`, `CLK_FOUT_EPLL`, `CLK_FOUT_RPLL`, `CLK_FOUT_IPLL`, `CLK_FOUT_SPLL`, .... explicit numeric ids span 1..799 across 251 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `core clocks`, `gate for special clocks (sclk)`, `gate clocks`, `mux clocks`, `divider clocks`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5420.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5433.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5433.h

## Purpose
`exynos5433.h` defines the device-tree clock binding ABI for Samsung Exynos5433 clock ids for many separate CMUs, including top, CPIF, MIF, PERIC, FSYS, display, audio, camera, ISP, GSCL, MFC, HEVC, and bus domains. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS5433_H`. The binding surface has 1274 exported non-guard macros; macro families include CLK_ACLK (399), CLK_PCLK (294), CLK_MOUT (203), CLK_DIV (162), CLK_SCLK (141), CLK_PHYCLK (41), CLK_FOUT (11), CLK_DOUT (4). Representative ids include `CLK_FOUT_ISP_PLL`, `CLK_FOUT_AUD_PLL`, `CLK_MOUT_AUD_PLL`, `CLK_MOUT_ISP_PLL`, `CLK_MOUT_AUD_PLL_USER_T`, `CLK_MOUT_MPHY_PLL_USER`, `CLK_MOUT_MFC_PLL_USER`, `CLK_MOUT_BUS_PLL_USER`, .... explicit numeric ids span 1..253 across 1271 constants. Function-like helpers: none. Expression/string-style macros to review include `CLK_MOUT_ACLK_BUS2_400_USER`, `CLK_ACLK_BUS2BEND_400`, `CLK_ACLK_BUS2RTND_400`. File section comments identify domains such as `CMU_TOP`, `CMU_CPIF`, `CMU_MIF`, `CMU_PERIC`, `CMU_PERIS`, `CMU_FSYS`, `CMU_G2D`, `CMU_DISP`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_FOUT_ISP_PLL`, `CLK_FOUT_MPHY_PLL`, `CLK_FOUT_MEM0_PLL`, `CLK_PCLK_SPI2` share `1`; `CLK_FOUT_AUD_PLL`, `CLK_MOUT_MPHY_PLL`, `CLK_FOUT_MEM1_PLL`, `CLK_PCLK_SPI1` share `2`; `CLK_MOUT_AUD_PLL`, `CLK_DIV_SCLK_MPHY`, `CLK_MOUT_MFC_PLL_DIV2`, `CLK_PCLK_HSI2C0` share `10`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos5433.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos7-clk.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos7-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos7885.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos7885.h

## Purpose
`exynos7885.h` defines the device-tree clock binding ABI for Samsung Exynos7885 clock ids for shared PLLs and CMU domains such as core, peripheral, top, CPUCL0/1, FSYS, G3D, MFC/MSCL, and display. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS_7885_H`. The binding surface has 138 exported non-guard macros; macro families include CLK_GOUT (66), CLK_MOUT (38), CLK_DOUT (25), CLK_FSYS (6), CLK_FOUT (3). Representative ids include `CLK_FOUT_SHARED0_PLL`, `CLK_FOUT_SHARED1_PLL`, `CLK_DOUT_SHARED0_DIV2`, `CLK_DOUT_SHARED0_DIV3`, `CLK_DOUT_SHARED0_DIV4`, `CLK_DOUT_SHARED0_DIV5`, `CLK_DOUT_SHARED1_DIV2`, `CLK_DOUT_SHARED1_DIV3`, .... explicit numeric ids span 1..62 across 138 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `CMU_TOP`, `CMU_CORE`, `CMU_PERI`, `CMU_FSYS`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_FOUT_SHARED0_PLL`, `CLK_MOUT_CORE_BUS_USER`, `CLK_MOUT_PERI_BUS_USER`, `CLK_MOUT_FSYS_BUS_USER` share `1`; `CLK_FOUT_SHARED1_PLL`, `CLK_MOUT_CORE_CCI_USER`, `CLK_MOUT_PERI_SPI0_USER`, `CLK_MOUT_FSYS_MMC_CARD_USER` share `2`; `CLK_DOUT_SHARED0_DIV2`, `CLK_MOUT_CORE_G3D_USER`, `CLK_MOUT_PERI_SPI1_USER`, `CLK_MOUT_FSYS_MMC_EMBD_USER` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos7885.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos850.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos850.h

## Purpose
`exynos850.h` defines the device-tree clock binding ABI for Samsung Exynos850 clock ids for shared/MMC PLLs and CMU domains such as core, DPU, HSI, PERI, CMGP, audio, HSI CMGP, and G3D. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_EXYNOS_850_H`. The binding surface has 357 exported non-guard macros; macro families include CLK_GOUT (171), CLK_MOUT (85), CLK_DOUT (78), CLK_FOUT (7), CLK_RCO (3), OSCCLK_RCO_APM (1), CLK_DLL (1), IOCLK_AUDIOCDCLK0 (1). Representative ids include `CLK_FOUT_SHARED0_PLL`, `CLK_FOUT_SHARED1_PLL`, `CLK_FOUT_MMC_PLL`, `CLK_MOUT_SHARED0_PLL`, `CLK_MOUT_SHARED1_PLL`, `CLK_MOUT_MMC_PLL`, `CLK_MOUT_CORE_BUS`, `CLK_MOUT_CORE_CCI`, .... explicit numeric ids span 1..90 across 357 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `CMU_TOP`, `CMU_APM`, `CMU_AUD`, `CMU_CMGP`, `CMU_CPUCL0`, `CMU_CPUCL1`, `CMU_G3D`, `CMU_HSI`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_FOUT_SHARED0_PLL`, `CLK_RCO_I3C_PMIC`, `CLK_DOUT_AUD_AUDIF`, `CLK_RCO_CMGP` share `1`; `CLK_FOUT_SHARED1_PLL`, `OSCCLK_RCO_APM`, `CLK_DOUT_AUD_BUSD`, `CLK_MOUT_CMGP_ADC` share `2`; `CLK_FOUT_MMC_PLL`, `CLK_RCO_APM__ALV`, `CLK_DOUT_AUD_BUSP`, `CLK_MOUT_CMGP_USI0` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/exynos850.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/fsd-clk.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/fsd-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/fsl,qoriq-clockgen.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/fsl,qoriq-clockgen.h

## Purpose
`fsl,qoriq-clockgen.h` defines the device-tree clock binding ABI for NXP/Freescale QorIQ clockgen ids and PLL divider helper macro. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_CLOCK_FSL_QORIQ_CLOCKGEN_H`. The binding surface has 7 exported non-guard macros; macro families include QORIQ_CLK_SYSCLK (1), QORIQ_CLK_CMUX (1), QORIQ_CLK_HWACCEL (1), QORIQ_CLK_FMAN (1), QORIQ_CLK_PLATFORM (1), QORIQ_CLK_CORECLK (1), QORIQ_CLK_PLL_DIV (1). Representative ids include `QORIQ_CLK_SYSCLK`, `QORIQ_CLK_CMUX`, `QORIQ_CLK_HWACCEL`, `QORIQ_CLK_FMAN`, `QORIQ_CLK_PLATFORM_PLL`, `QORIQ_CLK_CORECLK`, `QORIQ_CLK_PLL_DIV`. explicit numeric ids span 0..5 across 6 constants. Function-like helpers: `QORIQ_CLK_PLL_DIV`. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/fsl,qoriq-clockgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/g12a-aoclkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/g12a-aoclkc.h

## Purpose
`g12a-aoclkc.h` defines the device-tree clock binding ABI for Amlogic Meson G12A always-on clock controller ids for AO bus, IR, I2C, UART, SAR ADC, mailbox, M3/M4, CEC, and RTC clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `DT_BINDINGS_CLOCK_AMLOGIC_MESON_G12A_AOCLK`. The binding surface has 29 exported non-guard macros; macro families include CLKID_AO (29). Representative ids include `CLKID_AO_AHB`, `CLKID_AO_IR_IN`, `CLKID_AO_I2C_M0`, `CLKID_AO_I2C_S0`, `CLKID_AO_UART`, `CLKID_AO_PROD_I2C`, `CLKID_AO_UART2`, `CLKID_AO_IR_OUT`, .... explicit numeric ids span 0..28 across 29 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Amlogic Meson clock-controller drivers and DTS `clocks`/`assigned-clocks` specifiers for AO, audio, or main HIU domains. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/g12a-aoclkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/g12a-clkc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/g12a-clkc.h

## Purpose
`g12a-clkc.h` defines the device-tree clock binding ABI for Amlogic Meson G12A main clock tree ids for PLLs, muxes, dividers, gates, video, CPU, GPU, PCIe, SD/eMMC, USB, audio, and peripheral clocks. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `__G12A_CLKC_H`. The binding surface has 279 exported non-guard macros; macro families include CLKID (279). Representative ids include `CLKID_SYS_PLL`, `CLKID_FIXED_PLL`, `CLKID_FCLK_DIV2`, `CLKID_FCLK_DIV3`, `CLKID_FCLK_DIV4`, `CLKID_FCLK_DIV5`, `CLKID_FCLK_DIV7`, `CLKID_GP0_PLL`, .... explicit numeric ids span 0..278 across 279 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Amlogic Meson clock-controller drivers and DTS `clocks`/`assigned-clocks` specifiers for AO, audio, or main HIU domains. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/g12a-clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/google,gs101-acpm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/google,gs101-acpm.h

## Purpose
`google,gs101-acpm.h` defines the device-tree clock binding ABI for Google GS101 ACPM DVFS clock ids exposed through the ACPM clock controller. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_GOOGLE_GS101_ACPM_H`. The binding surface has 14 exported non-guard macros; macro families include GS101_CLK_ACPM (14). Representative ids include `GS101_CLK_ACPM_DVFS_MIF`, `GS101_CLK_ACPM_DVFS_INT`, `GS101_CLK_ACPM_DVFS_CPUCL0`, `GS101_CLK_ACPM_DVFS_CPUCL1`, `GS101_CLK_ACPM_DVFS_CPUCL2`, `GS101_CLK_ACPM_DVFS_G3D`, `GS101_CLK_ACPM_DVFS_G3DL2`, `GS101_CLK_ACPM_DVFS_TPU`, .... explicit numeric ids span 0..13 across 14 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as the file is organized primarily by macro naming rather than section comments.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. No obvious duplicate literal ids appear beyond any intentional gaps in the numbering.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/google,gs101-acpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/google,gs101.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/google,gs101.h

## Purpose
`google,gs101.h` defines the device-tree clock binding ABI for Google GS101 Samsung-style CMU clock ids for TOP plus many subsystem CMUs, including bus, CPU clusters, camera, display, TPU, G3D, HSI, PERIC, and media. It is a header-only contract: DTS files and clock-provider drivers share these names so that integer clock specifiers remain readable while compiled DTBs carry the numeric ids.

## Important APIs, types, and functions
The exported API is the macro namespace, not C functions or structs. The include guard is `_DT_BINDINGS_CLOCK_GOOGLE_GS101_H`. The binding surface has 639 exported non-guard macros; macro families include CLK_GOUT (418), CLK_MOUT (113), CLK_DOUT (99), CLK_FOUT (6), CLK_APM (3). Representative ids include `CLK_FOUT_SHARED0_PLL`, `CLK_FOUT_SHARED1_PLL`, `CLK_FOUT_SHARED2_PLL`, `CLK_FOUT_SHARED3_PLL`, `CLK_FOUT_SPARE_PLL`, `CLK_MOUT_PLL_SHARED0`, `CLK_MOUT_PLL_SHARED1`, `CLK_MOUT_PLL_SHARED2`, .... explicit numeric ids span 1..223 across 639 constants. Function-like helpers: none. Expression/string-style macros to review include none beyond literal ids. File section comments identify domains such as `CMU_TOP PLL`, `CMU_TOP MUX`, `CMU_TOP Dividers`, `CMU_TOP Gates`, `CMU_APM`, `CMU_DPU`, `CMU_HSI0`, `CMU_HSI2`.

## Control flow
There is no runtime control flow in this header. Build-time flow is the C preprocessor include guard followed by macro expansion in DTS preprocessing, clock-controller tables, and any driver code that includes the binding. Consumers pass these constants as clock specifier cells; the matching clock provider interprets the integer as an index into its registered clock data.

## State and persistence behavior
The file stores no runtime state and performs no persistence. Its numeric assignments are persistent ABI, because they are compiled into DTBs and must continue to match the provider's clock table across kernel updates. Repeated literal values are visible and should be treated as intentional aliases or independent per-domain namespaces: `CLK_FOUT_SHARED0_PLL`, `CLK_MOUT_APM_FUNC`, `CLK_MOUT_DPU_BUS_USER`, `CLK_FOUT_USB_PLL` share `1`; `CLK_FOUT_SHARED1_PLL`, `CLK_MOUT_APM_FUNCSRC`, `CLK_DOUT_DPU_BUSP`, `CLK_MOUT_PLL_USB` share `2`; `CLK_FOUT_SHARED2_PLL`, `CLK_DOUT_APM_BOOST`, `CLK_GOUT_DPU_PCLK`, `CLK_MOUT_HSI0_ALT_USER` share `3`.

## Dependencies and integration points
The header has no local include dependencies. It integrates with Samsung-style CMU/common-clock drivers and DTS clock specifiers where ids are grouped by clock management unit. Primary integration points are device-tree source includes, YAML binding examples using the same ids, provider arrays in `drivers/clk/`, and client nodes using `clocks`, `clock-names`, and `assigned-clocks`.

## Risks and edge cases
Renumbering or reusing an existing id can silently break old DTBs. Gaps, duplicate values, and expression-derived ids must be intentional and mirrored by provider tables. Large multi-domain headers are especially prone to off-by-one mistakes between comments, macro order, and driver arrays. String compatible macros, count macros, and helper macros need separate review from plain clock ids because they are consumed differently.

## Test signals
Useful signals are `dtbs_check` for bindings that include this header, full kernel builds of the matching clock provider, boot tests on boards that request representative clocks from each domain, and static cross-checks that every DTS-visible id maps to a provider entry. For edits, compare generated preprocessed DTS values before and after the change and add focused coverage for alias values, count macros, and the highest-numbered id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/google,gs101.h -->
