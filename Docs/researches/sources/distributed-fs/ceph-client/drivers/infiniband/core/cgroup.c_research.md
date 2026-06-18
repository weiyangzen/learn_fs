# sources/distributed-fs/ceph-client/drivers/infiniband/core/cgroup.c

## Purpose

`cgroup.c` connects RDMA devices and RDMA resource objects to the kernel RDMA cgroup controller. It provides device registration/unregistration and exported charge/uncharge helpers for RDMA resource accounting.

## Important APIs, Types, And Functions

- `ib_device_register_rdmacg()` sets `device->cg_device.name` and registers the RDMA cgroup device.
- `ib_device_unregister_rdmacg()` unregisters the RDMA cgroup device.
- `ib_rdmacg_try_charge()` charges a resource of type `enum rdmacg_resource_type` to an `ib_rdmacg_object` and device cgroup object.
- `ib_rdmacg_uncharge()` releases a prior charge.

## Control Flow

Device registration is expected before exposing the RDMA device to user space, so user allocations cannot bypass accounting. Unregistration is expected after user-triggered allocations are impossible and resources are deallocated. Per-object charge/uncharge calls delegate directly to `rdmacg_try_charge()` and `rdmacg_uncharge()`.

## State And Persistence

The file stores no private state. It writes the RDMA cgroup device name into `device->cg_device` and relies on the cgroup core for accounting state. Accounting is runtime-only and tied to device/resource lifetimes.

## Dependencies And Integration Points

The file includes `core_priv.h` for RDMA core internals and depends on the kernel RDMA cgroup API. The charge helpers are exported for consumers that allocate/deallocate RDMA resources and need cgroup enforcement.

## Risks

- Registering too late can allow unaccounted allocations; unregistering too early can strand accounting state or allow post-unregister allocation paths.
- Callers must pair successful charges with uncharges using the same device and resource index.
- `ib_rdmacg_try_charge()` can fail, and allocation paths must propagate or unwind that failure.

## Test Signals

Signals include cgroup limit enforcement for RDMA resources, no accounting leaks after resource teardown, correct failures when limits are exceeded, and lifecycle tests confirming registration precedes user exposure and unregistration follows resource cleanup.
