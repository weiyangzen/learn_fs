# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/Makefile

Purpose: Describes how Kbuild assembles the nGene PCIe bridge driver.

Important APIs, types, and functions: `ngene-objs` lists `ngene-core.o`, `ngene-i2c.o`, `ngene-cards.o`, and `ngene-dvb.o` as the composite module parts. `obj-$(CONFIG_DVB_NGENE) += ngene.o` wires the composite object to the Kconfig option. Two `ccflags-y` entries add DVB frontend and tuner include paths.

Control flow: Build-time only. Kbuild compiles each source file, links them into `ngene.o`, and emits a module or built-in object based on `CONFIG_DVB_NGENE`.

State and persistence: No runtime state. The Makefile controls object composition and include search paths.

Dependencies and integration points: The include flags support local C includes such as `stv090x.h`, `cxd2841er.h`, `tda18212.h`, and tuner headers included from `ngene-cards.c`. File ordering does not encode runtime sequencing; runtime entry points are exported through `ngene.h` and PCI module registration in `ngene-cards.c`.

Risks: Any new source added to the nGene driver must be added to `ngene-objs`. The explicit include paths mirror media-tree layout and can hide missing fully qualified include updates during refactors.

Test signals: Build `CONFIG_DVB_NGENE=y` and `m`, check the composite object includes all four source objects, and run include-path cleanup builds after moving frontend/tuner headers.
