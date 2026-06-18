# sources/distributed-fs/ceph-client/drivers/media/tuners/Kconfig

Purpose: Kconfig menu for common media tuner drivers. It defines the umbrella `MEDIA_TUNER` tristate, autoselect behavior for ancillary subdrivers, the visible "Customize TV tuners" menu, and per-driver symbols including the files in this work item: `MEDIA_TUNER_E4000`, `FC0011`, `FC0012`, `FC0013`, `FC2580`, `IT913X`, `M88RS6000T`, `MAX2165`, and `MC44S803`.

Control flow is Kconfig dependency resolution: symbols depend mainly on `MEDIA_SUPPORT` and `I2C`; E4000/FC2580 additionally depend on `VIDEO_DEV` and select `REGMAP_I2C`, while IT913X/M88RS6000T select `REGMAP_I2C`. Defaults are modules when ancillary autoselect is disabled. The top-level `MEDIA_TUNER` selects older analog helpers when `MEDIA_SUBDRV_AUTOSELECT` is set.

State is build configuration only. Dependencies integrate with Makefile `obj-$(CONFIG_...)` lines and header `IS_REACHABLE()` attach stubs. Risks: missing dependency selects cause link failures, hiding ancillary subdrivers can make expected options invisible, and autoselect may include drivers unexpectedly. Test signals: `allyesconfig`, `allmodconfig`, minimal I2C-disabled configs, and build tests for each symbol as built-in/module/disabled.
