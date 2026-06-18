# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.h

## Purpose
This header declares the mlx5 IB command-wrapper interface implemented in `cmd.c` and consumed by mlx5 RDMA subsystems.

## Important APIs, types, and functions
The declarations cover special mkey query, congestion parameter query, PD/TIR/TIS/RQT/transport-domain lifecycle, multicast group attach/detach, XRCD lifecycle, MAD IFC execution, UAR lifecycle, and VUID query. It includes `mlx5_ib.h` and `<linux/mlx5/driver.h>` so callers share the core device and mlx5 IB device types.

## Control flow
There is no executable control flow. Build-time inclusion makes command wrappers available to files such as congestion, QP, multicast, resource allocation, MAD, and user-context handling code.

## State and persistence behavior
The header owns no state. It defines function contracts for operations that mutate firmware resources or driver caches elsewhere.

## Dependencies and integration points
This is an internal interface boundary between mlx5 IB logic and mlx5 core command mailboxes. Changes here require matching implementation changes in `cmd.c` and caller updates across the mlx5 IB driver.

## Risks
Risks are ABI-internal: prototype drift, uid parameter misuse, ownership ambiguity for returned ids, and adding wrappers without clear allocation/deallocation pairing. Because it is included by multiple driver files, incorrect declarations can cause build failures or subtle call-site mismatches.

## Test signals
Compile coverage with all mlx5 optional features enabled is the primary signal. Runtime coverage comes from the command users: MAD, UAR, MCG, congestion, XRCD, and transport-domain lifecycle tests.
