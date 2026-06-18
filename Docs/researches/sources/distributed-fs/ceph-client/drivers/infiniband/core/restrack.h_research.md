# sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.h

## Purpose
`restrack.h` is the private header for RDMA resource tracking internals. It defines the per-device resource tracking root and declares the core lifecycle/name helpers implemented in `restrack.c`.

## Important APIs, types, and functions
- `struct rdma_restrack_root` contains the XArray for one resource type and the next cyclic allocation ID.
- Declared functions are `rdma_restrack_init()`, `rdma_restrack_clean()`, `rdma_restrack_add()`, `rdma_restrack_del()`, `rdma_restrack_new()`, `rdma_restrack_set_name()`, and `rdma_restrack_parent_name()`.

## Control flow and behavior
The header itself has no executable flow. Its contract is that device registration initializes an array of roots, resource creation initializes and adds entries, resource destruction deletes them, and callers may set ownership metadata either from the current task or from a parent resource.

## State, persistence, and dependencies
Persistent state is the `xarray` and `next_id` stored in every `rdma_restrack_root`. The header depends on Linux mutex declarations and public RDMA restrack entry/type definitions that are pulled in by includers.

## Integration points
This header is included by core resource tracking implementation and RDMA core files that need to initialize or manipulate tracking entries without exposing implementation details to external modules.

## Risks and test signals
Risks are mostly contract-level: adding new resource types without updating `res_to_dev()` and callers, or changing ID allocation assumptions without updating reporting consumers. Test signals are successful device init/cleanup with empty XArrays, resource count consistency, and compile coverage for all users of the private prototypes.
