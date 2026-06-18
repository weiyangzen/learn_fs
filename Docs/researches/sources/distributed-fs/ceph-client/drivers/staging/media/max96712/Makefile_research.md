# sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Makefile

Purpose: this Makefile connects `CONFIG_VIDEO_MAX96712` to the single object file implementing the Maxim deserializer V4L2 subdevice driver.

Important build API: `obj-$(CONFIG_VIDEO_MAX96712) += max96712.o` means the object is built into the kernel or as a module according to the Kconfig tristate state. There are no composite objects, generated sources, or local compiler flags.

Control flow and integration: the parent staging media Makefile includes this directory when enabled. The module metadata in `max96712.c` provides the runtime module description, author, license, I2C driver registration, and OF match table.

State and persistence behavior: no runtime state is created here. Build state is entirely determined by the Kconfig symbol.

Risks: because the driver is a single object, future file splits require converting this to a composite object list. The object name must continue to match the documented module name in Kconfig.

Test signals: verify `CONFIG_VIDEO_MAX96712=m` produces `max96712.ko` and `CONFIG_VIDEO_MAX96712=y` links the object into the kernel image without missing media, I2C, GPIO, or regmap dependencies.
