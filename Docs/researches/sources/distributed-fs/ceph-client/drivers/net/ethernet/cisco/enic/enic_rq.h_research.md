# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_rq.h

## Purpose
`enic_rq.h` is the small public header for ENIC receive-queue service routines.

## Important APIs, types, and functions
- `enic_rq_cq_service()` polls receive completions for a CQ and budget.
- `enic_rq_alloc_buf()` refills one receive descriptor.
- `enic_free_rq_buf()` releases an RQ buffer page.

## Control flow and state
The header only declares entry points. State is carried by `struct enic`, `struct vnic_rq`, and `struct vnic_rq_buf` supplied by callers and defined elsewhere.

## Dependencies and integration points
Consumers are ENIC open/NAPI/refill paths that need RX service and cleanup callbacks. It relies on declarations of `struct enic`, `struct vnic_rq`, and `struct vnic_rq_buf` being visible through surrounding includes.

## Risks and test signals
Risk is minimal in the header itself; ABI drift between declarations and implementation would break builds. Compile coverage and RX NAPI functional tests are the main signals.
