# sources/distributed-fs/ceph-client/drivers/media/usb/Makefile

Purpose: kbuild routing for USB media driver subdirectories.

APIs/rules: unconditional `obj-y` descends into DVB USB support directories. Conditional `obj-$(CONFIG_...)` entries build selected drivers including `airspy/`, `gspca/`, `uvc/`, `em28xx/`, and others.

Control flow/state: kbuild descends based on `.config`; no runtime state exists.

Dependencies/integration: config symbols must match sourced Kconfig files. `CONFIG_USB_AIRSPY` routes to `airspy/`.

Risks/tests: symbol/object drift prevents selected drivers from building. Test targeted module builds and Kconfig/Makefile coverage when adding drivers.
