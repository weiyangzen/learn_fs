# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.c

## Purpose

This file implements the IPU7 auxiliary bus device layer and runtime PM domain used to split the base PCI driver into ISYS/PSYS child devices.

## Important APIs, Types, and Functions

Public APIs are `ipu7_bus_initialize_device()`, `ipu7_bus_add_device()`, and `ipu7_bus_del_devices()`. Runtime PM callbacks are `bus_pm_runtime_suspend()` and `bus_pm_runtime_resume()`. `ipu7_bus_release()` frees per-device private data and the bus device.

## Control Flow

Initialization allocates an `ipu7_bus_device`, binds it to the PCI parent/IPU device/control data, initializes an auxiliary device, attaches a PM domain, forbids runtime PM, then enables PM. Adding the device calls `auxiliary_device_add()`, links it into `isp->devices` under a mutex, and allows runtime PM. Deletion disables runtime PM, removes from the list, deletes the auxiliary device, and uninitializes it. Runtime resume powers up the buttress-controlled subsystem before generic resume; suspend runs generic suspend then powers down.

## State and Persistence Behavior

Each child holds auxiliary device state, driver data, subsystem ID, pdata, MMU/syscom/firmware fields, DMA mask, firmware SGT, and boot config fields. A global mutex protects the device list.

## Dependencies and Integration Points

It depends on Linux auxiliary bus, PM domains/runtime PM, PCI, and the buttress power API. It is the handoff layer between `ipu7.c` and subsystem modules such as ISYS.

## Risks and Edge Cases

Powerdown failure attempts generic resume and returns busy/I/O error. Device release frees `pdata`, so ownership must be clear. Runtime PM is initially forbidden until the auxiliary device is added.

## Test Signals

Auxiliary probe/remove, runtime PM resume/suspend, failure of buttress powerup/powerdown, and unloading modules with live child devices.
