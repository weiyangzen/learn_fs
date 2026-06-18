# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/Makefile.am

Purpose: this Automake file builds `libusbip.la`, the shared support library used by `usbip` and `usbipd`.

Important declarations: `libusbip_la_CPPFLAGS` defines `USBIDS_FILE` from `@USBIDS_DIR@/usb.ids`; `libusbip_la_CFLAGS` inherits `@EXTRA_CFLAGS@`; `libusbip_la_LDFLAGS` sets libtool version info. `lib_LTLIBRARIES := libusbip.la` declares the installed library. Source membership includes USB name parsing, host/vUDC driver backends, common USB/sysfs helpers, VHCI driver access, and headers.

Control flow and integration: this file is generated into `libsrc/Makefile` by configure and is built before `src` through the parent `SUBDIRS`. `src/Makefile.am` links commands against `$(top_builddir)/libsrc/libusbip.la`.

State, dependencies, risks, and tests: no runtime state is owned here. Build dependencies include libudev and Linux USB headers through the source files. Risks include stale source lists causing missing symbols, and `USBIDS_FILE` being compiled in at build time. Test signals are successful library compile/link and downstream command link without unresolved symbols.
