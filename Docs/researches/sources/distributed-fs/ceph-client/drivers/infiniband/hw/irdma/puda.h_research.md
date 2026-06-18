# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.h

## Purpose
This header defines the PUDA contract for ILQ and IEQ resources: resource types, completion milestones, completion/send descriptors, DMA buffer layout, resource configuration, runtime resource state, and external PUDA/IEQ entry points.

## Important APIs, Types, And Functions
- `enum puda_rsrc_type` distinguishes ILQ and IEQ resources; `enum puda_rsrc_complete` tracks creation milestones used by cleanup.
- `struct irdma_puda_cmpl_info` captures decoded CQE metadata, including QP id, WQE index, payload length, protocol flags, VLAN, source MAC, and error code.
- `struct irdma_puda_send_info` is the compact send descriptor consumed by `irdma_puda_send()`.
- `struct irdma_puda_buf` represents one DMA-backed packet buffer and carries parsed header pointers, payload length, VLAN/source MAC flags, AH id, sequence number, loopback flag, and list/refcount state.
- `struct irdma_puda_rsrc_info` is the create-time input, while `struct irdma_puda_rsrc` is the long-lived CQ/QP/buffer-pool/statistics object.
- Prototypes expose PUDA resource creation, destruction, send, CQ polling, buffer-pool operations, IEQ QP lookup, TCP/IP update/parsing, MPA CRC handling, AH lifecycle, and IEQ cleanup.

## Control Flow
The header has no executable flow, but it defines the data flow used by `puda.c`: callers fill `irdma_puda_rsrc_info`, `irdma_puda_create_rsrc()` allocates and initializes `irdma_puda_rsrc`, receive completions populate `irdma_puda_cmpl_info`, packet buffers move among `bufpool`, RQ, `txpend`, and IEQ partial lists, and `irdma_puda_send_info` is assembled from a buffer before WQE emission.

## State And Persistence
All state is runtime kernel memory. `irdma_puda_rsrc` persists for the VSI ILQ/IEQ lifetime and owns coherent CQ/QP memory, virtual bookkeeping memory, allocated buffer list, free and pending lists, queue indexes, callbacks, and stats. `irdma_puda_buf` persists until resource teardown and is recycled across receive and transmit operations.

## Dependencies And Integration Points
The header depends on Linux list and refcount primitives, DMA and virtual memory wrappers, Ethernet address sizing, and IRDMA SC types from neighboring headers. It is included by PUDA implementation and by connection-management/offload code that needs IEQ cleanup, AH construction, or PUDA sends.

## Risks And Edge Cases
The comment that `list` must be first in `irdma_puda_buf` is a real ABI-with-local-code constraint because list nodes are cast back to buffers. Mis-sizing `buf_size`, SQ/RQ counts, or callback pointers in `irdma_puda_rsrc_info` can break resource creation or packet processing. Counters are plain `u64` and mostly diagnostic, not synchronized accounting.

## Test Signals
Compile coverage should catch prototype drift. Runtime signals are successful ILQ/IEQ creation, nonzero buffer pool counts, correct callback dispatch, no list corruption under debug list/KASAN, and cleanup that frees all `alloc_buf_count` buffers.
