# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.h

## Purpose

This internal header shares Speed Select device IDs, MSR addresses, device-type constants, callback structure, and helper prototypes between the common interface and backend drivers.

## Important APIs, Types, And Functions

`struct isst_if_cmd_cb` describes backend ioctl handlers, command sizes, user buffer offsets, API version, owner module, per-command callback, and optional default ioctl callback. Constants include `ISST_IF_CMD_LIMIT`, API/driver versions, backend IDs, PCI device IDs, and OS mailbox MSRs.

## Control Flow

Backends fill `struct isst_if_cmd_cb` and call `isst_if_cdev_register()`. The common ioctl path uses `cmd_size`, `offset`, and callback pointers to dispatch user requests.

## State And Persistence

The header itself has no state; it defines contracts for shared global state in `isst_if_common.c`.

## Dependencies And Integration Points

It depends on UAPI command structures and is included by MMIO, PCI mailbox, MSR mailbox, and TPMI core code.

## Risks

The callback contract requires correct `offset` and `cmd_size`; mistakes would copy the wrong bytes from userspace. `ISST_IF_CMD_LIMIT` bounds latency and memory use, so UAPI changes must respect it.

## Test Signals

Compile all backends, check API version reported through platform info, and exercise each backend's registered callback through the common ioctl path.
