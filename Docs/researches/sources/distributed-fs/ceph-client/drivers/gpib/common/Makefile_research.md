# sources/distributed-fs/ceph-client/drivers/gpib/common/Makefile

Purpose: declares the common GPIB kernel module build target. `obj-$(CONFIG_GPIB_COMMON) += gpib_common.o` makes the subsystem core conditional on `CONFIG_GPIB_COMMON`, and `gpib_common-objs := gpib_os.o iblib.o` links the OS/device-file layer with the exported bus operation library.

Important build APIs: the file uses standard kbuild composite object syntax. `gpib_os.o` contributes character-device registration, ioctl dispatch, board lifecycle, driver registration, PCI selection helpers, timers, event queues, and status queues. `iblib.o` contributes the reusable IEEE-488 operations used by the ioctl layer and hardware adapters.

Control flow and integration: all adapter Makefiles in sibling folders build separate board modules that call symbols exported by this common module. The common module must be available before board modules can resolve `gpib_register_driver`, `gpib_request_pseudo_irq`, `push_gpib_event`, and PCI helper exports.

State and persistence behavior: no runtime state is present in the Makefile itself. Its main effect is link composition: `gpib_os.c` and `iblib.c` share one module namespace, one `MODULE_ALIAS_CHARDEV_MAJOR(GPIB_CODE)`, and one exported symbol provider.

Dependencies: depends on Kconfig selecting `CONFIG_GPIB_COMMON` and on kbuild compiling both C files in the same directory with access to the GPIB include tree.

Risks: if new common source files are added but not included in `gpib_common-objs`, adapters may compile but fail to link or miss exported behavior. If `CONFIG_GPIB_COMMON` is disabled while board drivers are enabled, board modules will have unresolved common symbols unless Kconfig prevents that combination.

Test signals: run kernel build coverage with `CONFIG_GPIB_COMMON=m` and at least one adapter enabled; inspect `modinfo gpib_common`; verify `gpib_common.ko` contains both ioctl and library symbols via `nm`/`modpost`.
