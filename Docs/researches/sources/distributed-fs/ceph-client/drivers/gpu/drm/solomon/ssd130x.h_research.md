# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/ssd130x.h

Purpose: public header shared by SSD130x core and bus transports.

Important APIs and types: defines command/data pseudo-register bytes `SSD13XX_DATA` and `SSD13XX_COMMAND`, family and variant enums, `struct ssd130x_deviceinfo`, and `struct ssd130x_device`. The device struct embeds DRM plane/CRTC/encoder/connector state, regmap, variant info, parsed panel options, backlight/PWM/reset/regulator resources, geometry, and cached address ranges.

Control flow: transport drivers call `ssd130x_probe()`, `ssd130x_remove()`, and `ssd130x_shutdown()`. Match tables pass `ssd130x_variants[]` entries through device match data.

State and persistence: defines all core-owned state but no storage of its own. Cached address fields avoid redundant address-range commands during runtime updates.

Dependencies and integration: includes DRM connector/CRTC/driver/encoder and Linux regmap. Core source adds additional dependencies for resources and conversion.

Risks: `struct ssd130x_device` includes an `i2c_client *client` that is unused by SPI and appears unused by the core, suggesting legacy carryover. Variant enum order must remain synchronized with `ssd130x_variants[]` and transport match data.

Test signals: compile both transports and validate every OF table `.data` entry indexes a valid variant.
