# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Makefile

Purpose: builds the UDC core and selected USB peripheral controller drivers from Kconfig symbols.

Important APIs, types, and functions: `udc-core-y := core.o trace.o` builds common UDC support; `CFLAGS_trace.o` points trace generation at the source directory. `obj-$(CONFIG_...)` lines map each controller symbol to its object or subdirectory. Multi-object aliases include `fsl_usb2_udc-y := fsl_udc_core.o`.

Control flow: kbuild includes `udc-core.o` whenever `CONFIG_USB_GADGET` is enabled, then conditionally descends into controller objects such as `dummy_hcd.o`, `net2280.o`, `amd5536udc_pci.o`, `aspeed-vhub/`, `bdc/`, and `cdns2/`.

State and persistence: no runtime state. Build outputs depend on Kconfig values.

Dependencies and integration points: ties `drivers/usb/gadget/udc/Kconfig` symbols to compiled objects and subdirectories. The trace CFLAGS line supports local trace header inclusion.

Risks: symbol/object drift causes selected drivers not to build. Subdirectory entries require their own Makefiles. Missing shared object mappings can break link when Kconfig selects a core symbol.

Test signals: build each UDC symbol as module and built-in, run `make W=1 drivers/usb/gadget/udc/`, verify trace compilation, and compare Kconfig symbols against Makefile entries.
