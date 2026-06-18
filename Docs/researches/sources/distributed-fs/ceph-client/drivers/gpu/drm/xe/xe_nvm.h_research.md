
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.h

## Purpose

`xe_nvm.h` declares the Xe NVM auxiliary-device initialization entry point.

## Important APIs, Types, and Functions

It forward declares `struct xe_device` and exposes `int xe_nvm_init(struct xe_device *xe)`.

## Control Flow

Device probe calls `xe_nvm_init()` after enough platform/MMIO state exists to determine NVM availability and policy.

## State and Persistence Behavior

All persistent state is stored in `xe->nvm` by the implementation.

## Dependencies and Integration Points

The header is consumed by device probe code that conditionally creates the NVM auxiliary device.

## Risks and Edge Cases

Callers must not assume NVM exists after a successful `0` return because unsupported devices and VFs also return success with no device registered.

## Test Signals

Probe tests should assert both registered and intentionally absent NVM outcomes.
