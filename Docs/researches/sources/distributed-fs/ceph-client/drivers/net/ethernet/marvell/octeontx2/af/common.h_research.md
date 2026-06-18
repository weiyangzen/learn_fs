# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/common.h

## Purpose
Provides shared RVU AF constants and helpers for queue memory allocation, admin queues, NPA aura sizing, NIX scheduler/link/action identifiers, packet size limits, channel numbering, RSS defaults, and NDC transaction constants.

## Important APIs, Types, and Functions
Queue sizing macros include `Q_SIZE_*`, `Q_COUNT`, `Q_SIZE`, `AQ_SIZE`, and `AQ_PTR_MASK`. `struct qmem` records DMA-backed queue memory; `qmem_alloc` and `qmem_free` allocate/free physically contiguous, 128-byte-aligned queue buffers. `struct admin_queue` groups instruction/result qmem and a lock. Other declarations include `enum npa_aura_sz`, `NPA_AURA_COUNT`, NPA AQ result wrappers, `enum nix_scheduler`, scheduler quantum defaults, link type constants, FRS limits, NIX RX/TX action opcodes, NIX interface/channel/link macros, LSO indexes, RSS constants, and NDC enums.

## Control Flow
`qmem_alloc` validates queue size, allocates metadata with devres, allocates contiguous DMA memory with alignment slop, adjusts CPU and IOVA pointers to a 128-byte boundary, and records the offset. `qmem_free` reverses the alignment adjustment before freeing DMA memory and metadata.

## State and Persistence Behavior
`qmem` allocations persist for admin or hardware queue lifetime and expose stable DMA IOVA addresses. Constants determine ring depths, scheduler hierarchy, MCAM actions, physical link/channel numbering, RSS context limits, and packet length constraints.

## Dependencies and Integration Points
Includes `rvu_struct.h` and is included by `mbox.h` and AF implementation files for NPA, NIX, NPC, scheduler, and mailbox configuration. It depends on device-managed allocation, DMA APIs, `ilog2`, alignment helpers, and fixed-width types.

## Risks
`qmem_alloc` mutates `qmem->base`; every free path must subtract `qmem->align`. `aligned_addr` is an `int` despite storing an aligned DMA address expression. Queue-size macros assume power-of-four growth from 16 entries, and channel/link constants must match hardware/firmware conventions.

## Test Signals
Admin queue allocation/free during probe/remove and failure injection, DMA API debug, alignment checks, NPA/NIX AQ operations, queue-size boundary tests, RSS group allocation, LSO format programming, link/channel mapping, and frame-size configuration tests.
