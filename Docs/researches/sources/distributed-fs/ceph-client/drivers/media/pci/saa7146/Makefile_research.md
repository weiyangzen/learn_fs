# sources/distributed-fs/ceph-client/drivers/media/pci/saa7146/Makefile

Purpose: maps SAA7146 Kconfig symbols to the board-driver objects and adds the media I2C include path needed by local board sources.

Important APIs, types, and functions: `obj-$(CONFIG_VIDEO_MXB) += mxb.o`, `obj-$(CONFIG_VIDEO_HEXIUM_ORION) += hexium_orion.o`, and `obj-$(CONFIG_VIDEO_HEXIUM_GEMINI) += hexium_gemini.o` are the build rules. `ccflags-y += -I$(srctree)/drivers/media/i2c` lets `mxb.c` include local headers such as `tea6415c.h` and `tea6420.h`.

Control flow: build-system only. Enabled symbols cause Kbuild to compile and link the corresponding module or built-in object.

State and persistence: no runtime state. The built artifacts persist in the build tree.

Dependencies and integration points: relies on the Kconfig symbols and on headers from `drivers/media/i2c`. The resulting object modules register with the SAA7146 extension framework at module init.

Risks: removing the include path breaks MXB compilation. Incorrect object mapping would silently omit a selected driver. Since each source is a single-object module, link errors surface directly in that object.

Test signals: `make M=drivers/media/pci/saa7146` with each symbol as `m` or `y`; verify generated modules are named `mxb`, `hexium_orion`, and `hexium_gemini`.
