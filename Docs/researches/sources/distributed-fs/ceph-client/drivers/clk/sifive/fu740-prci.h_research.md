# sources/distributed-fs/ceph-client/drivers/clk/sifive/fu740-prci.h

Purpose: FU740 PRCI descriptor table with expanded PLL and auxiliary clock coverage.

Important APIs/types/functions: WRPLL metadata for core, DDR, GEMGXL, DVFS core, HFPCLK, and CLTX PLLs; ops for programmable/read-only WRPLL, TLCLK, HFPCLK divider, and PCIe AUX; `__prci_init_clocks_fu740[]`; `prci_clk_fu740`.

Control flow: selected by `"sifive,fu740-c000-prci"` OF match; common registration wires each descriptor to PRCI MMIO state and exposes onecell clocks.

State and persistence behavior: static descriptors plus cached WRPLL configs; PCIe AUX state remains in hardware enable bit.

Dependencies/integration points: FU740 binding IDs, common PRCI functions, WRPLL helper, and PCIe consumers of `pcie_aux`.

Risks: more bypass mux layers increase sequencing risk; `pclk` depends on HFPCLK divider; parent names and array indices are ABI-sensitive.

Test signals: FU740 boot/probe, all nine clocks present, WRPLL rate changes, HFPCLK-derived PCLK rate, and PCIe AUX enable/disable.
