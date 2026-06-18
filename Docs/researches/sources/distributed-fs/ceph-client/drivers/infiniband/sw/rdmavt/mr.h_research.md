<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.h

## Purpose

Declares rdmavt memory-region wrappers and MR operation prototypes.

## Important APIs, Types, And Functions

`struct rvt_mr` wraps `struct ib_mr`, optional `struct ib_umem`, and trailing `struct rvt_mregion`. `to_imr()` converts an `ib_mr` to the wrapper. Prototypes expose driver MR init/exit, DMA MR, user MR registration, deregistration, fast-reg MR allocation, and scatterlist mapping.

## Control Flow

RDMA core calls the declared MR handlers through rdmavt device ops; QP paths use the resulting `rvt_mregion` state for SGE validation.

## State And Persistence Behavior

The wrapper persists for the MR lifetime. The `rvt_mregion` must be last, matching allocation patterns that include flexible map storage.

## Dependencies And Integration Points

Includes RDMA VT definitions and is paired with `mr.c`.

## Risks And Edge Cases

Changing struct layout can break assumptions in allocation and `container_of()` conversions. The header does not expose key-validation exports; those are declared in broader rdmavt public headers.

## Test Signals

Compile tests catch layout and signature drift; MR lifecycle tests validate wrapper conversion and cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mr.h -->
