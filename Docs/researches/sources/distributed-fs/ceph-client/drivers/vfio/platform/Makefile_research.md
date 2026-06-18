<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/Makefile

## Purpose
This Makefile maps VFIO platform Kconfig symbols to kernel objects. It builds the shared base module, optional reset subdirectory, generic platform binder, and AMBA binder.

## Important APIs, types, and functions
`vfio-platform-base-y` combines `vfio_platform_common.o` and `vfio_platform_irq.o`. `obj-$(CONFIG_VFIO_PLATFORM_BASE)` emits `vfio-platform-base.o` and descends into `reset/`. `vfio-platform-y` maps to `vfio_platform.o`, and `vfio-amba-y` maps to `vfio_amba.o`.

## Control flow
The build dependency mirrors Kconfig: once the base symbol is enabled, common code and reset handlers can be built. The generic and AMBA binders are independent object modules that depend on the base symbols and exported functions at link/load time.

## State and persistence behavior
No runtime state exists. The file persists build composition by deciding which object code is part of the kernel image or module set.

## Dependencies and integration points
The Makefile depends on the platform Kconfig symbols and on reset Makefile contents. It integrates common code with bus-specific frontends, so symbol exports in `vfio_platform_common.c` and `vfio_platform_irq.c` must remain available to both binders.

## Risks and test signals
Build risks include missing reset subdirectory descent, mismatched object names, or unresolved exports if common code changes. Test signals are clean builds for built-in and module combinations of `VFIO_PLATFORM_BASE`, `VFIO_PLATFORM`, `VFIO_AMBA`, and reset modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Makefile -->
