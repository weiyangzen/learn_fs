# sources/distributed-fs/ceph-client/drivers/rapidio/Makefile

Purpose: builds the RapidIO core and optional RapidIO modules according to Kconfig symbols.

Important entries: `obj-$(CONFIG_RAPIDIO) += rapidio.o` builds the aggregate core object. `rapidio-y := rio.o rio-access.o rio-driver.o rio-sysfs.o` supplies base subsystem, config access, bus/driver model, and sysfs pieces. Optional objects include `rio-scan.o` for basic enumeration and `rio_cm.o` for channelized messaging. It always descends into `switches/` and `devices/` when `CONFIG_RAPIDIO` is enabled. `subdir-ccflags-$(CONFIG_RAPIDIO_DEBUG) := -DDEBUG` enables debug macros throughout the subtree.

Control flow and integration: the build system links `rio-access.c` and `rio-driver.c` into the core `rapidio` object, making exported symbols available to device drivers such as `tsi721` and user-facing drivers such as `rio_mport_cdev`. Subdirectories compile additional drivers based on their own Makefiles and config symbols.

State and persistence: no runtime state; build products persist as kernel objects/modules depending on tristate choices.

Dependencies: Linux kbuild, top-level RapidIO Kconfig symbols, and source files in this directory plus child directories.

Risks: because debug flags are applied as subdir ccflags, enabling `RAPIDIO_DEBUG` can significantly increase log volume across multiple drivers. If `CONFIG_RAPIDIO=m`, child built-in assumptions must still be module-safe.

Test signals: inspect `make V=1 drivers/rapidio/` output for expected object lists under `RAPIDIO=y/m`, `RAPIDIO_ENUM_BASIC`, `RAPIDIO_CHMAN`, and `RAPIDIO_DEBUG`.
