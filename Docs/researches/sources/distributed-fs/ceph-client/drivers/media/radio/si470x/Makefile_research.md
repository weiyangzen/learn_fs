# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Makefile

Purpose: maps Si470x Kconfig symbols to kbuild object files.

Important APIs and entries: `obj-$(CONFIG_RADIO_SI470X)` builds `radio-si470x-common.o`, `obj-$(CONFIG_USB_SI470X)` builds `radio-si470x-usb.o`, and `obj-$(CONFIG_I2C_SI470X)` builds `radio-si470x-i2c.o`.

Control flow: kbuild compiles the common helper as its own module and bus-specific USB/I2C modules separately according to selected tristates. Bus modules depend on exported symbols from the common module.

State and persistence: no runtime state. Build output is determined by `.config`.

Dependencies and integration points: depends on Kconfig symbols from the same directory and source file names. The common file exports `si470x_ctrl_ops`, `si470x_viddev_template`, `si470x_set_freq`, `si470x_start`, and `si470x_stop` for bus modules.

Risks: adding a new bus transport requires both Kconfig and Makefile updates. If common and bus symbols are built with incompatible module/link settings, unresolved export issues would appear at build time.

Test signals: per-symbol builds for common, USB, I2C, and combined configurations; module dependency generation; and `make M=drivers/media/radio/si470x`.
