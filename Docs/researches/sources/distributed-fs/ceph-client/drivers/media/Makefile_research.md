# sources/distributed-fs/ceph-client/drivers/media/Makefile

Purpose: This Makefile orders and gates compilation of the media driver subtree. It ensures foundational subtrees such as I2C/tuners, media controller, V4L2, DVB, RC, and CEC are linked before dependent drivers.

Important APIs, types, and functions: Build variables include unconditional `obj-y += i2c/ tuners/`, `obj-$(CONFIG_DVB_CORE) += dvb-frontends/`, conditional `mc/`, `v4l2-core/`, `dvb-core/`, unconditional `rc/`, `obj-$(CONFIG_CEC_CORE) += cec/`, and final driver directory aggregation for `common/ platform/ pci/ usb/ mmc/ firewire/ spi/ test-drivers/` plus `radio/` under `CONFIG_VIDEO_DEV`.

Control flow and state: Kbuild descends into core/ancillary directories first so built-in drivers that depend on I2C subdrivers or core APIs can resolve symbols. `CONFIG_MEDIA_CONTROLLER=y` is special-cased so the media controller core is only linked into `MEDIA_SUPPORT` when built in.

State and persistence behavior: There is no runtime state. The file transforms `.config` symbols into object-directory traversal.

Dependencies and integration points: It integrates Kconfig symbols with Kbuild and relies on each child directory to gate individual drivers. It also reflects a link-order dependency: I2C drivers before other drivers, RC core before RC drivers, and CEC subtree when `CEC_CORE` is selected.

Risks and edge cases: Reordering can break built-in link dependencies or cause drivers to initialize before the core they require. Adding a new CEC or media subtree in the wrong position can create unresolved symbols in non-modular builds that would not appear in module-only testing.

Test signals: Build coverage should include built-in and modular media configs, `CONFIG_CEC_CORE=y/m`, `CONFIG_VIDEO_DEV=n`, `CONFIG_DVB_CORE=y/m`, and `CONFIG_MEDIA_CONTROLLER=y` to catch ordering and link failures.
