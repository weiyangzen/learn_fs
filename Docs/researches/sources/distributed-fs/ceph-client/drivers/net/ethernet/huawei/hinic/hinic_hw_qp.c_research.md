# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_qp.c

## Purpose
Implements HINIC send and receive queue-pair primitives. It prepares firmware SQ/RQ contexts, initializes per-queue software resources, builds TX and RX WQEs, handles queue doorbells, tracks SKBs by WQE index, manages receive CQEs and producer-index DMA memory, and exposes helpers used by the upper NIC TX/RX path.

## Important APIs, Types, and Functions
Public APIs include context builders `hinic_qp_prepare_header`, `hinic_sq_prepare_ctxt`, `hinic_rq_prepare_ctxt`, SQ/RQ init/clean, free-space queries, TX offload task setters, WQE prepare/get/write/read/put helpers, SGE extraction, RQ WQE prepare/read/update helpers, and SQ doorbell writing. Important internals allocate `saved_skb` arrays, RQ CQEs, and RQ PI coherent memory.

## Control Flow
SQ/RQ initialization attaches HWIF/WQ/MSI-X state, sets queue ids and doorbells, and allocates saved-SKB arrays; RQ additionally allocates one coherent CQE per descriptor and a coherent PI word. Context builders read WQ first page PFNs and block PFNs, encode queue ids, CI/PI, prefetch values, interrupt ids, CQE addresses, and endianness for firmware. TX flow gets a WQE, prepares control/task/buffer descriptors, writes the WQE big-endian into the work queue, stores the SKB, and rings the SQ doorbell. RX flow prepares WQEs with buffer SGEs and CQE SGEs, updates PI memory, reads CQE `RXDONE`, retrieves the saved SKB and SGE length, clears done, and returns the WQE.

## State and Persistence Behavior
`hinic_sq` persists WQ pointer, qid, IRQ/MSI-X entry, hardware CI coherent address, doorbell base, and saved SKBs. `hinic_rq` persists WQ pointer, qid, affinity mask, IRQ/MSI-X entry, buffer size, saved SKBs, coherent CQEs, and coherent PI address. Firmware-visible state includes SQ/RQ contexts, WQ pages, CQE DMA addresses, SQ doorbells, and RQ PI memory.

## Dependencies and Integration Points
Depends on HINIC common/WQE/WQ/QP-context definitions, PCI DMA APIs, SKBs, and the IO layer. Upper NIC TX/RX code uses these helpers to enqueue packets and harvest completions.

## Risks
Saved SKB indexing assumes masked producer/consumer indices match WQ allocation. RQ allocates one coherent CQE object per descriptor, which is simple but memory intensive. Endian conversion must be applied exactly once when writing WQEs and reading SGEs/CQEs. `hinic_sq_read_wqe` does not check `IS_ERR` before dereferencing, so callers must only read when a completion is available. Doorbell writes require memory barriers before notifying hardware.

## Test Signals
TX/RX queue init/clean, descriptor allocation failures, TX WQE size variants, checksum and TSO task-field setup, SQ doorbells, RQ CQE RXDONE handling, RQ PI update, SKB recovery on TX/RX completion, endian validation, and queue wraparound are important tests.
