# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra20.c

## Purpose
This file provides the Tegra20 MC SoC descriptor plus Tegra20-specific reset, interconnect aggregation, interrupt handling, and debugfs statistics collection. It is used by the common MC platform driver to expose memory clients, reset controls, ICC nodes, error interrupts, and a `stats` debugfs seqfile.

## Important APIs, Types, And Functions
Important data includes `tegra20_mc_clients`, `tegra20_mc_resets`, `tegra20_mc_reset_ops`, `tegra20_mc_icc_ops`, `tegra20_mc_irq_handlers`, `tegra20_mc_intmasks`, and `tegra20_mc_soc`. Reset functions are `tegra20_mc_hotreset_assert()`, `tegra20_mc_hotreset_deassert()`, `tegra20_mc_block_dma()`, `tegra20_mc_dma_idling()`, `tegra20_mc_unblock_dma()`, and `tegra20_mc_reset_status()`. ICC functions are `tegra20_mc_of_icc_xlate_extended()`, `tegra20_mc_icc_aggreate()`, and `tegra20_mc_icc_set()`. Statistics functions build two hardware gatherers at a time and render per-client percentages in `tegra20_mc_stats_show()`.

## Control Flow
Common MC probe consumes `tegra20_mc_soc` and calls `tegra20_mc_probe()`, which adds the debugfs `stats` seqfile. Reset operations block DMA, poll idle status, assert/deassert hotreset, and unblock DMA by manipulating per-reset control/status/reset registers under `mc->lock`. ICC xlate finds the requested client node, tags display and VI clients as ISO, and aggregation scales ISO peak bandwidth by 300 percent before passing requests up the ICC graph. Interrupt handling masks `MC_INTSTATUS` by the SoC interrupt mask, decodes EMEM decode errors, invalid GART pages, and security violations, logs client/direction/address details, and clears handled bits.

## State And Persistence
Most state is hardware-resident: reset bits, DMA block bits, interrupt status, and MC statistics counters. `tegra20_mc_stat_lock` serializes debugfs statistics gathering globally. The stats path allocates a temporary per-client array per read and samples counters for `MC_STAT_SAMPLE_TIME_USEC`. ICC node data is allocated per translation. No file-local persistent device state exists beyond constant descriptors and the global mutex.

## Dependencies And Integration Points
The file depends on Tegra20 memory DT bindings, common `mc.h`, debugfs seqfile support, the interconnect framework, and common MC names/error strings from `mc.c`. The SoC descriptor advertises 32-bit addressing, `client_id_mask = 0x3f`, Tegra20 register layout, Tegra20 reset ops, and Tegra20 interrupt handlers. The EMC driver consumes the MC ICC aggregation behavior when creating EMC-side ICC routes.

## Risks
The stats collector assumes paired clients and writes directly to shared MC gather registers, so concurrent readers are serialized but other firmware/kernel users of those counters could interfere. Interrupt handling indexes `mc->soc->clients[id]` from hardware-reported IDs; bad IDs could overrun if hardware reports outside `client_id_mask` assumptions. Reset ops must match hardware polarity exactly or DMA may remain blocked or reset may be inverted. ICC `set` is intentionally a no-op, leaving arbitration defaults unchanged.

## Test Signals
Tests should cover reset consumers for AVPC/DC/DCB/EPP/2D/HC/ISP/MPCORE/MPE/3D/PPCS/VDE/VI, debugfs `stats` output under active memory traffic, MC error interrupt injection or fault generation for GART/security/EMEM decode, ICC path creation for display and VI as ISO, and suspend/resume behavior through the common MC layer. A useful regression signal is stable DMA after repeated reset assert/deassert cycles.
