<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci.h -->
# sources/distributed-fs/ceph-client/include/linux/peci.h

## Purpose
Defines the Linux PECI core device model abstractions: controllers, controller operations, devices, and bounded request buffers.

## Important APIs, Types, And Functions
- `PECI_REQUEST_MAX_BUF_SIZE` caps PECI TX/RX buffers at 32 bytes.
- `struct peci_controller_ops` contains the controller-specific `xfer()` method.
- `struct peci_controller` embeds `struct device`, controller ops, a `bus_lock` mutex held for transfer duration, and a controller ID.
- `devm_peci_controller_add()` registers a managed PECI controller.
- `to_peci_controller()` and `to_peci_device()` are container helpers.
- `struct peci_device` stores device-model state, CPU identity information, PECI address, and deletion flag.
- `struct peci_request` carries the target device plus TX/RX buffers and lengths.

## Control Flow
A hardware driver registers a `peci_controller` with `devm_peci_controller_add()` and supplies `xfer()`. PECI core/device drivers build `struct peci_request` objects with TX and expected RX lengths, then the core serializes bus access with `bus_lock` and invokes the controller `xfer()` callback for a given address.

## State And Persistence
Persistent kernel state is the registered controller device, discovered PECI devices with CPU info/socket/address, and the deletion flag used during removal. Request buffers are stack or caller-owned transaction state and are bounded to 32 bytes.

## Dependencies And Integration Points
Depends on Linux device model, mutexes, kernel helpers, and fixed-width types. It integrates controller drivers on non-PECI buses, PECI CPU helper routines, hwmon/thermal/power drivers, and device lifetime management through devres.

## Risks And Edge Cases
Risks include missing bus serialization in controller drivers, buffer length overflow beyond 32 bytes, use-after-delete of `peci_device`, transfer callbacks returning partial or malformed data, and address collisions on a controller bus.

## Test Signals
Register/unregister controller drivers, enumerate PECI devices, run concurrent transfer clients to validate `bus_lock`, test max-length TX/RX requests, simulate controller errors, and remove devices while clients hold references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/peci.h -->
