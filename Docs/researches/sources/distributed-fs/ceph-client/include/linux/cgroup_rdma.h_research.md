# sources/distributed-fs/ceph-client/include/linux/cgroup_rdma.h

## Purpose

`cgroup_rdma.h` declares RDMA controller accounting for HCA handles and HCA objects per cgroup.

## Important APIs, Types, and Functions

Resource ids are `RDMACG_RESOURCE_HCA_HANDLE`, `RDMACG_RESOURCE_HCA_OBJECT`, and `RDMACG_RESOURCE_MAX`. Under `CONFIG_CGROUP_RDMA`, types include `rdma_cgroup` and `rdmacg_device`, with APIs `rdmacg_register_device()`, `rdmacg_unregister_device()`, `rdmacg_try_charge()`, and `rdmacg_uncharge()`.

## Control Flow

RDMA devices register with the controller. RDMA/IB allocation paths call `rdmacg_try_charge()` before creating resources and call `rdmacg_uncharge()` on release.

## State and Persistence Behavior

Runtime state is per-cgroup `rdma_cgroup` css and per-device resource pools. No disk persistence is owned; limits and usage are exposed through cgroup controller files in implementation code.

## Dependencies and Integration Points

It includes `cgroup.h` and integrates with the RDMA/IB stack and cgroup controller core.

## Risks and Edge Cases

The header declares APIs only when enabled; callers must be config-guarded. Device unregister must coordinate with outstanding charged resources. Resource type indexes must remain aligned with controller files.

## Test Signals

Build with `CONFIG_CGROUP_RDMA`, register/unregister mock devices, charge/uncharge both resource types, test limit failures, and verify callers compile out or guard use when disabled.
