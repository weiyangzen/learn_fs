<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.c

## Purpose
`rmi_bus.c` implements the Linux `rmi4` bus, registration of physical RMI devices from transport drivers, registration of per-function child devices, binding of function handlers, nested IRQ setup for function attention callbacks, OF child matching, debug logging, and module init/exit.

## Important APIs, Types, and Functions
Exported APIs include `rmi_dbg()`, `rmi_register_transport_device()`, `rmi_unregister_transport_device()`, `rmi_is_physical_device()`, `rmi_is_function_device()`, `rmi_register_function()`, `rmi_unregister_function()`, `__rmi_register_function_handler()`, `rmi_unregister_function_handler()`, and `rmi_of_property_read_u32()`. Bus matching is done by `rmi_bus_match()`. Function probing uses `rmi_function_probe()`, `rmi_function_remove()`, and `rmi_create_function_irq()`.

## Control Flow
Module init registers the `rmi4` bus, registers all compiled-in function handlers, and registers the physical RMI driver. A transport driver calls `rmi_register_transport_device()`, which creates a physical `rmi_device`; the physical driver scans the PDT and calls `rmi_register_function()` for function child devices. Function child probe invokes the handler's `probe()` and maps each function interrupt bit into a Linux IRQ with a simple nested IRQ chip and threaded handler. Module exit unregisters the physical driver, function handlers, and bus.

## State and Persistence
Physical devices and function devices are kernel device-model objects with release callbacks that free allocated structures. Function IRQ mappings are disposed on unregister. The global `debug_flags` module parameter controls conditional debug output.

## Dependencies and Integration Points
The file integrates with Linux device/bus core, IRQ domains, OF child nodes named `rmi4-fXX`, PM infrastructure, RMI transport APIs from `linux/rmi.h`, and the physical-driver helpers in `rmi_driver.c`. The `fn_handlers[]` list is built from Kconfig-selected handler symbols.

## Risks and Edge Cases
Error unwind during bus init unregisters the bus but does not explicitly unregister function handlers if physical-driver registration fails after handler registration; this mirrors the local code path and should be checked carefully. Function IRQ creation assumes `rmi_driver_data` and `irqdomain` are ready before function probe side effects. Optional OF properties return zero and default values when absent, so callers must distinguish absent optional values from explicit zero where that matters.

## Test Signals
Validate transport registration/unregistration, function device creation/removal, handler binding by function number, nested IRQ delivery to attention callbacks, OF child binding, module unload, and debug flag output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_bus.c -->
