# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.h

## Purpose
This header defines the netdev-facing data model for the `bnge` driver: TX/RX descriptors, completions, software buffer tracking, ring groups, stats memory, NAPI/NQ/CP/RX/TX ring structures, VNIC/filter state, netdev private state, constants, doorbell helpers, and exported netdev helper prototypes.

## Important APIs, Types, And Functions
Core types include `tx_bd`, `rx_bd`, `tx_cmp`, `bnge_sw_tx_bd`, `bnge_sw_rx_bd`, `bnge_sw_rx_agg_bd`, `bnge_ring_grp_info`, `bnge_tpa_info`, `bnge_stats_mem`, `bnge_net`, `bnge_cp_ring_info`, `bnge_nq_ring_info`, `bnge_rx_ring_info`, `bnge_tx_ring_info`, `bnge_napi`, `bnge_vnic_info`, `bnge_filter_base`, `bnge_l2_key`, and `bnge_l2_filter`. Important macros define descriptor counts, ring indexing, completion indexing, stats offsets, queue/TPA limits, NQ handle layout, and doorbell writes.

## Control Flow
The header is passive, but its structures encode runtime control flow. NQ rings own completion rings; completion rings point back to NAPI; RX/TX rings point to their completion ring and doorbell; VNICs point to RSS/filter DMA tables; `bnge_net` ties those pieces to timers, workqueues, feature flags, and stats.

## State And Persistence
Most fields are runtime state allocated on netdev open and freed on close. Persistent across open/close are netdev-level settings such as ring sizes, RSS key validity, previous stats, feature flags, timer/workqueue state, and ethtool link request state. Firmware IDs are invalidated and recreated per open.

## Dependencies And Integration Points
It includes HSI definitions, doorbell definitions, descriptor helpers, and link state. It is consumed by netdev, TX/RX datapath, HWRM command wrappers, resource reservation, and ethtool code.

## Risks
The data model is tightly coupled to queue counts and page-size-derived ring sizes. Incorrect masks or page counts can corrupt ring indexing. `bnge_net` combines many ownership domains, so lifecycle mistakes can become use-after-free across NAPI, IRQ, workqueue, timer, or firmware cleanup paths.

## Test Signals
Compile-time layout use, queue-count changes, RSS table sizing, XDP/page_pool-style RX recycling signals, TPA aggregation, TX completion, NAPI polling, and stat ops are the key coverage areas.
