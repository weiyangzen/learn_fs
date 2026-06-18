# sources/distributed-fs/ceph-client/drivers/tty/serdev/core.c

## Purpose
Implements the serial device bus core: controller/device allocation, bus matching, OF/ACPI enumeration, exported client APIs for open/close/write/baud/parity/flow/modem/break control, driver registration, runtime PM, and power-domain integration.

## Important APIs, types, and functions
- Bus/device model: `serdev_bus_type`, `serdev_device_type`, `serdev_ctrl_type`, `serdev_device_match()`, `serdev_device_uevent()`, `modalias_show()`.
- Device lifecycle: `serdev_device_alloc()`, `serdev_device_add()`, `serdev_device_remove()`, `serdev_device_put()` via release, and single-slave storage in `ctrl->serdev`.
- Controller lifecycle: `serdev_controller_alloc()`, `serdev_controller_add()`, `serdev_controller_remove()`, controller release through `ctrl_ida`.
- Client APIs: `serdev_device_open()`, `serdev_device_close()`, `devm_serdev_device_open()`, `serdev_device_write_buf()`, `serdev_device_write()`, `serdev_device_write_wakeup()`, `serdev_device_write_flush()`, `serdev_device_set_baudrate()`, `serdev_device_set_flow_control()`, `serdev_device_set_parity()`, `serdev_device_wait_until_sent()`, `serdev_device_get_tiocm()`, `serdev_device_set_tiocm()`, and `serdev_device_break_ctl()`.
- Enumeration: `of_serdev_register_devices()`, `of_find_serdev_controller_by_node()`, `serdev_acpi_get_uart_resource()`, `acpi_serdev_register_devices()`, `acpi_serdev_check_resources()`, and blacklist/quirk paths.
- Driver registration: `__serdev_device_driver_register()`, `serdev_drv_probe()`, `serdev_drv_remove()`, and `serdev_drv_shutdown()`.

## Control flow
`postcore_initcall(serdev_init)` registers the `serial` bus before serial drivers create controllers. A controller driver allocates a controller, sets operations, then calls `serdev_controller_add()`. The core adds the controller device, enables runtime PM, then enumerates child serdev devices from devicetree children or ACPI UARTSerialBus resources. Device add enforces the current single-slave limit by checking `ctrl->serdev`.

Client drivers match by ACPI or OF modalias. Probe attaches a PM domain with power-on semantics, then calls the serdev driver's `probe`. Serdev clients open the controller through `ctrl->ops->open`, then take a runtime PM reference; close releases runtime PM and calls controller close.

Synchronous write serializes through `serdev->write_lock`, repeatedly calls controller `write_buf`, advances the buffer by accepted bytes, and waits on `write_comp` until `serdev_device_write_wakeup()` is called by the controller side.

## State and persistence behavior
State is transient kernel device-model state: controller IDs from `ctrl_ida`, controller/device references, `ctrl->serdev`, completions and mutexes per serdev device, runtime PM state, ACPI enumeration marks, and OF/ACPI fwnodes. No persistent storage is used.

## Dependencies and integration points
Depends on Linux driver core, OF and ACPI matching/enumeration, PM domains, runtime PM, property APIs, IDA allocation, and serdev controller operation callbacks usually supplied by `serdev-ttyport.c` or hardware-specific controllers. ACPI has Apple-specific fallback behavior for empty resource templates and a blacklist for known problematic INT3511/INT3512 devices.

## Risks and edge cases
- Only one serdev child per controller is supported; additional children return `-EBUSY`.
- `serdev_device_write()` requires client `write_wakeup`; without it, synchronous writes fail with `-EINVAL` or can time out.
- `serdev_controller_add()` treats absence of both OF and ACPI devices as `-ENODEV`, except DT graph connector cases.
- ACPI scan depth and resource matching must avoid claiming unrelated UARTSerialBus devices.
- Runtime PM ordering matters: open first calls controller open, then gets PM; failures must close the controller.

## Test signals
Tests should cover OF child enumeration, ACPI UARTSerialBus enumeration and blacklists, single-child busy rejection, modalias uevents, open/close runtime PM reference behavior, synchronous write completion/timeout/signal paths, and exported parameter setters returning `-EOPNOTSUPP` when controller callbacks are missing.
