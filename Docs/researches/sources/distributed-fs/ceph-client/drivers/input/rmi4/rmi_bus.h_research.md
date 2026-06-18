<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.h

## Purpose
`rmi_bus.h` defines the internal RMI bus abstractions for physical devices, function devices, function handlers, transport read/write helpers, and debug flags.

## Important APIs, Types, and Functions
`struct rmi_function` represents one function descriptor discovered on a physical RMI device and includes IRQ metadata plus a flexible `irq_mask`. `struct rmi_function_handler` describes handler callbacks for probe, remove, config, reset, attention, suspend, and resume. Inline helpers `rmi_read()`, `rmi_read_block()`, `rmi_write()`, and `rmi_write_block()` dispatch through the transport operations. The header declares function/device registration APIs and `rmi_bus_type`.

## Control Flow
The header defines the callback contracts used by `rmi_bus.c` and `rmi_driver.c`: transports create physical devices, the physical driver creates function devices, and function handlers bind by function number and receive lifecycle/attention callbacks.

## State and Persistence
The structures describe runtime device-model state. `irq_mask` is sized dynamically based on total function IRQ bits when functions are allocated.

## Dependencies and Integration Points
It depends on public RMI platform/transport definitions from `linux/rmi.h`, Linux device-driver types, and the bus implementation. Function drivers include this header indirectly through `rmi_driver.h`.

## Risks and Edge Cases
The inline transport helpers assume `xport->ops->read_block` and `write_block` are valid and return kernel-style error codes. Handlers must tolerate callbacks being absent in other functions and must manage device data lifetime through devm or remove callbacks.

## Test Signals
Build coverage with multiple transports and functions, static analysis of callback signatures, and runtime RMI function probe/IRQ/config paths validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.h -->
