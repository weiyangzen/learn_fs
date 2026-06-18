# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/Makefile

Purpose: Defines Kbuild object composition for Marvell NFC NCI core and transport modules.

Important APIs, types, and functions: `nfcmrvl-y += main.o fw_dnld.o` builds the common core; transport modules map `usb.o`, `uart.o`, `i2c.o`, and `spi.o` into `nfcmrvl_usb`, `nfcmrvl_uart`, `nfcmrvl_i2c`, and `nfcmrvl_spi`.

Control flow: Build-time only. Kbuild emits the selected core and bus modules from Kconfig symbols.

State and persistence behavior: No runtime state in this file; module names and object composition are build outputs visible to userspace.

Dependencies and integration points: Aligns `nfcmrvl/Kconfig` with source files in the same directory. The core object combines main driver logic with firmware download support.

Risks: Module composition must keep common firmware download code linked into the core and avoid unresolved symbols for transport modules. Renaming transport modules affects autoload and packaging.

Test signals: Build each transport as a module, run modpost for unresolved symbols, verify module names, and build with only the core selected where Kconfig permits.
