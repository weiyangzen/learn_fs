<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xen/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/xen/Makefile

## Purpose
Kbuild manifest for the ARM Xen virtual machine DTB.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_VIRT)` lists `xenvm-4.2.dtb`.

## Control flow
Kbuild builds the Xen VM DTB when `CONFIG_ARCH_VIRT` is enabled.

## State and persistence behavior
No runtime state. It persists the virtual platform DTB artifact used for Xen guest or VM boot scenarios.

## Dependencies and integration points
Depends on the Xen VM DTS source, virtual platform Kconfig, DTC, and Xen/ARM boot ABI expectations.

## Risks and edge cases
Virtual platform DTB changes can affect guest boot even without physical hardware. The config gate means it is missed by non-virt builds.

## Test signals
Run `make ARCH=arm dtbs` with `ARCH_VIRT`; boot a Xen guest or run DT schema validation for the virtual DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xen/Makefile -->
