<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mstar-msc313-mpll.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mstar-msc313-mpll.h

Purpose: Defines output indices for the MStar/SigmaStar MSC313 MPLL divider outputs.

Important APIs, types, and functions: Exports `MSTAR_MSC313_MPLL_DIV2`, `_DIV3`, `_DIV4`, `_DIV5`, `_DIV6`, `_DIV7`, and `_DIV10`. No functions, structs, or runtime macros exist.

Control flow: The header is declarative. The MPLL clock provider maps DT clock specifiers to the corresponding fixed-factor divider output.

State and persistence: Constants are stable DT ABI. PLL rate and divider behavior are implemented in provider code and hardware.

Dependencies and integration points: Used by MStar/SigmaStar DTS files and consumers that need a divided MPLL clock source.

Risks and test signals: Risks are limited but ABI-critical: the IDs begin at 1, so provider arrays must either reserve index 0 or translate explicitly. Test with DT binding checks, MPLL provider probe, clk summary rates for each divider, and peripheral consumers whose rates depend on divided MPLL outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mstar-msc313-mpll.h -->
