# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.h

## Purpose
`nicvf_queues.h` is the public queue ABI for the ThunderX VF driver. It defines per-queue limits, default ring sizes, interrupt vector ranges, descriptor alignment requirements, queue reset/enable bits, receive/transmit error enumerations, queue state structures, descriptor access macros, and prototypes shared between `nicvf_main.c`, `nicvf_queues.c`, and related ethtool/stat paths.

## Important APIs, Types, and Constants
The header defines queue topology constants such as `MAX_RCV_QUEUES_PER_QS`, `MAX_SND_QUEUES_PER_QS`, `MAX_CMP_QUEUES_PER_QS`, interrupt ids `NICVF_INTR_ID_*`, default lengths `SND_QUEUE_LEN`, `CMP_QUEUE_LEN`, `RCV_BUF_COUNT`, thresholds for CQ/RBDR backpressure/drop, and descriptor sizes/alignment. Core structures include `q_desc_mem`, `pgcache`, `rbdr`, `rcv_queue`, `cmp_queue`, `snd_queue`, and `queue_set`. Access macros `GET_RBDR_DESC`, `GET_SQ_DESC`, and `GET_CQ_DESC` encapsulate descriptor indexing.

## Control Flow and Integration
The header does not execute control flow, but it encodes invariants assumed by the C files: one default RBDR per queue set, up to eight RQ/SQ/CQ entries per queue set, CQ/SQ interrupt vector ranges, ring lengths as power-of-two masks, receive buffer length calculation including `skb_shared_info`, and CQ/RBDR drop thresholds sized to protect transmit CQE space. Its prototypes expose queue setup, data transfer, interrupt control, RX/TX descriptor handling, and stats/error accounting to the rest of the driver.

## State and Persistence
All state described here is in-memory runtime state. Descriptor memory metadata records DMA handles and aligned base addresses. RBDR state tracks page recycling and buffer ring progress. RQ/SQ/CQ structures track enable flags, routing to completion queues, thresholds, ring pointers, SKB/XDP page backpointers, TSO header DMA storage, locks, and per-queue counters. None of this is persisted across driver reloads.

## Dependencies and Risks
The header depends on Linux netdevice, IOMMU, XDP, and `q_struct.h`. Risks are mostly contract risks: changing queue sizes or threshold values can break hardware assumptions; changing struct layout can affect cacheline behavior; `nicvf_iova_to_phys` assumes identity mapping without an IOMMU domain; and descriptor access macros rely on correct ring descriptor type and q_len masking by callers.

## Test Signals
Compile coverage across endian modes and XDP-enabled kernels is important. Runtime signals include successful queue allocation/open, RX/TX across all queues, interrupt vector naming/affinity, XDP RXQ registration, CQ error recovery, stats reads, and validation that queue length/threshold changes remain accepted by hardware.
