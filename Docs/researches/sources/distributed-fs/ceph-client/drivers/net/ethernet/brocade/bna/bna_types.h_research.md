# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna_types.h

## Purpose
Defines the central BNA runtime object model for the BR-series Ethernet driver. It is the contract between low-level BNA control code, Linux-facing BNAD glue, firmware message handling, statistics, CAM managers, queue resources, and interrupt moderation.

## Important APIs, Types, and Functions
The header is type-only but critical. It defines status and resource enums (`bna_status`, `bna_cleanup_type`, `bna_cb_status`, `bna_res_type`, `bna_mem_type`, `bna_intr_type`), module resource IDs, Tx/Rx resource IDs, Tx/Rx/RxF FSM event enums, link/enet/ethport flags, RSS pending flags, packet-rate thresholds, and DIM load/bias categories.

Core structures include generic resource descriptors `bna_mem_descr`, `bna_mem_info`, `bna_intr_info`, and `bna_res_info`; firmware/hardware metadata `bna_attr`, `bna_ioceth`, `bna_enet`, and `bna_ethport`; interrupt block state `bna_ib`; Tx data path state `bna_tcb`, `bna_txq`, `bna_tx`, `bna_tx_config`, `bna_tx_event_cbfn`, and `bna_tx_mod`; Rx state `bna_rcb`, `bna_rxq`, `bna_ccb`, `bna_cq`, `bna_rx_config`, `bna_rxp`, `bna_rxf`, `bna_rx`, `bna_rx_event_cbfn`, and `bna_rx_mod`; CAM modules `bna_ucam_mod`, `bna_mcam_handle`, `bna_mcam_mod`; and aggregate state `struct bna`.

## Control Flow and State
There is no executable control flow, but the fields encode ownership and lifecycle. Control-plane objects carry FSM function pointers and callback pointers; data-path objects carry ring pointers, producer/consumer indices, interrupt vectors, doorbells, queue depth, DMA backing, and BNAD cookies. `bna_rxf` splits desired filter state into pending and active queues/bitmasks, while `bna_tx_mod` and `bna_rx_mod` own free/active queues and RID masks. `struct bna` aggregates IOC, CEE, flash, message queue, enet, ethport, stats, Tx/Rx modules, CAM modules, and BNAD backpointer.

## State and Persistence Behavior
State is volatile and driver-owned. Hardware-persistent concepts, such as firmware attributes, CAM handles, queue IDs, link status, pause, MTU, RSS tables, VLAN filters, and counters, are mirrored here only while the driver is loaded. The resource descriptors define allocation shape but not ownership lifetime by themselves; BNAD allocation/free routines fill and release them.

## Dependencies and Integration Points
Includes `cna.h`, `bna_hw_defs.h`, `bfa_cee.h`, and `bfa_msgq.h`, so it binds this Ethernet layer to common CNA/BFA firmware infrastructure and hardware register/message definitions. It is consumed by `bna_tx_rx.c`, `bnad.c`, `bnad.h`, ethtool/debugfs code, firmware callback dispatch, and the broader BNA modules for IOC/enet/stats.

## Risks and Test Signals
This file is an ABI-like internal layout. Risks are cacheline-sensitive data-path field drift, enum value changes breaking FSM dispatch or resource indexing, callback signature mismatch, resource index mismatch between request/allocation/create paths, and stats layout assumptions in ethtool. Test signals are allmodconfig builds, open/stop with all Rx path types, MSI-X and INTx operation, ethtool stats count/string alignment, and debug checks that `BNA_*_RES_T_MAX` arrays are fully populated before allocation.
