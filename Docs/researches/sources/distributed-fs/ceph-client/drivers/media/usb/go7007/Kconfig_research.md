# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/Kconfig

Purpose: declares kernel configuration options for the WIS GO7007 MPEG encoder family, USB transport support, firmware loader support, and Sensoray 2250/2251 board support.

Important APIs/types/functions: Kconfig symbols are `VIDEO_GO7007`, `VIDEO_GO7007_USB`, `VIDEO_GO7007_LOADER`, and `VIDEO_GO7007_USB_S2250_BOARD`. `VIDEO_GO7007` depends on V4L2/I2C/SND/USB, selects vb2 vmalloc, tuner, Cypress firmware, PCM audio, and multiple possible media subdevice drivers under autoselect. USB, loader, and Sensoray symbols layer on top of the base symbol.

Control flow: build-time only. Enabling the base driver exposes the core module; enabling USB adds the transport module; enabling loader adds the firmware loader; enabling Sensoray adds board-specific support. Defaults make the loader `y` when the base is enabled unless overridden.

State and persistence: no runtime state. It controls which object files/modules are compiled and which dependency modules are selected.

Dependencies and integration points: integrates with the media Kconfig tree, V4L2, I2C, ALSA, USB, Cypress firmware helper, and optional subdevice drivers (`saa711x`, `tw2804`, `tw9903`, `tw9906`, `uda1342`, `ov7640`, Sony tuner support).

Risks: broad `select` usage can force extra media/ALSA code into builds and hide missing direct dependencies in source files. `VIDEO_GO7007_LOADER` defaulting to y may surprise minimal configurations. Tests should include `allyesconfig`, `allmodconfig`, minimal module builds for each symbol, and dependency-resolution checks with `MEDIA_SUBDRV_AUTOSELECT` both enabled and disabled.
