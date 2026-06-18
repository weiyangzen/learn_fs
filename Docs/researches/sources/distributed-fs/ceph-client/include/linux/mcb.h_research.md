<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mcb.h -->
# sources/distributed-fs/ceph-client/include/linux/mcb.h

## Purpose
This header defines the MEN Chameleon Bus core interfaces for FPGA-described MCB devices, buses, drivers, resources, and registration helpers.

## Important APIs, types, and functions
`struct mcb_bus` describes a carrier-backed bus and IRQ lookup callback. `struct mcb_device` holds device IDs, instance/group/variant/BAR/revision, IRQ and memory resources, bus pointer, and DMA device. `struct mcb_driver` provides ID table and probe/remove/shutdown callbacks. APIs include `mcb_register_driver`, `mcb_unregister_driver`, `module_mcb_driver`, bus/device allocation and registration helpers, memory request/release helpers, IRQ/resource queries, and bus reference helpers.

## Control flow
Carrier drivers allocate a bus, discover Chameleon table entries, allocate/register devices, and add them to the bus. Function drivers register an ID table and bind through probe. Drivers request memory or IRQ resources using MCB helpers and release them during remove.

## State and persistence
Runtime state is in device-model objects, resource descriptors, bus reference counts, and discovered FPGA metadata. Hardware FPGA configuration persists outside the header.

## Dependencies and integration points
It depends on Linux device model, module device tables, IRQ return types, and resources. It integrates FPGA carrier drivers with MCB function drivers.

## Risks and test signals
Risks include duplicate device registration, stale `is_added`, resource lifetime leaks, incorrect IRQ callback behavior, and carrier removal while devices are bound. Test bus allocation/release, device discovery, driver matching, resource request/release, IRQ lookup failures, and module unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mcb.h -->
