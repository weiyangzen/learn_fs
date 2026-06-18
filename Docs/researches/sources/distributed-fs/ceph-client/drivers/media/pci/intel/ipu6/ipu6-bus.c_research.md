# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.c

## Purpose
This file implements the private IPU6 auxiliary bus glue used to expose IPU subsystems, such as ISYS and PSYS, as auxiliary devices under the PCI parent. It also attaches a runtime-PM domain that powers subsystem buttress controls around generic child suspend/resume.

## Important APIs, types, and functions
`ipu6_bus_initialize_device()` allocates `struct ipu6_bus_device`, initializes its embedded `auxiliary_device`, associates platform data and a buttress power-control descriptor, installs the PM domain, and enables runtime PM in a forbidden state. `ipu6_bus_add_device()` registers the auxiliary device, adds it to `isp->devices` under `ipu6_bus_mutex`, and allows runtime PM. `ipu6_bus_del_devices()` disables runtime PM, removes list entries, deletes auxiliary devices, and uninitializes them. `bus_pm_runtime_suspend()` and `bus_pm_runtime_resume()` wrap `pm_generic_runtime_*()` with `ipu6_buttress_power()`.

## Control flow and integration points
The PCI core initializes a bus device, then adds it so a matching auxiliary driver can bind. Runtime resume powers the subsystem first and then resumes the child driver; runtime suspend suspends the child driver first and then powers down the hardware. On power-down failure the code attempts to resume the child to leave the device usable.

## State, persistence, and dependencies
State is the allocated `ipu6_bus_device`, list membership in `isp->devices`, platform data, firmware pointers, MMU pointer, package directory data, and buttress control descriptor. Dependencies include Linux auxiliary bus, runtime PM, PM domains, PCI drvdata, and `ipu6_buttress_power()`.

## Risks and test signals
Risks are PM ordering bugs, leaked auxiliary devices on add/delete errors, use-after-free of platform data, and list races if deletion overlaps driver callbacks. Test signals include auxiliary probe/remove, runtime PM get/put cycles, power-domain transition logs, error injection for power-down failure, and clean module unload with no remaining devices.
