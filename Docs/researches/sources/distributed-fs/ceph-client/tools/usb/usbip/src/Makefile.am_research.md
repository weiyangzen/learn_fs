# sources/distributed-fs/ceph-client/tools/usb/usbip/src/Makefile.am

Purpose: this Automake file builds the installed `usbip` CLI and `usbipd` daemon.

Important declarations: `AM_CPPFLAGS` includes `libsrc` and defines `USBIDS_FILE`; `AM_CFLAGS` inherits configure flags; `LDADD` links against `libusbip.la`. `sbin_PROGRAMS := usbip usbipd` declares both binaries. `usbip_SOURCES` includes command dispatch, utilities, network helpers, and attach/detach/list/bind/unbind/port subcommands. `usbipd_SOURCES` includes daemon code and network helpers.

Control flow and integration: generated Makefiles compile commands after the library. The daemon and CLI share `usbip_network.c`, while only the CLI includes command submodules.

State, dependencies, risks, and tests: no runtime state is owned here. Build depends on libusbip and configured libudev/libwrap linkage. Risks include source-list drift, compiled-in usb.ids path, and daemon linking network code separately from the CLI. Test signals are successful build of both sbin programs and command help/version execution.
