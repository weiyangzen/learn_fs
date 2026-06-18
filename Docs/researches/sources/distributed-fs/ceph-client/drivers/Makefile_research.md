# sources/distributed-fs/ceph-client/drivers/Makefile

## Purpose
This is the top-level kernel drivers build Makefile. It maps Kconfig symbols to driver subdirectories and defines the broad build order for built-in and modular driver objects.

## Important APIs, Types, And Functions
There are no runtime APIs. The core interface is kbuild syntax: `obj-y` for always-descended directories and `obj-$(CONFIG_...)` for conditional descent. The acceleration integration point is `obj-$(CONFIG_DRM_ACCEL) += accel/`. The file also includes subsystem ordering comments for dependencies like GPIO after pinctrl, DMA early, and GPU after char/IOMMU.

## Control Flow
During kbuild, the top-level build system expands enabled `obj-*` entries and descends into selected directories. Built-in order matters for initcall/link ordering and for availability of infrastructure expected by later subsystems.

## State, Dependencies, Integration, Risks, And Tests
State is build graph state derived from `.config`. Dependencies are directory names and Kconfig symbols. Risks include incorrect conditional symbols preventing driver compilation, ordering regressions, and typoed directories. Test signals are `make drivers/`, allmodconfig/allnoconfig coverage, and confirming `drivers/accel/` is built only with `CONFIG_DRM_ACCEL`.
