# sources/distributed-fs/ceph-client/drivers/nfc/pn533/Makefile

Purpose: Defines Kbuild object composition for PN533 core and transport modules.

Important definitions: `pn533_usb-objs = usb.o`, `pn533_i2c-objs = i2c.o`, and `pn532_uart-objs = uart.o` map transport modules. `obj-$(CONFIG_NFC_PN533)` builds `pn533.o`; transport objects are controlled by their matching Kconfig symbols.

Control flow: No runtime flow; Kbuild links source files into modules.

State and persistence: Build artifacts only.

Dependencies and integration points: Must stay aligned with exports from `pn533.c` and imports from transport files such as `pn53x_common_init()`, `pn533_finalize_setup()`, and `pn533_recv_frame()`.

Risks: Object/module name drift breaks module loading or Kconfig help text. Test signals include allmodconfig builds and link checks for each transport against the core symbol exports.
