# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.h

## Purpose
`rxe.h` is the top-level RXE internal header. It centralizes RDMA/network includes, debug/error logging macros, ABI constants, common prototypes, and the helper that maps a netdev to an RXE device.

## Important APIs, types, and functions
It defines `RXE_UVERBS_ABI_VERSION`, `RXE_ROCE_V2_SPORT`, logging macros for device/object types, `rxe_set_mtu()`, `rxe_add()`, `rxe_rcv()`, `rxe_get_dev_from_net()`, port state helpers, and the external workqueue `rxe_wq`. It includes RXE network, opcode, header, parameter, verbs, and local declarations.

## Control flow
The inline `rxe_get_dev_from_net()` calls `ib_device_get_by_netdev(ndev, RDMA_DRIVER_RXE)` and converts the returned IB device to `struct rxe_dev`; callers must release the reference. Other declarations are implemented in RXE source files.

## State and persistence
No state is owned in the header. Constants affect user ABI and default packet behavior; logging macros shape diagnostic output.

## Dependencies and integration points
The header integrates RXE with RDMA core headers, user verbs structures, address/GID helpers, sk_buffs, and internal RXE modules. It is included by most RXE implementation files.

## Risks
ABI version changes affect userspace providers. Logging macros dereference object/device pointers, so callsites must ensure object lifetime. `rxe_get_dev_from_net()` reference ownership must be followed exactly to avoid leaks or use-after-put.

## Test signals
Build all RXE objects after header changes, run uverbs compatibility tests, and use refcount/debug builds around duplicate-device and netdev-delete paths that call `rxe_get_dev_from_net()`.
