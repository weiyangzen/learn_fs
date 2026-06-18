# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264.c

Purpose: This file defines Tegra264 memory-controller topology, interconnect bandwidth handoff to BPMP, and custom fault interrupt decoding for MCF, hub, SBS, and channel interrupt sources. It exports `tegra264_mc_soc` for the shared Tegra MC driver.

Important APIs/types/functions: `tegra264_mc_clients` maps Tegra264 memory clients to BWMGR IDs and ICC traffic classes. `tegra264_mc_icc_set()` sends BPMP `MRQ_BWMGR_INT` calculate-and-set requests. `tegra264_mc_icc_aggregate()` sums average and maxes peak bandwidth. Fault handlers include `mcf_log_fault()`, `handle_mcf_irq()`, `hub_log_fault()`, `handle_hub_irq()`, hub-specific wrappers, `handle_generic_irq()`, `handle_sbs_irq()`, and `handle_channel_irq()`. `tegra264_mc_regs`, `tegra264_mc_intmasks`, and `tegra264_mc_irq_handlers` describe register layout, masks, priorities, and IRQ dispatch.

Control flow: ICC set calls follow the Tegra234-style BPMP path but use Tegra264 BWMGR IDs. MCF IRQ handling reads the broadcast common status, iterates active slices, decodes per-slice fault status/address/client/type, logs ratelimited errors, and clears slice interrupts. Hub IRQ handling reads a hubc global status, handles scrubber status, iterates hub interrupts, logs per-hub client/status/address, and clears hub/global status. SBS and channel handlers scan all MC channels for status and clear them.

State and persistence: The file is stateless beyond const tables. Runtime state lives in `struct tegra_mc`, hardware status registers, and BPMP firmware bandwidth state. IRQ handlers clear hardware-latched faults after logging.

Dependencies and integration: Depends on Tegra264 memory DT bindings, Tegra ICC, BPMP, `soc/tegra/mc.h`, shared `mc.h`, and `tegra264-bwmgr.h`. It integrates with shared Tegra186 MC ops and multi-interrupt MC registration.

Risks and test signals: Risks include wrong aperture mapping, status/address decoding, client ID masks, or failure to clear interrupts. Test signals include correct BPMP bandwidth votes, actionable MC fault logs with client/address/type, no IRQ storms after injected faults, and validation of hub/MC channel interrupt routing.
