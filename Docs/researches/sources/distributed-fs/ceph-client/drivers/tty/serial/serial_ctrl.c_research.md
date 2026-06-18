# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_ctrl.c

## Purpose
Serial-base controller device driver. It binds synthetic controller devices on the `serial-base` bus and enables runtime PM for the controller-level device.

## Important APIs, Types, And Functions
`serial_ctrl_probe()` enables runtime PM; `serial_ctrl_remove()` disables it. `serial_ctrl_register_port()` forwards to `serial_core_register_port()`, and `serial_ctrl_unregister_port()` forwards to `serial_core_unregister_port()`. `serial_base_ctrl_init()` and exit register/unregister the internal driver named `ctrl`.

## Control Flow
The serial-base bus init calls `serial_base_ctrl_init()`. When a controller device created by `serial_base_ctrl_add()` binds, probe enables PM. UART add/remove calls from low-level drivers are routed through this layer into `serial_core.c`.

## State And Persistence
No private persistent state is kept in this file. Runtime PM enablement is tied to the lifetime of the synthetic controller device.

## Dependencies And Integration Points
Uses Linux device core, PM runtime, serial core, and the local serial-base header. It is a thin bridge between serial-base controller devices and serial-core registration.

## Risks
Because it intentionally does little, most risk is ordering: controller PM must be enabled only after a controller device exists and disabled on remove. Forwarding functions preserve the serial-core contract.

## Test Signals
Inspect controller devices on the serial-base bus, verify PM runtime state appears for controller devices, and confirm `uart_add_one_port()`/`uart_remove_one_port()` still create and destroy tty devices through this layer.
