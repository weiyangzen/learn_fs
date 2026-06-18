
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.h

## Purpose
`hinic3_rx.h` defines RX CQE/WQE formats, CQE bitfield helpers, RX queue state, dynamic RX resources, and public RX lifecycle/polling functions for hinic3.

## Important APIs, Types, And Functions
- `RQ_CQE_OFFOLAD_TYPE_*`, `RQ_CQE_SGE_*`, and `RQ_CQE_STATUS_*` masks decode CQE packet type, IP type, tunnel format, VLAN enable, length, checksum error, LRO count, and RX done state.
- `struct hinic3_rxq_stats` stores per-RXQ counters with `u64_stats_sync`.
- `struct hinic3_rq_cqe` is the hardware completion format.
- `struct hinic3_rq_wqe` contains buffer and CQE DMA addresses posted to hardware.
- `struct hinic3_rx_info` tracks one page-pool page and offset.
- `struct hinic3_rxq` is the live RX queue object.
- `struct hinic3_dyna_rxq_res` carries dynamic resources before they are attached to a live RXQ.

## Control Flow
The header supports allocation/configuration code in `hinic3_rx.c`: dynamic resources are filled first, then copied into `hinic3_rxq`; polling decodes CQEs with the macros and updates the queue indices.

## State And Persistence Behavior
`struct hinic3_rxq` holds all active RX queue state and references DMA/coherent/page-pool resources owned by queue lifecycle code. It persists only while the netdev queue configuration is active.

## Dependencies And Integration Points
It includes bitfield, DIM, and netdevice headers and references `struct hinic3_io_queue`, `struct hinic3_irq_cfg`, and page-pool objects used by NIC device and interrupt code.

## Risks And Edge Cases
- The misspelled `OFFOLAD` macro names are part of local API; renaming requires touching all users.
- Field widths in macros must match firmware CQE layout.
- `q_mask` assumes power-of-two depth.
- `dev` is documented as the device for DMA mapping but the implementation primarily uses the page pool and PCI device for coherent CQE allocation.

## Test Signals
Compile-time coverage of CQE field users, runtime CQE decode validation, and queue stats consistency under RX traffic are useful signals.
