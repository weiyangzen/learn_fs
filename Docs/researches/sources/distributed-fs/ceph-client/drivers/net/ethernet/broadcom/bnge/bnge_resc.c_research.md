# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.c

## Purpose
This file calculates and reserves hardware resources for the `bnge` function. It balances RX rings, TX rings, completion rings, NQs/MSI-X vectors, VNICs, RSS contexts, stat contexts, and auxiliary RoCE reservations against firmware-reported maxima.

## Important APIs, Types, And Functions
Public functions are `bnge_aux_has_enough_resources`, `bnge_fix_rings_count`, `bnge_cal_nr_rss_ctxs`, `bnge_get_rxfh_indir_size`, `bnge_reserve_rings`, `bnge_alloc_irqs`, `bnge_free_irqs`, `bnge_net_init_dflt_config`, `bnge_net_uninit_dflt_config`, and `bnge_aux_init_dflt_config`. Internal helpers convert TX rings to completion demand, compute max/default rings, reserve auxiliary MSI-X/stat contexts, initialize RSS indirection, and trim shared rings.

## Control Flow
Default configuration allocates the RSS indirection table, computes default shared RX/TX/NQ counts from CPU/RSS defaults and firmware maxima, reserves rings through HWRM, and stores filter capacity. Before open, `bnge_reserve_rings` recalculates demand, asks firmware to reserve resources, copies actual reservations back, reduces local ring counts if necessary, updates NQ/stat counts, and refreshes RSS indirection when RX reservation changed. IRQ allocation then asks PCI for MSI-X vectors and readjusts ring counts to available vectors.

## State And Persistence
The file mutates `bd->rx_nr_rings`, `bd->tx_nr_rings`, `bd->tx_nr_rings_per_tc`, `bd->nq_nr_rings`, `bd->aux_num_msix`, `bd->aux_num_stat_ctxs`, `bd->irq_tbl`, `bd->irqs_acquired`, `bd->rss_indir_tbl`, and `bd->hw_resc` reservations. These values persist as the sizing basis for netdev allocation and firmware object creation.

## Dependencies And Integration Points
It depends on HWRM resource wrappers, PCI MSI-X allocation, ethtool RSS default helper, RoCE capability flags, and ring constants from `bnge_netdev.h` and `bnge_resc.h`.

## Risks
Resource math has many coupled dimensions. Shared-channel mode and multi-TC TX mapping can make TX rings and completion rings differ. RoCE reservations reduce L2 capacity. Unsigned arithmetic around available IRQs/stat contexts must avoid underflow when maxima are below current demand.

## Test Signals
Probe on systems with few and many MSI-X vectors, shared and non-shared channels, RoCE enabled/disabled, CPU-count variation, firmware resource reductions, and repeated reserve/open paths. Validate queue counts, RSS indirection size, and no open failure after reductions.
