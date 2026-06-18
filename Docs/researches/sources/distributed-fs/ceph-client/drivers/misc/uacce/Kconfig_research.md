# sources/distributed-fs/ceph-client/drivers/misc/uacce/Kconfig

## Purpose
`uacce/Kconfig` declares the build option for UACCE, the Accelerator Framework for User Land.

## Important APIs, Types, and Functions
The single symbol is `CONFIG_UACCE`, a tristate option labelled "Accelerator Framework for User Land". It depends on `IOMMU_API` and points users to the UAPI header `include/uapi/misc/uacce/uacce.h` and documentation `Documentation/misc-devices/uacce.rst`.

## Control Flow
Kconfig has no runtime control flow. Selecting `CONFIG_UACCE=y` builds the framework into the kernel; `m` builds it as a module; `n` excludes it.

## State and Persistence
No runtime state is defined here. The selected Kconfig value controls compilation and availability.

## Dependencies and Integration Points
The dependency on `IOMMU_API` reflects UACCE's use of IOMMU/SVA features for userspace accelerator access. The symbol is consumed by the local Makefile to build `uacce.o`.

## Risks and Edge Cases
If accelerator drivers expect UACCE but `IOMMU_API` is disabled, the framework cannot be selected. The help text explicitly advises unsure users to say no because the option exposes direct userspace accelerator interfaces.

## Test Signals
Check Kconfig visibility with and without `IOMMU_API`, built-in and module builds, and accelerator-driver dependency chains that select or depend on `UACCE`.
