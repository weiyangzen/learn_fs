# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra234.c

Purpose: This file provides the Tegra234 memory-controller SoC descriptor and bandwidth-management interconnect callbacks. It maps memory clients to BPMP bandwidth-manager IDs, Stream IDs, security/override registers, client traffic classes, interrupt masks, and the exported `tegra234_mc_soc`.

Important APIs/types/functions: `tegra234_mc_clients` is the central client table. `tegra234_mc_icc_set()` packages ICC bandwidth requests into `MRQ_BWMGR_INT` BPMP messages using `CMD_BWMGR_INT_CALC_AND_SET`, selecting ISO or NISO bandwidth by client type and passing peak bandwidth as the MC floor. `tegra234_mc_icc_aggregate()` sums average bandwidth and keeps maximum peak bandwidth, multiplying CPU-cluster peak requests by channel count. `tegra234_mc_icc_get_init_bw()` initializes ICC nodes to zero. `tegra234_mc_icc_ops`, `tegra234_mc_intmasks`, and `tegra234_mc_soc` connect these callbacks to shared MC code.

Control flow: Common Tegra MC registration consumes `tegra234_mc_soc`. ICC `set_bw` calls reach `tegra234_mc_icc_set()`, which skips self-links, no-ops if BPMP BWMGR is unsupported, validates BPMP availability, sends an MRQ, and converts BPMP failures into kernel errors. Interrupt handling uses common Tegra30 handlers with Tegra234 masks and register layout.

State and persistence: The file keeps only immutable tables. Dynamic state is in `struct tegra_mc`, BPMP firmware, ICC nodes, and hardware registers. Bandwidth decisions persist in BPMP/MC state until updated.

Dependencies and integration: Depends on Tegra234 DT bindings, Linux ICC, `linux/tegra-icc.h`, BPMP MRQ definitions, `soc/tegra/mc.h`, and shared `mc.h`. Integration points include BPMP firmware, memory-client SID programming, carveout handling, MC fault IRQs, and the interconnect framework.

Risks and test signals: Risks include stale BPMP IDs, incorrect client type classification, CPU cluster channel scaling mistakes, and unavailable BPMP references. Test signals include successful ICC path setup, BPMP bandwidth MRQs without `rx.ret` failures, working DMA isolation for SIDs, and correct reporting of MC decode/security/carveout faults.
