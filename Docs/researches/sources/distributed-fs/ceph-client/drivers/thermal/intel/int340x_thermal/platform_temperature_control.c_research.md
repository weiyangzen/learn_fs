# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/platform_temperature_control.c

## Purpose

`platform_temperature_control.c` exposes Processor Thermal Device platform temperature control MMIO registers as sysfs and debugfs controls for target temperature, enable, tolerance/gain, and debug temperature override.

## Important APIs, Types, and Functions

`struct mmio_reg` describes bitfields and units. `struct ptc_data` stores per-instance offset, PCI device, sysfs group, attributes, and group name. Exported APIs are `proc_thermal_ptc_add()` and `proc_thermal_ptc_remove()`. `ptc_mmio_show()`, `ptc_store()`, and `ptc_mmio_write()` implement field access under `ptc_lock`. Debugfs `temperature_0..2` files write override values via `ptc_temperature_write()`.

## Control Flow

When the PTC feature bit is present, add initializes three instances at offsets `0x5B20`, `0x5B28`, and `0x5B30`, creates per-instance sysfs groups named `ptc_N_control`, and creates a global debugfs directory. Sysfs reads extract bitfields and scale 0.5C units to millicelsius-like integer values; writes validate input against field masks and write back through read-modify-write.

## State and Persistence Behavior

The file has static global `ptc_instance[]` and `ptc_debugfs`. Hardware register values persist in the processor thermal MMIO block until changed or reset. The mutex serializes concurrent read-modify-write sequences.

## Dependencies and Integration Points

It depends on PCI driver data being `struct proc_thermal_device` with valid `mmio_base`, sysfs/debugfs, and the processor thermal feature mask. It is invoked by `proc_thermal_mmio_add()` and removed by `proc_thermal_mmio_remove()`.

## Risks and Test Signals

Risks include global static instances shared across devices, ignoring `ptc_create_groups()` failures, debugfs override bypassing sysfs visibility, unit truncation on writes, and write-shift overflow if inputs exceed masks. Test signals include PTC feature probe, three sysfs groups, read/write validation, debugfs override enable/disable with zero/nonzero writes, and concurrent sysfs access under lock.
