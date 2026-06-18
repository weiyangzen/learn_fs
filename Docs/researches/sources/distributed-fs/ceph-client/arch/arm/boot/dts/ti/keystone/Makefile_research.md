<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/Makefile

## Purpose
Kbuild manifest for TI Keystone ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_KEYSTONE)` lists K2HK, K2L, K2E, K2G EVM, and K2G ICE DTBs.

## Control flow
The DTBs are built when `CONFIG_ARCH_KEYSTONE` is enabled.

## State and persistence behavior
No runtime state. The file persists board DTB publication for Keystone platforms.

## Dependencies and integration points
Depends on Keystone DTS files, SoC Kconfig, DTC, and binding schemas for TI Keystone peripherals.

## Risks and edge cases
Renamed DTS files or missing board entries break build coverage. Board DTBs must stay aligned with boot firmware expectations and Keystone interrupt/timer bindings.

## Test signals
Run `make ARCH=arm dtbs` with Keystone enabled and `make ARCH=arm dtbs_check` for K2 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/Makefile -->
