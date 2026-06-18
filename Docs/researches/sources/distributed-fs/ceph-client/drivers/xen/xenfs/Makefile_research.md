<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/Makefile

## Purpose
This kbuild file defines the Xen filesystem module composition. It builds `xenfs.o` when `CONFIG_XENFS` is enabled and conditionally adds dom0-only xenstored support and hypervisor-symbol exposure.

## Important APIs, types, and functions
It is declarative kbuild. `xenfs-y` always includes `super.o`; `xenfs-$(CONFIG_XEN_DOM0)` adds `xenstored.o`; `xenfs-$(CONFIG_XEN_SYMS)` adds `xensyms.o`.

## Control flow
Kbuild evaluates config symbols and links the selected objects into the `xenfs` module or built-in object. The final object supplies the `xenfs` filesystem type and optional files under its root.

## State and persistence
No runtime state is stored here. The persistent effect is build graph selection from `.config`.

## Dependencies and integration points
It binds Xen config choices to source files in `drivers/xen/xenfs`. `super.c` references file operations that only exist when the corresponding object is included.

## Risks and test signals
Risks are missing conditional objects when `super.c` exposes optional files, or stale object names. Test signals are `CONFIG_XENFS=y/m`, dom0/non-dom0 builds, `CONFIG_XEN_SYMS` toggles, and module link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/Makefile -->
