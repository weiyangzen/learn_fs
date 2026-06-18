<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.h

## Purpose

Defines PVRDMA's verb-level ABI enums, attribute structs, and operation prototypes corresponding to RDMA core verbs.

## Important APIs, Types, And Functions

The header defines PVRDMA GIDs, link layers, MTUs, port states/capabilities/width/speed, port attributes, global routes, GRH, AH attributes, CQ notification flags, QP capabilities/types/create flags/attribute masks/states/migration states, SRQ attributes, QP attributes, send flags, access flags, and prototypes for all PVRDMA verbs handlers.

## Control Flow

Implementation files translate between RDMA core structs and these PVRDMA structs before sending commands to the device or interpreting responses. The prototypes are installed into `ib_device_ops` in `pvrdma_main.c`.

## State And Persistence Behavior

The header itself has no runtime state. Its structs define state persisted in command payloads, work queue entries, AVs, and query responses.

## Dependencies And Integration Points

Includes Linux types and is consumed by `pvrdma.h`, `pvrdma_dev_api.h`, and all verbs implementation files. It must stay aligned with the device backend ABI.

## Risks And Edge Cases

Many enums intentionally mirror RDMA core values. Any mismatch requires explicit conversion helpers; assuming 1:1 mapping where it no longer holds would corrupt commands or completions. Attribute masks cap accepted fields through `PVRDMA_QP_ATTR_MASK_MAX`.

## Test Signals

Compile-time size/layout assertions and runtime query/modify/post tests should validate enum translation, QP state/attribute masks, CQ notification flags, and access/send flag masking.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_verbs.h -->
