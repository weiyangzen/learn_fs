<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/Kconfig

## Purpose
This Kconfig file defines VFIO support for platform and AMBA devices, plus the menu that includes optional VFIO platform reset handlers. It scopes the platform VFIO family to ARM, ARM64, or compile-test builds.

## Important APIs, types, and functions
The important symbols are `VFIO_PLATFORM_BASE`, `VFIO_PLATFORM`, and `VFIO_AMBA`. `VFIO_PLATFORM_BASE` is a hidden tristate that selects `VFIO_VIRQFD`, providing the common platform base and IRQ eventfd support. `VFIO_PLATFORM` enables the generic platform bus binder. `VFIO_AMBA` enables the deprecated AMBA binder when `ARM_AMBA` or `COMPILE_TEST` is available.

## Control flow
Kconfig selection flows from a user-visible bus driver to the shared base. Selecting either generic platform support or AMBA support selects `VFIO_PLATFORM_BASE`; the reset-driver submenu is visible only when the base is enabled. The file then sources `drivers/vfio/platform/reset/Kconfig`.

## State and persistence behavior
There is no runtime state. The persistent effect is the kernel configuration choice that decides which objects are built into the kernel or as modules.

## Dependencies and integration points
This file integrates with `drivers/vfio/platform/Makefile`, the reset subdirectory Kconfig, and generic VFIO virqfd support. The AMBA option is explicitly deprecated in help text, which affects maintenance expectations.

## Risks and test signals
Risk centers on accidental enablement without reset support, because the generic platform driver defaults to requiring reset at runtime. Configuration tests should cover `allyesconfig`, module builds, `COMPILE_TEST`, ARM/ARM64 visibility, and builds where only `VFIO_AMBA` or only `VFIO_PLATFORM` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/Kconfig -->
