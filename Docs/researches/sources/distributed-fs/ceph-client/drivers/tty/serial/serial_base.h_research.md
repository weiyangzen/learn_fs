# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base.h

## Purpose
Internal header for the Linux serial-base bus glue used by serial core, controller devices, and port devices. It is not intended for low-level UART drivers directly.

## Important APIs, Types, And Functions
Defines `struct serial_ctrl_device`, containing a child `struct device` and an IDA for port IDs, and `struct serial_port_device`, containing a child `struct device`, backing `uart_port`, and TX-enabled flag. It declares init/exit hooks for controller and port drivers, bus driver registration helpers, add/remove helpers for synthetic serial-base devices, serial core register/unregister entry points, and console preference matching when console support is enabled.

## Control Flow
`serial_base_bus.c`, `serial_ctrl.c`, `serial_port.c`, and `serial_core.c` share this header. `uart_add_one_port()` reaches `serial_ctrl_register_port()`, then `serial_core_register_port()`, which creates or reuses a controller device and creates a port device before registering the tty.

## State And Persistence
The structures hold only runtime device-model state. IDA state persists for the lifetime of a controller device and is released when its ports are removed.

## Dependencies And Integration Points
Depends on Linux device model, serial core, and container macros. It bridges traditional `uart_port` registration with the newer `serial-base` bus.

## Risks
The header defines internal contracts: misuse by low-level drivers or stale assumptions about `port_dev` lifecycle can lead to runtime PM or device-model bugs.

## Test Signals
Build serial core with and without console support, add/remove multiple ports sharing the same physical device and controller ID, and validate generated device names and port ID reuse.
