# sources/distributed-fs/ceph-client/drivers/media/i2c/Kconfig

Purpose: Central Kconfig menu for V4L2 media I2C subdevice drivers, including camera sensors, lenses, flash devices, audio/video decoders, video encoders, SDR tuners, helper chips, and serializers/deserializers.

Important APIs/types/functions: The file is gated by `if VIDEO_DEV`. Relevant entries in this subset are `VIDEO_AD5820` under `VIDEO_CAMERA_LENS` with `depends on I2C && GPIOLIB`, `MEDIA_CONTROLLER`, and `VIDEO_V4L2_SUBDEV_API`; `VIDEO_ADP1653` under flash devices with `depends on I2C && GPIOLIB && MEDIA_CAMERA_SUPPORT`; `VIDEO_ADV7170` and `VIDEO_ADV7175` under "Video encoders" with `depends on VIDEO_DEV && I2C`. The file also sources nested Kconfigs such as `ccs`, `et8ek8`, and `cx25840`.

Control flow: Menuconfig symbols group large families and hide ancillary subdrivers when `MEDIA_HIDE_ANCILLARY_SUBDRV` is set. Selecting a tristate here controls Makefile object inclusion and, for some camera/lens symbols, selects media-controller/subdev support needed by the implementation.

State and persistence: Kconfig selections are compile-time state controlling which modules are built and which helper frameworks are selected. No runtime state exists.

Dependencies/integration: Integrated with the media subsystem Kconfig tree, I2C, V4L2, media controller, GPIO, OF, ACPI, regmap, and helper subsystem symbols. `drivers/media/i2c/Makefile` consumes these symbols.

Risks and test signals: Build all relevant symbols as disabled/built-in/module, especially dependency combinations for lens/flash media-controller support and old video encoders. Kconfig dependency mistakes surface as missing types/functions at compile time or unusable menus for board configurations.
