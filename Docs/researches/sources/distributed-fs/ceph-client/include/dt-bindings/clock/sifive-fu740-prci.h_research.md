# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu740-prci.h

## Purpose
`sifive-fu740-prci.h` defines PRCI clock indexes for the SiFive FU740 SoC.

## Important APIs, types, and functions
The header exports `FU740_PRCI_CLK_COREPLL`, `DDRPLL`, `GEMGXLPLL`, `DVFSCOREPLL`, `HFPCLKPLL`, `CLTXPLL`, `TLCLK`, `PCLK`, and `PCIE_AUX`. These IDs cover CPU, DDR, Ethernet, DVFS, high-frequency peripheral, cluster/TileLink, peripheral bus, and PCIe auxiliary clocks.

## Control flow
The constants are used in DT clock phandles. Runtime operations are handled by the FU740 PRCI driver, which maps IDs to PRCI PLL or derived clock registers.

## State and persistence
The header has no state. PRCI register settings and firmware initialization determine runtime clock rates and persistence across resets or low-power states.

## Dependencies and integration points
It integrates with FU740 DTS, SiFive PRCI support, CPU DVFS, DDR, Ethernet, PCIe, peripheral bus devices, and platform firmware assumptions.

## Risks and test signals
Risks include wrong clock ID for PCIe or peripheral bus consumers, unstable ABI numbering, and rate-change conflicts with firmware. Test signals include PRCI registration, CPU DVFS behavior, DDR stability, Ethernet and PCIe bring-up, and clk-summary rate consistency.
