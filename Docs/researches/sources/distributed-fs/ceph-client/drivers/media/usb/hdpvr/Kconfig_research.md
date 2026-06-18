<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Kconfig

Purpose: Kconfig entry for Hauppauge HD PVR USB support. It enables the `hdpvr` V4L2 driver as a tristate option.

Important APIs/types/functions: `config VIDEO_HDPVR` is the only symbol. It depends on `VIDEO_DEV` and documents that modular builds produce the `hdpvr` module.

Control flow: when selected, Kbuild includes `drivers/media/usb/hdpvr/Makefile`, which links the core, control, video, and I2C sources into one driver. The symbol does not select helper libraries itself; it relies on media core dependencies around `VIDEO_DEV`.

State and persistence: build-time configuration only. It creates no runtime state and no persistent data.

Dependencies and integration: integrates the HD-PVR USB driver into the media USB menu. Runtime USB matching is implemented in `hdpvr-core.c`, not here.

Risks: the dependency is minimal. If optional I2C/IR support is expected, the source uses `IS_ENABLED(CONFIG_I2C)` rather than a Kconfig dependency here, so configurations without I2C still build the driver but omit adapter registration.

Test signals: `oldconfig`, `allmodconfig`, and `make M=drivers/media/usb/hdpvr`; verify `CONFIG_VIDEO_HDPVR=m` produces `hdpvr.ko` and that `CONFIG_VIDEO_DEV=n` hides the option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Kconfig -->
