# sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.c

Purpose: platform driver for SiFive FU540/FU740 Power Reset Clock Interface blocks.

Important APIs/types/functions: MMIO helpers; WRPLL pack/unpack/read/write helpers; WRPLL rate ops; PLL enable/disable/is_enabled; TLCLK and HFPCLK recalc; core/corepll/hfpclk mux helper functions; PCIe AUX gate ops; `__prci_register_clocks()`; `sifive_prci_probe()`.

Control flow: probe selects a descriptor from OF match data, allocates per-device state, maps registers, registers an active-low simple reset controller, then registers clocks. Clock registration enforces exactly two parents, reads current WRPLL config, registers each `clk_hw`, and publishes a onecell provider. Rate changes compute WRPLL settings, optionally bypass, write config, and delay for lock.

State and persistence behavior: per-device MMIO/reset/onecell state; per-clock PRCI pointer and optional WRPLL cached config; actual enable/mux/reset state in hardware. No explicit PM save/restore.

Dependencies/integration points: Linux CCF, platform/OF APIs, reset-simple, Analog Bits WRPLL library, and FU540/FU740 descriptor headers.

Risks: strict parent count can fail probe on DT changes; mux helper writes are not locally locked; set-rate bypass sequencing must match active-clock expectations; reset and clock control share one block.

Test signals: probe on FU540/FU740 DTs, reset-controller consumer tests, WRPLL set/recalc, parent-count failure coverage, PCIe AUX toggling, and boot stability during core PLL changes.
