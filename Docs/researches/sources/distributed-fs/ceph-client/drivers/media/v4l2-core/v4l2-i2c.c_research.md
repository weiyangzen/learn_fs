# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-i2c.c

## Purpose
`v4l2-i2c.c` provides helper functions for V4L2 subdevices implemented as I2C clients. It initializes subdevice/client cross-links, creates board-info or probed I2C clients, registers them under a V4L2 device, unregisters non-firmware-created clients, reports subdevice addresses, and exposes common tuner probe address lists.

## Important APIs, Types, and Functions
Exported APIs include `v4l2_i2c_subdev_unregister`, `v4l2_i2c_subdev_set_name`, `v4l2_i2c_subdev_init`, `v4l2_i2c_new_subdev_board`, `v4l2_i2c_new_subdev`, `v4l2_i2c_subdev_addr`, and `v4l2_i2c_tuner_addrs`. Important types are `struct v4l2_subdev`, `struct i2c_client`, `struct i2c_adapter`, `struct i2c_board_info`, and `enum v4l2_i2c_tuner_type`.

## Control Flow
`v4l2_i2c_subdev_init` calls `v4l2_subdev_init`, marks the subdevice as I2C, sets the owner from the I2C driver's module owner, stores the device pointer, connects `sd` to `client` through V4L2 and I2C clientdata, and generates a name containing driver, adapter id, and address. `v4l2_i2c_new_subdev` builds board info from a client type and address, then delegates to `v4l2_i2c_new_subdev_board`.

`v4l2_i2c_new_subdev_board` first requests the I2C module by type. It creates either a scanned or fixed-address I2C client, checks that a driver bound, temporarily gets the I2C driver's module owner, obtains the subdevice from clientdata, registers it with the V4L2 device using `__v4l2_device_register_subdev`, then releases the temporary module reference. If any step leaves a client without a registered subdevice, the client is unregistered. `v4l2_i2c_subdev_unregister` explicitly unregisters only clients that lack firmware nodes, preserving DT/ACPI-created devices.

## State and Persistence Behavior
State is runtime-only: I2C client objects, V4L2 subdevice bindings, clientdata pointers, module references, and optional V4L2-device subdevice list membership. Firmware-created devices are not removed by this helper because the platform will not recreate them from a V4L2 driver probe alone.

## Dependencies and Integration Points
This file integrates the I2C core, module autoloading, V4L2 subdevice core, and V4L2 device registration. Bridge drivers use it to instantiate legacy board-info based sensors, tuners, and decoders.

## Risks
Autoload timing and module reference ordering are delicate: the helper explicitly loads the module before creating the client so `client->driver` and clientdata are available. Firmware-created clients must not be unregistered. Failure paths must avoid leaking clients or module references. Name construction assumes `client->dev.driver` and adapter data are valid after binding.

## Test Signals
Test fixed-address and probed-address creation, missing module/driver binding, failed V4L2 subdevice registration, firmware-node clients on unregister, address reporting with and without clientdata, tuner address list selection, and module reference balance over probe/remove cycles.
