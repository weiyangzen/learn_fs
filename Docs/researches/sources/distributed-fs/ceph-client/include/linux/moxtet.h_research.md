<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moxtet.h -->
# sources/distributed-fs/ceph-client/include/linux/moxtet.h

## Purpose
`moxtet.h` defines the Turris MOX module configuration bus interface, including module IDs, bus state, IRQ mapping, driver registration, and device access helpers.

## Important APIs, Types, and Functions
It defines `TURRIS_MOX_MAX_MODULES`, CPU/module ID enums, `MOXTET_NIRQS`, `struct moxtet`, `struct moxtet_driver`, `to_moxtet_driver()`, `__moxtet_register_driver()`, `moxtet_unregister_driver()`, `moxtet_register_driver()`, `module_moxtet_driver()`, `struct moxtet_device`, `moxtet_device_read()`, `moxtet_device_write()`, `moxtet_device_written()`, and `to_moxtet_device()`.

## Control Flow and State
The bus tracks detected modules in `moxtet::modules`, transmit bytes in `tx`, and IRQ state in an embedded domain/chip/mask/existence/position table. Drivers register with an ID table and device-driver object. Device read/write helpers communicate one-byte state to individual MOX modules.

## State and Persistence Behavior
State is runtime bus/device state. Debugfs state is optional. IRQ masks and module arrays persist while the bus device exists.

## Dependencies and Integration Points
It depends on the Linux device model, IRQ domains/chips, mutexes, modules, and optional debugfs. It integrates Turris MOX module drivers with the platform bus implementation.

## Risks
IRQ position and mask bookkeeping must match physical modules. The fixed module count limits probing. Device read/write ordering must respect the bus mutex. Driver registration lifetime follows device-model rules.

## Test Signals
Probe systems with each module ID, test IRQ delivery/masking, register/unregister module drivers, validate debugfs output, and read/write devices under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/moxtet.h -->
