# sources/distributed-fs/ceph-client/kernel/cgroup/rdma.c

## Purpose

`rdma.c` implements the RDMA cgroup controller, limiting per-cgroup, per-device RDMA resources such as HCA handles and HCA objects.

## Important APIs, Types, and Functions

Important types are `struct rdma_cgroup`, `struct rdmacg_device`, `struct rdmacg_resource_pool`, and `struct rdmacg_resource`. Exported APIs are `rdmacg_register_device()`, `rdmacg_unregister_device()`, `rdmacg_try_charge()`, and `rdmacg_uncharge()`. User files are `rdma.max` and `rdma.current`.

## Control Flow and State

RDMA device drivers register devices into the global `rdmacg_devices` list. Limits are configured as lines beginning with a device name followed by resource assignments such as `hca_handle=max hca_object=32`. `rdmacg_resource_set_max()` parses those assignments, finds or creates the cgroup/device resource pool, and updates limits.

Charging pins the current RDMA css and walks from the current cgroup to the root. For each ancestor it lazily creates an rpool for the target device, increments usage if below max, and rolls back via `rdmacg_uncharge_hierarchy()` on allocation or limit failure. Uncharge walks back up the hierarchy and decrements usage. Empty rpools whose limits are all unlimited are freed.

## Dependencies and Integration Points

The controller integrates with RDMA core through `linux/cgroup_rdma.h`, cgroup css lifetime, cgroup files, parser helpers, and a global mutex protecting both device and per-cgroup resource-pool lists.

## Risks and Edge Cases

Device unregister assumes no new RDMA resources will be created and frees all pools for that device. Charge rollback must stop at the failed ancestor to avoid over-uncharge. Resource parsing accepts `max` or nonnegative integers and must reject malformed input. Rpool lifetime is tied both to usage and configured finite limits, so cleanup depends on `usage_sum` and `num_max_cnt`.

## Test Signals

Tests should register/unregister devices, write valid and invalid `rdma.max` lines, charge below and above per-resource limits, verify rollback on failures, read current and max across multiple devices, free pools after uncharge/reset-to-max, and race reads/writes against device removal under the mutex.
