# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-pll.h

## Purpose
`sophgo,sg2042-pll.h` defines the PLL clock IDs for the Sophgo SG2042 PLL provider.

## Important APIs, types, and functions
The complete API is `MPLL_CLK`, `FPLL_CLK`, `DPLL0_CLK`, and `DPLL1_CLK`. There are no functions or structs.

## Control flow
DTS clock specifiers select one of these PLL outputs. The SG2042 PLL driver exposes the selected PLL to downstream clkgen or device consumers.

## State and persistence
The header is stateless. PLL frequency and lock state are held in hardware registers and may be initialized by firmware.

## Dependencies and integration points
It integrates with SG2042 DTS, the Sophgo PLL driver, the SG2042 clkgen provider, CPU, fabric, DDR, and peripheral clock trees that consume PLL roots.

## Risks and test signals
Risks include swapped PLL IDs, unsafe rate changes to shared roots, and firmware/kernel disagreement on PLL configuration. Test signals include PLL provider probe, clock summary root rates, stable CPU/DDR operation, and downstream clkgen consumers receiving expected parent rates.
