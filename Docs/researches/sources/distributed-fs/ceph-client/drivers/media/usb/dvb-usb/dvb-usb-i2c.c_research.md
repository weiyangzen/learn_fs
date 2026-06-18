# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-i2c.c

Purpose: I2C adapter registration helpers for DVB USB devices whose bridge exposes an I2C bus to demodulators, tuners, EEPROMs, or board peripherals.

Important APIs/functions: `dvb_usb_i2c_init()` registers an `i2c_adapter` using `d->props.i2c_algo`; `dvb_usb_i2c_exit()` unregisters it when initialized.

Control flow: device init calls `dvb_usb_i2c_init()` after power-on. If the device properties lack `DVB_USB_IS_AN_I2C_ADAPTER`, the function is a no-op. Otherwise it validates the algorithm, names the adapter after the device description, sets parent device and private data, calls `i2c_add_adapter()`, and sets `DVB_USB_STATE_I2C`. Exit deletes the adapter if the state bit is present.

State and persistence: the `i2c_adapter` embedded in `struct dvb_usb_device` persists for the device lifetime. The state bit gates cleanup. Hardware I2C state is implemented by each device-specific algorithm.

Dependencies and integration: depends on Linux I2C core and property callbacks from board drivers.

Risks: a device declaring I2C capability without an algorithm fails init. Adapter naming depends on a valid matched description. Cleanup relies on the state bit being set only after successful registration.

Test signals: probe devices with and without I2C capability, demod/tuner attach through registered adapter, `i2cdetect`-style transfer behavior where safe, and disconnect cleanup without leaked adapters.
