# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ctl_defs.h

## Purpose
`cxgb3_ctl_defs.h` defines command IDs and payload structures for internal `cxgb3` offload control requests between upper-layer protocol drivers and the T3 low-level driver.

## Important APIs, Types, And Functions
- Command IDs cover adapter limits and resources (`GET_MAX_OUTSTANDING_WR`, `GET_TX_MAX_CHUNK`, TID/STID/RTBL ranges, L2T capacity, MTUs, WR length, MAC-to-interface lookup, DDP parameters, ports), iSCSI params, RDMA params/CQ/control-QP operations, offload page info, iSCSI IPv4 address, and embedded firmware/TP version info.
- `struct tid_range`, `mtutab`, `iff_mac`, `iscsi_ipv4addr`, `ddp_params`, `adap_ports`, `ulp_iscsi_info`, `rdma_info`, `rdma_cq_op`, `rdma_cq_setup`, `rdma_ctrlqp_setup`, `ofld_page_info`, and `ch_embedded_info` define typed request/response payloads.

## Control Flow And State
There is no executable flow. Upper-layer offload clients pass command IDs and matching structures to control dispatch code in `cxgb3_offload`/`t3cdev` paths. The low-level driver fills ranges, tables, PCI device pointers, doorbell addresses, memory windows, queue setup data, or protocol parameters.

## State And Persistence Behavior
The structures expose live adapter state rather than owning state. Returned pointers such as netdevs, PCI devices, MTU tables, and kernel doorbell addresses are borrowed from the adapter. RDMA/iSCSI setup structures can cause persistent hardware context programming when consumed by control handlers.

## Dependencies And Integration Points
The header forward-declares `net_device` and `pci_dev` and uses kernel integer types. It integrates `cxgb3` with iSCSI and RDMA upper layers, offload page allocation decisions, TID/STID allocation, L2 table sizing, and firmware/protocol version reporting.

## Risks And Edge Cases
The command enum and payload type must stay synchronized with dispatch code and upper-layer clients. Several structures contain raw pointers, so lifetime and context rules matter. Version or layout drift can break out-of-tree consumers. Resource ranges are half-open or capacity-based and require callers to validate bounds.

## Test Signals
Signals include offload control command tests for each enum path, iSCSI/RDMA bring-up, correct TID/STID/L2T/MTU/DDP values, CQ/control-QP setup success and teardown, and embedded firmware/TP version reporting.
