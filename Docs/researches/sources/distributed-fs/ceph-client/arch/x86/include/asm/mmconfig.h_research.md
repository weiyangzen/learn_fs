# sources/distributed-fs/ceph-client/arch/x86/include/asm/mmconfig.h

## Purpose
Declares x86 PCI MMCONFIG enablement quirks for AMD systems.

## Important APIs, Types, And Functions
When `CONFIG_PCI_MMCONFIG` is enabled, exports `fam10h_check_enable_mmcfg()` and `check_enable_amd_mmconf_dmi()`. Otherwise both compile to empty stubs.

## Control Flow
Boot-time PCI setup can call these helpers to detect and enable memory-mapped PCI config space on systems that need family 10h or DMI-based quirks.

## State And Persistence
No header-owned state. Implementations may update PCI MMCONFIG availability for the booted kernel.

## Dependencies And Integration Points
Integrates with x86 PCI initialization, ACPI/firmware MMCONFIG discovery, and AMD platform quirks.

## Risks And Edge Cases
Enabling incorrect MMCONFIG ranges can break PCI config access. Stubs must allow non-MMCONFIG builds to compile without conditional callers.

## Test Signals
Boot PCI enumeration on AMD family 10h and affected DMI systems, plus builds with `CONFIG_PCI_MMCONFIG` disabled.
