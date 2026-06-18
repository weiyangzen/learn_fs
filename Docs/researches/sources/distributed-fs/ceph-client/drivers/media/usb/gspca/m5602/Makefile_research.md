<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Makefile

Purpose: this Makefile composes the ALi m5602 GSPCA module from its bridge core and sensor-specific implementation files.

Important APIs, types, and functions: `obj-$(CONFIG_USB_M5602) += gspca_m5602.o` binds build output to Kconfig. `gspca_m5602-objs` lists `m5602_core.o`, `m5602_ov9650.o`, `m5602_ov7660.o`, `m5602_mt9m111.o`, `m5602_po1030.o`, `m5602_s5k83a.o`, and `m5602_s5k4aa.o`. `ccflags-y` adds the parent GSPCA include path.

Control flow: Kbuild compiles and links the listed objects into `gspca_m5602.o` for either built-in or module output.

State and persistence: no runtime state. The object list defines which sensor backends are available to the bridge core.

Dependencies and integration points: must match declarations and sensor tables used by the m5602 core and `m5602_bridge.h`; the include flag is required for `gspca.h`.

Risks: object list drift causes link failures or missing sensor support. Test signals are clean Kbuild with `CONFIG_USB_M5602=m`, expected module name, and no missing sensor symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/Makefile -->
