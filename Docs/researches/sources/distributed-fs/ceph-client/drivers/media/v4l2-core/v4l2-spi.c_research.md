# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-spi.c

## Purpose
`v4l2-spi.c` provides helper routines for V4L2 subdevices implemented as SPI devices. It mirrors the older I2C helper pattern for initializing, dynamically creating, registering, and unregistering SPI-backed subdevs.

## Important APIs, Types, And Functions
Exports are `v4l2_spi_subdev_init()`, `v4l2_spi_new_subdev()`, and `v4l2_spi_subdev_unregister()`. They operate on `struct v4l2_subdev`, `struct spi_device`, `struct spi_controller`, `struct spi_board_info`, and `struct v4l2_device`.

## Control Flow
`v4l2_spi_subdev_init()` calls `v4l2_subdev_init()`, marks the subdev as SPI, copies the SPI driver's module owner, stores the SPI device in subdev private data, stores the subdev in SPI driver data, and formats a subdev name from driver and device names. `v4l2_spi_new_subdev()` optionally requests the module named by `modalias`, creates a device with `spi_new_device()`, verifies a bound driver, takes the module reference, retrieves the subdev from driver data, registers it with the V4L2 device, then drops the temporary module reference. On failure it unregisters the SPI device. `v4l2_spi_subdev_unregister()` unregisters only board-created SPI devices without firmware nodes.

## State And Persistence
State is the bidirectional association between SPI device and V4L2 subdev, plus module reference counts during registration. No persistent configuration is stored by this helper; it delegates lifetime to SPI core and V4L2 device registration.

## Dependencies And Integration Points
The file depends on SPI core APIs, V4L2 common/device/subdev helpers, and module loading. It is used by bridge drivers that instantiate SPI peripheral subdevices from board info instead of firmware-described devices.

## Risks And Test Signals
Risks include NULL driver pointers after device creation, module reference imbalance, unregistering firmware-owned devices, and assuming the SPI driver set its drvdata to a subdev during probe. Tests should cover modalias autoload success/failure, driver-bound and unbound `spi_new_device()` results, `__v4l2_device_register_subdev()` failure cleanup, and unregister behavior for OF/fwnode versus board-info devices.
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-spi.c

## Purpose
`v4l2-spi.c` provides helper routines for V4L2 subdevices implemented as SPI devices. It mirrors the older I2C helper pattern for initializing, dynamically creating, registering, and unregistering SPI-backed subdevs.

## Important APIs, Types, And Functions
Exports are `v4l2_spi_subdev_init()`, `v4l2_spi_new_subdev()`, and `v4l2_spi_subdev_unregister()`. They operate on `struct v4l2_subdev`, `struct spi_device`, `struct spi_controller`, `struct spi_board_info`, and `struct v4l2_device`.

## Control Flow
`v4l2_spi_subdev_init()` calls `v4l2_subdev_init()`, marks the subdev as SPI, copies the SPI driver's module owner, stores the SPI device in subdev private data, stores the subdev in SPI driver data, and formats a subdev name from driver and device names. `v4l2_spi_new_subdev()` optionally requests the module named by `modalias`, creates a device with `spi_new_device()`, verifies a bound driver, takes the module reference, retrieves the subdev from driver data, registers it with the V4L2 device, then drops the temporary module reference. On failure it unregisters the SPI device. `v4l2_spi_subdev_unregister()` unregisters only board-created SPI devices without firmware nodes.

## State And Persistence
State is the bidirectional association between SPI device and V4L2 subdev, plus module reference counts during registration. No persistent configuration is stored by this helper; it delegates lifetime to SPI core and V4L2 device registration.

## Dependencies And Integration Points
The file depends on SPI core APIs, V4L2 common/device/subdev helpers, and module loading. It is used by bridge drivers that instantiate SPI peripheral subdevices from board info instead of firmware-described devices.

## Risks And Test Signals
Risks include NULL driver pointers after device creation, module reference imbalance, unregistering firmware-owned devices, and assuming the SPI driver set its drvdata to a subdev during probe. Tests should cover modalias autoload success/failure, driver-bound and unbound `spi_new_device()` results, `__v4l2_device_register_subdev()` failure cleanup, and unregister behavior for OF/fwnode versus board-info devices.
