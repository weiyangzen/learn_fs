<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Kconfig

Purpose: this Kconfig fragment defines `CONFIG_USB_GL860`, the build-time switch for the Genesys Logic GL860 GSPCA camera driver.

Important APIs, types, and functions: it declares a `tristate` option named "GL860 USB Camera Driver" and depends on both `VIDEO_DEV` and `USB_GSPCA`. Its help text documents that the module name is `gspca_gl860`.

Control flow: there is no runtime control flow. In Kbuild configuration, selecting `Y` links the driver into the kernel image, `M` builds the module, and unset excludes the GL860 sources from compilation.

State and persistence: the option persists through the kernel `.config`. It gates compilation only; runtime state is held by `gl860.c` and sensor files.

Dependencies and integration points: integrates with the media USB GSPCA Kconfig hierarchy. The `USB_GSPCA` dependency is important because GL860 sources include and call the shared GSPCA core.

Risks: if dependencies are relaxed incorrectly, the module could compile without required V4L2/GSPCA symbols. Test signals are Kconfig visibility under the GSPCA menu, successful `M` builds producing `gspca_gl860.ko`, and absence of unresolved GSPCA/V4L2 symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Kconfig -->
