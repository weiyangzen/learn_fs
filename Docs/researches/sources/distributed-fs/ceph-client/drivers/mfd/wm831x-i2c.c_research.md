# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-i2c.c

`wm831x-i2c.c` is the I2C frontend for WM831x PMICs. It matches supported WM831x/WM832x devices, allocates shared core state, creates the I2C regmap, copies platform data, and delegates to `wm831x_device_init()`.

The main function is `wm831x_i2c_probe()`: it obtains enum match data with `i2c_get_match_data()`, allocates `struct wm831x`, stores client data, sets device/type, initializes `devm_regmap_init_i2c()` using `wm831x_regmap_config`, copies `wm831x_pdata`, and passes `i2c->irq` to the core. PM callbacks `wm831x_i2c_suspend()` and `wm831x_i2c_poweroff()` call core suspend/shutdown helpers. `wm831x_i2c_id[]`, `wm831x_i2c_driver`, and `wm831x_i2c_init()` provide matching and `subsys_initcall()` registration.

The file has little persistent state beyond devres allocation, regmap, and I2C client data. It depends on I2C, OF match data exported from the core, regmap I2C support, platform data, and the common WM831x core. It suppresses bind attributes, so manual sysfs unbind/rebind is disabled.

Risks: probe fails if match data is missing; no remove path is provided; hibernation/freeze coverage differs from the SPI frontend. Test signals include I2C ID and OF matching, regmap allocation failures, successful child-device creation through the core, and suspend/poweroff callback exercise.
