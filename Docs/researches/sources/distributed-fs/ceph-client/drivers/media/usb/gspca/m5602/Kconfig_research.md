<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Kconfig

Purpose: this Kconfig fragment defines `CONFIG_USB_M5602`, the build option for ALi m5602 GSPCA webcam support.

Important APIs, types, and functions: it declares a `tristate` option named "ALi USB m5602 Camera Driver", depends on `VIDEO_DEV` and `USB_GSPCA`, and documents the output module name `gspca_m5602`.

Control flow: no runtime behavior. The setting controls whether the m5602 bridge core and supported sensor files are built in, modular, or omitted.

State and persistence: persists in kernel `.config`; runtime state is defined in m5602 C sources and `m5602_bridge.h`.

Dependencies and integration points: integrates with the parent GSPCA media driver menu and Kbuild files. It must remain aligned with the Makefile's `obj-$(CONFIG_USB_M5602)` binding.

Risks: missing `USB_GSPCA` dependency would expose unresolved core symbols. Test signals include menu visibility, successful `CONFIG_USB_M5602=m` build, and generated `gspca_m5602.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Kconfig -->
