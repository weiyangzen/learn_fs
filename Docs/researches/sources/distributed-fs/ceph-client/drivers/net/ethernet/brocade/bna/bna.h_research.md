# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bna.h

## Purpose
`bna.h` is the central internal interface header for the BNA ethernet driver. It exposes queue arithmetic, DMA address conversion, RX mode state helpers, CAM list helpers, module accessors, and cross-module prototypes for BNA core, mailbox, IOCETH, ENET, ETHPORT, TX, RX, RXF, stats, and BNAD callback integration.

## Important APIs, Types, and Functions
- DMA conversion macros: `BNA_SET_DMA_ADDR()` and `BNA_GET_DMA_ADDR()`.
- Queue macros: `BNA_TXQ_WI_NEEDED()`, `BNA_QE_INDX_ADD()`, `BNA_QE_INDX_INC()`, `BNA_Q_INDEX_CHANGE()`, `BNA_QE_FREE_CNT()`, and `BNA_QE_IN_USE_CNT()`.
- Packet accounting: `BNA_UPDATE_PKT_CNT()`.
- Callback helpers for RXF start/stop/CAM filter completion.
- RX mode helpers for promisc, default, and allmulti enable/disable/inactive state using mode plus bitmask.
- `GET_RXQS()` maps RX path type to large/small/header/data RX queues.
- Resource-ID lookup macros `bna_tx_from_rid()` and `bna_rx_from_rid()`.
- CAM queue accessors and `bna_mac_find()`.
- Prototypes for exported internal APIs such as `bna_init()`, `bna_mod_init()`, `bna_enet_enable()`, `bna_ioceth_enable()`, TX/RX create/destroy/enable/disable/configure, and BNAD callbacks.

## Control Flow and State
The header shapes interactions between the core BNA object and submodules. BNAD calls BNA APIs to initialize resources, enable IOCETH/ENET, create TX/RX objects, adjust MTU and pause settings, set MAC/multicast/VLAN filters, and request stats. Firmware responses enter through `bna_mbox_handler()` and class-specific handlers declared here. TX/RX modules use resource-ID masks and active queues so ENET responses can be routed from firmware `enet_id` back to the right software object.

## State and Persistence Behavior
Most macros operate on state owned by `struct bna` and substructures declared in `bna_types.h`: queue indices, RID masks, RX mode bitmasks, CAM free/delete queues, callback slots, and DMA addresses. The header does not store state itself, but callers must maintain invariants such as stable list membership, valid RID values, and queue depths suitable for bitmask wrapping.

## Dependencies and Integration Points
The header includes `bfa_defs.h`, `bfa_ioc.h`, `bfi_enet.h`, and `bna_types.h`. It integrates the firmware ABI with Linux network-driver glue via BNAD callbacks and module APIs. `bna_enet.c` implements many prototypes in this header; TX/RX/RXF files implement the rest.

## Risks
- Queue index macros assume power-of-two depths.
- DMA conversion macros depend on struct layout casting through `struct bna_dma_addr`; changes to endian/layout would be risky.
- Callback helper macros clear callback fields before invocation, which prevents repeat calls but can hide reentrancy expectations.
- `bna_tx_from_rid()` and `bna_rx_from_rid()` perform linear list searches; stale or duplicate RIDs can misroute firmware responses.
- RX mode macros use separate `mode` and `bitmask` state; callers must keep both consistent.

## Test Signals
Signals include clean build coverage across all BNA modules, TX/RX response routing by RID, queue wrap/free/in-use calculations under boundary conditions, DMA address round-trips, RX mode transitions for promisc/default/allmulti, CAM allocation/free behavior, and BNAD callback invocation for enable, disable, link, stats, and cleanup flows.
