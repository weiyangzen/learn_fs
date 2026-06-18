# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uda_d.h

## Purpose
This header defines UDA hardware descriptor bit constants for SQ WQEs, UDA QP context fields, Manage Address Vector CQP WQEs, multicast group context/WQEs, and qhash programming.

## Important APIs, Types, And Functions
- L4 and inner IP packet type constants define values used in UDA send descriptors.
- `IRDMA_UDA_QPSQ_*` macros describe UDA SQ WQE fields such as push, inline data, fragment count, checksum, AH index, protocol, MAC/IP/L4 lengths, multicast, loopback, and immediate data.
- `IRDMA_UDAQPC_*` macros describe UDA QP context fields, many aliased to generic QP context masks.
- `IRDMA_UDA_CQPSQ_MAV_*` macros define address-vector CQP WQE fields used by `irdma_sc_access_ah()`.
- `IRDMA_UDA_MGCTX_*` and `IRDMA_UDA_CQPSQ_MG_*` define multicast context and multicast CQP WQE fields.
- `IRDMA_UDA_CQPSQ_QHASH_*` defines qhash table programming fields for destination/source ports, addresses, QPN, management operation, IP version, LAN forwarding, and entry type.

## Control Flow
There is no executable flow. The macros are consumed by WQE/context writers through `FIELD_PREP()` and `FIELD_GET()` so numeric values are placed into exact hardware bit positions.

## State And Persistence
No runtime state is stored here. The constants determine the persistent binary layout written into device-visible WQEs, QP contexts, multicast contexts, and qhash commands.

## Dependencies And Integration Points
The header relies on Linux bit macros such as `BIT_ULL()` and `GENMASK_ULL()` and generic IRDMA QP context masks. It is included by `uda.c` and other WQE writers for UDA and qhash operations.

## Risks And Edge Cases
Any incorrect mask or line selector corrupts hardware descriptors in ways that may surface as CQP failures, malformed packets, or silent offload misbehavior. Several macros alias generic QP context fields, so changes in generic definitions affect UDA. The typo-like `IRDMA_UDA_CQPSQ_MAV_DOLOOPBACKK` name is part of local API use and should not be casually renamed without updating consumers.

## Test Signals
Build coverage catches missing macro names. Hardware or emulation tests should validate AH programming, UDA send WQEs, multicast group programming, qhash programming, VLAN and IPv4/IPv6 variants, and descriptor dumps against hardware specifications.
