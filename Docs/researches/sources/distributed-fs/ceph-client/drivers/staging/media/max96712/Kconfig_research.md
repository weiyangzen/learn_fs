# sources/distributed-fs/ceph-client/drivers/staging/media/max96712/Kconfig

Purpose: this Kconfig entry exposes the staging V4L2 subdevice driver for Maxim MAX96712 Quad GMSL2 deserializers as `CONFIG_VIDEO_MAX96712`. It can be built in or as a module and documents that the module name is `max96712`.

Important symbols: `VIDEO_MAX96712` is a tristate option labeled "Maxim MAX96712 Quad GMSL2 Deserializer support". It directly depends on `I2C`, `OF_GPIO`, and `VIDEO_DEV`, and selects `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, and `MEDIA_CONTROLLER`.

Control flow and integration: Kconfig selection controls whether `max96712.o` is included by the local Makefile. The dependencies line up with `max96712.c`, which uses I2C regmap access, optional GPIO power control, fwnode endpoint parsing, V4L2 subdev state, controls, and media pads.

State and persistence behavior: no runtime state is defined here. The configuration state determines whether the driver can bind compatible OF nodes and whether V4L2 subdevice/media-controller support is available.

Risks: the driver parses OF graph endpoints and uses `devm_gpiod_get_optional()`, so `OF_GPIO` and fwnode selections are required. If the driver later supports ACPI or non-OF systems, these dependencies may need loosening. Selecting subdev API and media controller can pull additional framework code into builds, which is expected for this driver.

Test signals: `allyesconfig`, `allmodconfig`, and `COMPILE_TEST`-style builds should verify dependency closure. Runtime probe tests need a device tree node with an endpoint on port 4 and an optional `enable` GPIO.
