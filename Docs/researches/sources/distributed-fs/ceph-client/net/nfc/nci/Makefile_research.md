# sources/distributed-fs/ceph-client/net/nfc/nci/Makefile

Purpose: Describes how the NFC NCI core and optional transport modules are built.

Important APIs and targets: `obj-$(CONFIG_NFC_NCI) += nci.o` builds the core aggregate. `nci-objs := core.o data.o lib.o ntf.o rsp.o hci.o` defines the core module contents. `nci_spi-y += spi.o` and `obj-$(CONFIG_NFC_NCI_SPI) += nci_spi.o` build the SPI transport. `nci_uart-y += uart.o` and `obj-$(CONFIG_NFC_NCI_UART) += nci_uart.o` build the UART transport.

Control flow: Kbuild links the listed object files into `nci.ko` or built-in code according to Kconfig selections. Transport objects are separate modules so controller drivers can depend on only the transport they need.

State and persistence: No runtime state. Build graph state is determined by Kconfig symbols.

Dependencies and integration points: Must remain synchronized with exported symbols used by NCI drivers and with files present in the directory. Core includes HCI-over-NCI support by always linking `hci.o` into `nci.o`.

Risks: Adding new core source files without updating `nci-objs` silently omits code. Removing or renaming transport files without updating the Makefile breaks builds under matching config combinations.

Test signals: Build all enabled combinations and verify that exported symbols from `core.o`, `data.o`, `lib.o`, `ntf.o`, `rsp.o`, and `hci.o` are available from the core module.
