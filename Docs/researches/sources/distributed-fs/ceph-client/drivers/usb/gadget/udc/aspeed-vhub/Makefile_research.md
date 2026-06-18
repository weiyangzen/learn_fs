# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Makefile

Purpose: kbuild recipe for the Aspeed vHub UDC driver.

Important APIs, types, and functions: maps `CONFIG_USB_ASPEED_VHUB` to `aspeed-vhub.o` and composes it from `core.o`, `ep0.o`, `epn.o`, `dev.o`, and `hub.o`.

Control flow: when the Kconfig symbol is enabled, kbuild compiles and links all five implementation objects into one driver.

State and persistence: build-only file with no runtime state.

Dependencies and integration points: must stay synchronized with declarations in `vhub.h` and calls between core, endpoint-zero, generic endpoint, device, and hub emulation files.

Risks: omitting one component breaks unresolved symbols or runtime functionality. Adding new implementation files requires this list to change.

Test signals: build as module and built-in, ensure all five objects link, and run modpost to catch missing exports or unresolved internal calls.
