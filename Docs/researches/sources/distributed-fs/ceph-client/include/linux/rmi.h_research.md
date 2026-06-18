# sources/distributed-fs/ceph-client/include/linux/rmi.h

## Purpose
`rmi.h` is the public interface for Synaptics RMI4 touch/input devices. It describes platform data, function descriptors, transport devices, transport operations, RMI drivers, device-private runtime state, and suspend/resume/attention entry points.

## Important APIs, types, and functions
Key data structures include `struct rmi_2d_axis_alignment`, `enum rmi_sensor_type`, `struct rmi_2d_sensor_platform_data`, `struct rmi_gpio_data`, `enum rmi_reg_state`, `struct rmi_f01_power_management`, `struct rmi_device_platform_data_spi`, `struct rmi_device_platform_data`, `struct rmi_function_descriptor`, `struct rmi_transport_dev`, `struct rmi_transport_ops`, `struct rmi_driver`, `struct rmi_device`, `struct rmi4_attn_data`, and `struct rmi_driver_data`. Public functions are `rmi_register_transport_device()`, `rmi_unregister_transport_device()`, `rmi_set_attn_data()`, `rmi_driver_suspend()`, and `rmi_driver_resume()`.

## Control flow, state, and persistence
Transport drivers allocate an `rmi_transport_dev`, fill bus-specific read/write/reset operations, platform data, and a parent device, then register it with the RMI core. Function discovery uses `struct rmi_function_descriptor` page/offset fields to bind function drivers. Attention data and IRQ state are carried through `rmi4_attn_data` and `rmi_driver_data` FIFOs/lists. Runtime state persists in the device model, function lists, interrupt masks, wakeup settings, and platform-configured sensor overrides until unregister or suspend/resume changes them.

## Dependencies and integration points
The header integrates Linux device core, input subsystem, interrupts, kfifo, lists, modules, and bus transports such as I2C/SPI/HID. Platform data feeds F01 power management, F11 2D absolute/relative reporting, F30/F3A GPIO/button reporting, reset GPIO handling, firmware reset delays, and optional SPI chip-select timing callbacks.

## Risks and test signals
Risks include incorrect axis swap/flip/clipping, invalid firmware quirk overrides, missing interrupt masks, transport read/write block-size mismatches, custom SPI chip-select timing errors, and stale attention data across suspend/resume. Test signals include probe/discovery on RMI4 touchpads and touchscreens, F11 coordinate transformation tests, GPIO/button quirk coverage, suspend wake behavior, IRQ FIFO draining, reset sequencing, and transport error injection.
