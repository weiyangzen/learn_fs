# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base_bus.c

## Purpose
Implements the `serial-base` bus and the synthetic controller/port devices that sit between physical UART hardware devices and tty/serial-core registration.

## Important APIs, Types, And Functions
`serial_base_driver_register()` and unregister bind controller/port drivers to the bus. `serial_base_ctrl_add()` creates controller devices named `physical:ctrl_id`; `serial_base_port_add()` creates port devices named `physical:ctrl_id.port_id`; remove helpers delete and put devices. `serial_base_match_and_update_preferred_console()` supports `console=DEVNAME:0.0` style matching under console builds.

## Control Flow
`arch_initcall(serial_base_init)` registers the bus, then the controller and port drivers, and sets `serial_base_initialized`. Device creation before init returns `-EPROBE_DEFER`. Matching is prefix-based on device type (`ctrl` or `port`) against driver name. Port IDs are allocated from the controller's IDA unless `uart_port.port_id` is preselected.

## State And Persistence
Runtime state includes the bus registration flag, device objects, fwnode references reused from physical parents, and per-controller IDA allocations. No persistent data survives module unload.

## Dependencies And Integration Points
Uses device core, IDA, fwnode/property handling, spinlock includes, serial core, and optional console matching. `serial_core.c` is the primary caller for add/remove.

## Risks
Reference counting is central: fwnode handles are acquired during init and released in device release callbacks, and failed add paths must call `put_device()`. Prefix matching is simple, so driver names must remain `ctrl` and `port` aligned. Early port registration depends on `-EPROBE_DEFER` behavior.

## Test Signals
Validate `/sys/bus/serial-base` devices, add multiple UARTs under one physical device, test fixed and automatic `port_id`, force early registration deferral, remove last port and confirm controller cleanup, and test preferred-console matching.
