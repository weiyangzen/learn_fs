<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.h

## Purpose

Declares rdmavt address-handle operation functions.

## Important APIs, Types, And Functions

Prototypes cover `rvt_create_ah()`, `rvt_destroy_ah()`, `rvt_modify_ah()`, and `rvt_query_ah()`.

## Control Flow

The functions are installed into RDMA device ops by rdmavt core users and implemented in `ah.c`.

## State And Persistence Behavior

No state is defined here; AH state is in rdmavt core structs from `<rdma/rdma_vt.h>`.

## Dependencies And Integration Points

Includes RDMA VT public definitions and is included by rdmavt core registration code.

## Risks And Edge Cases

Prototype changes must match RDMA core operation signatures.

## Test Signals

Compile coverage catches signature drift between header, implementation, and device-op registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/ah.h -->
