# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Makefile

Purpose: Kbuild object composition for the legacy `dvb-usb` framework and its device-specific modules. It links the common framework pieces and maps Kconfig symbols to composite driver objects.

Important APIs/types/functions: `dvb-usb-objs` aggregates common framework files including firmware, init, URB, I2C, DVB, remote, and generic `usb-urb.o`. `obj-$(CONFIG_DVB_USB)` emits `dvb-usb.o`. Per-driver composite variables such as `dvb-usb-a800-objs`, `dvb-usb-cxusb-objs`, `dvb-usb-dib0700-objs`, and others map source files to modules. `ccflags-y` adds include paths for DVB frontends, tuners, and media common code.

Control flow: after Kconfig selects a symbol, Kbuild includes the corresponding `obj-*` line. Composite object lists fold one or more C files into each resulting module. CXUSB conditionally adds analog support when `CONFIG_DVB_USB_CXUSB_ANALOG=y`.

State and persistence: no runtime state; it defines build artifacts and include path visibility.

Dependencies and integration: pairs with `Kconfig` and legacy source files in this directory. Include flags allow direct inclusion of frontend/tuner/common headers used by the many bridge drivers.

Risks: missing an object from a composite list causes unresolved symbols or missing functionality. Common `ccflags-y` expose broad include paths to every object, which can mask dependency boundaries. Object naming differs from source names in some cases, so Kconfig/module naming must remain synchronized.

Test signals: `make M=drivers/media/usb/dvb-usb` under each selected symbol; module names match expected `dvb-usb-*`; CXUSB analog object inclusion when enabled; link success with frontend/tuner configs as modules and built-ins.
