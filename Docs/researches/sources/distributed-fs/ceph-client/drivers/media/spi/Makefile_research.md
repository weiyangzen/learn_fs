# sources/distributed-fs/ceph-client/drivers/media/spi/Makefile

Purpose: kbuild file mapping media SPI Kconfig symbols to object files.

Important APIs and entries: it adds the CXD2880 frontend include directory with `ccflags-y += -I $(srctree)/drivers/media/dvb-frontends/cxd2880`. It builds `cxd2880-spi.o` for `CONFIG_CXD2880_SPI_DRV` and `gs1662.o` for `CONFIG_VIDEO_GS1662`.

Control flow: during kernel builds, selected config symbols append the corresponding object to the directory target. The comment asks maintainers to keep entries sorted by Kconfig name.

State and persistence: no runtime state. Build outputs are determined by `.config`.

Dependencies and integration points: integrates `drivers/media/spi` with the CXD2880 DVB frontend headers and kbuild symbol expansion from the sibling Kconfig file.

Risks and edge cases: adding new CXD2880 include paths or source splits requires keeping the include flag and object mapping in sync. Sort-order comments are maintenance-only and not enforced.

Test signals: compile with each config enabled independently and together; verify CXD2880 headers resolve and module names match Kconfig help text.
