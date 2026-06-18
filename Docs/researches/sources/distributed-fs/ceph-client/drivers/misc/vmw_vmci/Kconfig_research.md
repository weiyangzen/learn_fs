# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/Kconfig

## Purpose
`vmw_vmci/Kconfig` declares the VMware VMCI driver option, enabling Virtual Machine Communication Interface support for host-guest and guest-guest communication through VMware's virtual device.

## Important APIs, Types, and Functions
The single symbol is `CONFIG_VMWARE_VMCI`, a tristate option labelled "VMware VMCI Driver". It depends on `(X86 || ARM64) && !CPU_BIG_ENDIAN && PCI` and documents that the module name is `vmw_vmci`.

## Control Flow
Kconfig has no runtime flow. The symbol controls whether the VMCI driver is omitted, built in, or built as a module.

## State and Persistence
No runtime state is present. The selected Kconfig value determines build inclusion.

## Dependencies and Integration Points
The architecture, endian, and PCI dependencies match the VMCI virtual PCI device support. Other drivers, such as the VMware balloon driver, can use VMCI APIs when the VMCI driver is available.

## Risks and Edge Cases
Big-endian and non-PCI configurations cannot select the driver. Built-in users that want VMCI services must consider init ordering; the balloon driver explicitly uses `late_initcall()` partly to allow VMCI to probe first.

## Test Signals
Check Kconfig visibility on x86 and arm64 little-endian PCI builds, module output as `vmw_vmci`, and dependent VMware features with built-in versus module configurations.
