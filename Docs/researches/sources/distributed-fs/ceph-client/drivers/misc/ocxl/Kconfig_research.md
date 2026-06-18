# sources/distributed-fs/ceph-client/drivers/misc/ocxl/Kconfig

## Purpose
This Kconfig file controls OpenCAPI/OCXL support. It defines the base dependency symbol and the user-visible OCXL driver option for coherent accelerators exposed under `/dev/ocxl/`.

## Important APIs, types, and functions
It defines `OCXL_BASE` as a bool selecting `PPC_COPRO_BASE`, and `OCXL` as a tristate "OpenCAPI coherent accelerator support" depending on `HOTPLUG_PCI_POWERNV`, selecting `OCXL_BASE`, defaulting to module.

## Control flow and state
There is no runtime flow. Enabling `OCXL` includes the OCXL driver build and support infrastructure for PowerNV OpenCAPI devices.

## State and persistence behavior
No runtime state exists in Kconfig. It affects build-time configuration only.

## Dependencies and integration points
The option integrates with PowerPC/PowerNV PCI hotplug and coprocessor infrastructure. Help text distinguishes OCXL/OpenCAPI from IBM CAPI `CONFIG_CXL`.

## Risks and test signals
Risks are dependency drift with architecture-specific APIs and accidental build exposure on unsupported platforms. Test signals include PowerNV builds, module builds, dependency resolution for `PPC_COPRO_BASE`, and absence from unsupported platform configs.
