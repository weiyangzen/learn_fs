# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.h

## Purpose
`enic_wq.h` declares the ENIC transmit completion helper APIs.

## Important APIs, types, and functions
- `enic_free_wq_buf()` releases a single WQ buffer's DMA mapping and SKB ownership.
- `enic_wq_cq_service()` services TX completions for a CQ and budget.

## Control flow and state
The header carries no logic. Callers pass ENIC and WQ objects whose runtime state is mutated by the implementation.

## Dependencies and integration points
This header is used by ENIC TX setup/cleanup and completion code. It assumes `struct enic`, `struct vnic_wq`, and `struct vnic_wq_buf` are available from included ENIC headers.

## Risks and test signals
The header's main risks are declaration drift and missing includes. Build coverage and TX completion path tests cover it indirectly.
