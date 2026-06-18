# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/Makefile

Purpose: maps `CONFIG_USB_STV06XX` to the composite `gspca_stv06xx` module and lists its bridge and sensor backend objects.

Important APIs and entries: `obj-$(CONFIG_USB_STV06XX) += gspca_stv06xx.o`; `gspca_stv06xx-objs` includes `stv06xx.o`, `stv06xx_vv6410.o`, `stv06xx_hdcs.o`, `stv06xx_pb0100.o`, and `stv06xx_st6422.o`; `ccflags-y` adds the parent GSPCA include path.

Control flow: kbuild compiles separate backend objects and links them into one module, letting the bridge core probe and dispatch among statically linked sensor descriptors.

State and persistence: no runtime state. It defines build composition only.

Dependencies and integration points: depends on Kconfig symbol `USB_STV06XX`, local headers under `stv06xx/`, and parent `drivers/media/usb/gspca` headers.

Risks: adding or removing a backend requires updating this list. The headers define some `const struct stv06xx_sensor` objects, so the single composite module include pattern matters for avoiding duplicate definitions.

Test signals: module build with `CONFIG_USB_STV06XX=y/m`, link checks for all sensor descriptor references, and include-path validation.
