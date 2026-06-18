# sources/distributed-fs/ceph-client/drivers/mfd/viperboard.c

## Purpose
`viperboard.c` is the USB MFD core for the Nano River Technologies Viperboard. It identifies the USB device, stores shared USB state, reads firmware version bytes, and registers hotplug child devices for GPIO, I2C, and ADC functions.

## Important APIs, Types, And Functions
The USB match table `vprbrd_table[]` matches vendor/product `0x2058:0x1005`. Child cells are `viperboard-gpio`, `viperboard-i2c`, and `viperboard-adc`. Lifecycle functions are `vprbrd_probe()` and `vprbrd_disconnect()`, registered through `module_usb_driver()`. Shared state is `struct vprbrd` from `linux/mfd/viperboard.h`, including USB device pointer, lock, and control buffer.

## Control Flow
Probe allocates state, initializes its mutex, stores the `usb_device` pointer from the interface, attaches state to the USB interface and embedded platform device, reads major and minor version bytes with USB control messages on endpoint zero, logs the version and bus/address, and calls `mfd_add_hotplug_devices()` for the child cells. On child-add failure it frees state and returns the error. Disconnect removes MFD children, clears USB interface data, frees state, and logs debug output.

## State, Persistence, And Dependencies
The core persists only the in-memory `struct vprbrd` while the USB interface is bound. Hardware state is not modified beyond control-message reads. Child drivers depend on the shared USB device pointer, buffer, and lock for their own transactions. Dependencies include USB core control transfers, MFD hotplug device support, child drivers for GPIO/I2C/ADC, and the Viperboard protocol constants.

## Integration Points
The MFD children are created as hotplug devices under the USB interface device so they follow USB connect/disconnect lifetime. The core does not implement GPIO/I2C/ADC protocols itself; it provides discovery and shared transport state for child drivers. Module aliasing comes from `MODULE_DEVICE_TABLE(usb, vprbrd_table)`.

## Risks
Version control-message failures are tolerated silently, leaving version fields partially zero while probe continues. The USB device pointer is not separately reference-counted with `usb_get_dev()`, so correctness relies on interface binding lifetime. Error cleanup frees state but does not clear interface data on the probe failure path. `dev_set_drvdata(&vb->pdev.dev, vb)` depends on the layout and initialization expectations of `struct vprbrd`. The core advertises no SPI child despite the board comment noting unsupported SPI.

## Test Signals
Tests should plug the matching USB device, confirm version log formatting, and verify hotplug creation of GPIO/I2C/ADC children. Disconnect should remove children before freeing shared state. Fault tests should inject failed major/minor version reads and failed MFD child registration. Concurrency tests should run child USB operations while disconnecting to verify child cleanup and shared-lock behavior.
