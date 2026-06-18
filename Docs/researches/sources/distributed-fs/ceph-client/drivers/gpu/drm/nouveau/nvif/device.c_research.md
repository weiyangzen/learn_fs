# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/device.c

## Purpose
This file wraps the root NVIF device object, device info query, MMIO mapping, device time reads, usermode teardown, and runlist cache cleanup.

## Important APIs, Types, and Functions
Public functions are `nvif_device_ctor`, `nvif_device_dtor`, `nvif_device_map`, and `nvif_device_time`.

## Control Flow
Constructor creates the device object, initializes runlist/usermode fields, then queries `NV_DEVICE_V0_INFO` into `device->info`. Time reads either call the usermode fast path or issue `NV_DEVICE_V0_TIME`. Destructor destroys usermode state, frees runlist cache, and destroys the device object.

## State and Persistence Behavior
State includes device object mapping, `device->info`, optional runlist array, runlist count, and optional usermode object/function table.

## Dependencies and Integration Points
It depends on NVIF client/object APIs, device class methods, usermode helpers, and FIFO runlist discovery.

## Risks
Time fallback warns on method failure but still returns the possibly unchanged time. Constructor failure after object creation must be handled by callers via destructor.

## Test Signals
Signals include device construction/info query, device map/unmap, usermode and non-usermode time reads, runlist cache allocation/free, and device teardown.
