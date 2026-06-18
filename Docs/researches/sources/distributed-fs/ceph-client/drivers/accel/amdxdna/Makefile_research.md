# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Makefile

## Purpose
This Makefile defines the object list for the AMD XDNA driver module.

## Important APIs, Types, And Functions
`amdxdna-y` lists the compilation units linked into `amdxdna.o`, including AIE2 context, error, message, PCI, PM, PSP, SMU, solver, GEM, IOMMU, mailbox, sysfs, user-buffer, and NPU register files. `obj-$(CONFIG_DRM_ACCEL_AMDXDNA) = amdxdna.o` connects the object to the Kconfig symbol.

## Control Flow
kbuild compiles each listed `.o` and links them into a single built-in or module object depending on `CONFIG_DRM_ACCEL_AMDXDNA`.

## State, Dependencies, Integration, Risks, And Tests
Build state is the object list. Risks include missing new source files, stale deleted file references, and link-order issues for init/exit or exported helper dependencies. Test signals are `make M=drivers/accel/amdxdna`, modpost symbol checks, and verifying that all expected feature files are included in `amdxdna.o`.
