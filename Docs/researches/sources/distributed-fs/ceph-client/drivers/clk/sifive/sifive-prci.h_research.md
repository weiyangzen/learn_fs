# sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.h

Purpose: shared SiFive PRCI register map and driver-private interfaces.

Important APIs/types/functions: register offsets/masks for PLLs, muxes, PCIe AUX, reset, and mux status; `EXPECTED_CLK_PARENT_COUNT`; `PRCI_RST_NR`; `struct __prci_data`; `struct __prci_wrpll_data`; `struct __prci_clock`; `struct prci_clk_desc`; prototypes for mux helpers and CCF ops.

Control flow: no runtime implementation; common driver and FU540/FU740 descriptors share this contract.

State and persistence behavior: defines cached WRPLL config and per-device MMIO/reset/onecell storage structures.

Dependencies/integration points: WRPLL helper, CCF, reset-simple, platform devices, and DT binding descriptor headers.

Risks: register bitfields are shared across several PLL instances; HFPCLK macro naming appears inconsistent and needs compile coverage; reset count and bit positions are hardware ABI.

Test signals: compile both descriptor headers, boot both compatibles, validate reset IDs, and compare register offsets with hardware manuals.
