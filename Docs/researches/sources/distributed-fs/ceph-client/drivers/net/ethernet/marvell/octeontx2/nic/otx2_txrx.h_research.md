# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.h

## Purpose
`otx2_txrx.h` declares the data-path queue model and packet-buffer sizing constants for the RVU NIC. It is the shared interface between queue setup, TX/RX processing, XDP/XSK, QoS send queues, and representor/VF data paths.

## Important APIs, Types, and Definitions
Constants describe channel bases, alignment/headroom, Ethernet/MTU limits, page-pool sizing, GSO/fragment limits, CQ interrupt thresholds, CQ status bits, and `OTX2_RX_MATCH_ID_MASK`. Data types include `queue_stats`, `otx2_rcv_queue`, `sg_list`, `otx2_snd_queue`, `cq_type`, `otx2_cq_poll`, `otx2_pool`, `otx2_cq_queue`, and `otx2_qset`. The inline `otx2_iova_to_phys()` abstracts IOMMU translation. Prototypes expose NAPI, TX append/flush, and pool refill functions.

## Control Flow
The header itself has only the IOVA translation inline. Its structures define control flow used by the implementation: CINTs map to up to RX, TX, XDP, and QoS CQs; CQ queues point to receive pools; SQs hold descriptor memory, LMT addresses, SG tracking, timestamp memory, optional IPsec queues, and XSK pools.

## State and Persistence
All queue state is runtime-only and tied to device open/resource allocation. Persistent state across packets includes SQ/CQ indices, queue memory pointers, page-pool and XSK pool associations, refill scheduling flags, and per-queue stats.

## Dependencies and Integration Points
The header includes kernel Ethernet, IOMMU, VLAN, XDP, and XSK APIs. It is included by `otx2_txrx.c`, `otx2_xsk.c`, `qos_sq.c`, `rep.h`, and common setup code that allocates or configures qsets.

## Risks and Edge Cases
The queue structures are cacheline-aligned and shared with hot paths, so field changes can affect performance and races. `OTX2_MAX_CQ_CNT` and `CQS_PER_CINT` constrain representor and QoS queue mapping. Buffer sizing macros must leave enough headroom for XDP metadata, skb shared info, timestamps, and MTU changes.

## Test Signals
Compile all users after structure changes. Runtime tests should validate queue counts, CINT-to-CQ mapping, RX buffer sizing for MTU and XDP limits, IOMMU and non-IOMMU DMA translation, XSK pool attachment, and per-queue stats under multi-queue traffic.
