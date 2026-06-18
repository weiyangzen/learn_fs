<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dfl.h -->
# sources/distributed-fs/ceph-client/include/linux/dfl.h

## Purpose
Defines the public driver-model API for Intel FPGA Device Feature List devices on the DFL bus.

## Important APIs, Types, And Functions
The main types are `enum dfl_id_type`, `struct dfl_device`, and `struct dfl_driver`. `struct dfl_device` carries bus device state, FIU type, feature id, revision, MMIO resource, IRQ list, container device, matched id entry, DFH version, and copied parameter block. Driver helpers include `to_dfl_dev()`, `to_dfl_drv()`, `dfl_driver_register()`, `__dfl_driver_register()`, `dfl_driver_unregister()`, `module_dfl_driver()`, and `dfh_find_param()`.

## Control Flow
DFL bus enumeration creates `struct dfl_device` objects for discovered features. A `struct dfl_driver` supplies an id table plus `probe()` and optional `remove()` callbacks. `module_dfl_driver()` wires normal module init/exit to DFL registration and unregistration.

## State And Persistence
State is per-device kernel state: MMIO/IRQ resources, feature metadata, a pointer to the FPGA container, and feature parameter memory. The header defines no persistence; hardware feature state lives behind MMIO and the container driver.

## Dependencies And Integration Points
Depends on the Linux driver model, module ownership, `mod_devicetable.h`, resources, and DFL FPGA container code. It integrates accelerator feature drivers with FPGA FME and PORT feature units.

## Risks And Edge Cases
Drivers must match the correct FIU type and feature id. Misusing the copied `params` block or assuming a DFH version can break feature probing. IRQ array lifetime and MMIO resource bounds are provided by the bus and must be respected by child drivers.

## Test Signals
Build DFL drivers as modules and built-ins, verify modalias/id-table binding, probe/remove ordering, resource exposure, IRQ counts, `dfh_find_param()` lookup, and failed-probe unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dfl.h -->
