# sources/distributed-fs/ceph-client/drivers/media/spi/Kconfig

Purpose: defines Kconfig menu entries for media SPI adapter drivers, currently Sony CXD2880 SPI support and Gennum GS1662 serializer support.

Important APIs and symbols: the file is gated by `if VIDEO_DEV && SPI`. `CXD2880_SPI_DRV` is a tristate depending on `DVB_CORE && SPI` and defaults to module when ancillary autoselect is disabled. `VIDEO_GS1662` is a tristate depending on `SPI && VIDEO_DEV`, selecting `MEDIA_CONTROLLER` and `VIDEO_V4L2_SUBDEV_API`.

Control flow: Kconfig selection controls whether the matching Makefile builds `cxd2880-spi.o` and/or `gs1662.o`. The top comment for hidden ancillary subdrivers informs menu visibility when `MEDIA_HIDE_ANCILLARY_SUBDRV` is active.

State and persistence: selected values persist only in the kernel build configuration. There is no runtime state.

Dependencies and integration points: integrates with the media driver Kconfig hierarchy, DVB core, SPI core, V4L2 device support, media controller, and ancillary-driver autoselection policy.

Risks and edge cases: the outer `VIDEO_DEV && SPI` gate means CXD2880 SPI support is hidden if `VIDEO_DEV` is off even though the symbol itself depends on DVB core and SPI. Default module behavior changes with `MEDIA_SUBDRV_AUTOSELECT`, so build coverage should include both manual and autoselected configurations.

Test signals: `menuconfig` visibility, `allyesconfig/allmodconfig` builds, configs with `MEDIA_SUBDRV_AUTOSELECT` enabled/disabled, and module presence for `cxd2880-spi` and `gs1662`.
