# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.h

## Purpose
Declares HINIC queue-pair constants, SQ doorbell bitfields, default SQ/RQ geometry, RX buffer size mapping, SQ/RQ/QP structures, and public queue-pair helper APIs for context setup and WQE manipulation.

## Important APIs, Types, and Functions
Important constants include `HINIC_SQ_WQEBB_SIZE`, `HINIC_RQ_WQEBB_SIZE`, 256 KiB SQ/RQ page sizes, 4K default depths, min/max queue depths, and `HINIC_RX_BUF_SZ`. Core structs are `hinic_sq`, `hinic_rq`, and `hinic_qp`. Public helpers prepare contexts, initialize/clean SQ/RQ, get free WQEBBs, set TX offload task fields, get/write/read/put SQ/RQ WQEs, extract SGEs, prepare RQ WQEs, and update RQ PI.

## Control Flow
The header has no direct flow. It defines the API used by IO creation and the upper NIC data path to manage WQEs and hardware queue contexts.

## State and Persistence Behavior
SQ/RQ structs store per-queue runtime state and pointers to hardware-visible coherent memory. Queue depth, page size, RX buffer size index, MSI-X entry, and doorbell fields are firmware/hardware contracts.

## Dependencies and Integration Points
Includes common HINIC definitions, HWIF, WQE, WQ, and QP context headers plus Linux SKB and PCI APIs. It bridges the hardware IO setup to packet TX/RX code.

## Risks
Changing queue geometry constants impacts firmware context layout, WQ allocation, and NIC buffer sizing. `HINIC_RX_BUF_SZ` and `HINIC_RX_BUF_SZ_IDX` must remain synchronized. Doorbell bitfields and offload task setters must match hardware WQE format.

## Test Signals
Compile coverage, queue create/destroy, firmware context setup, RX buffer-size negotiation, TX checksum/TSO field generation, doorbell writes, RX CQE handling, and queue depth boundary validation cover this header.
