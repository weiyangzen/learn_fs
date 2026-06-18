# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ah.c

## Purpose
This file implements mlx5 address-handle creation and query. It converts RDMA core `rdma_ah_attr` values into an mlx5 address vector used by UD/RoCE send paths and returns selected AH data to userspace.

## Important APIs, types, and functions
The public functions are `mlx5_ib_create_ah` and `mlx5_ib_query_ah`. Internal helpers are `mlx5_ah_get_udp_sport`, which selects a RoCEv2 UDP source port from the GRH flow label or device minimum, and `create_ib_ah`, which fills `struct mlx5_ib_ah` address-vector fields.

## Control flow
Creation first rejects RoCE AHs without GRH. For userspace RoCE AH creation, it validates the response length and copies the resolved destination MAC back through udata. The helper then copies GRH destination GID, flow label, SGID index, hop limit, and traffic class when present; translates static rate; and diverges by AH type. RoCE AHs set optional LAG transmit port, destination MAC, UDP source port, SL bits, and ECN enablement for RoCEv2. InfiniBand AHs set DLID, path bits, and SL.

Query clears the output attribute, restores type, checks whether the AV has GRH-present state, populates GRH and DGID, then sets DLID, static rate, and SL from the stored AV fields.

## State and persistence behavior
The AH state is the in-memory `mlx5_ib_ah` address vector. It is stable until the AH is destroyed by RDMA core. No firmware object is allocated here and there is no disk persistence.

## Dependencies and integration points
The file depends on RDMA AH helpers, GID type semantics, RoCE UDP port helpers, rate translation via `mlx5r_ib_rate`, LAG slave selection, user ABI response structures, and mlx5 send-path AV consumers.

## Risks
Risks include incorrect GRH requirement enforcement for RoCE, wrong SL bit packing for RoCE versus IB, stale assumptions about `sgid_attr`, UDP source-port entropy mismatch, ECN bit behavior, and query not reconstructing all RoCE-specific attributes such as MAC fields.

## Test signals
Create/query IB, RoCEv1, and RoCEv2 AHs; validate udata DMAC response length handling; test flow-label-derived UDP sport; verify LAG transmit slave mapping; send UD traffic across SL/rate settings; and run negative tests for RoCE without GRH and invalid static rates.
