# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/Makefile

## Purpose
This Makefile defines the kernel build composition for the Intel fm10k Ethernet Switch Host Interface driver.

## Important APIs, types, and functions
The key build target is `obj-$(CONFIG_FM10K) += fm10k.o`. The `fm10k-y` object list includes main, common, PCI, netdev, ethtool, PF/VF, mailbox, SR-IOV, and TLV implementation files. Optional objects are `fm10k_debugfs.o` under `CONFIG_DEBUG_FS` and `fm10k_dcbnl.o` under `CONFIG_DCB`.

## Control flow
There is no runtime flow. Kbuild links listed objects into the `fm10k` module/built-in object when `CONFIG_FM10K` is enabled, and conditionally includes debugfs/DCB support based on kernel config.

## State and persistence behavior
No runtime state is stored here. Build configuration controls which driver features exist in the resulting binary, which indirectly affects runtime interfaces such as debugfs and DCB netlink ops.

## Dependencies and integration points
The Makefile integrates with Linux Kbuild and the driver source layout. The object list must match symbols declared in `fm10k.h` and referenced by fm10k main/PCI/netdev code.

## Risks
Omitting a required object causes unresolved symbols or missing runtime functionality. Including optional files without their configs would break builds where dependent kernel APIs are disabled. Reordering is generally low risk, but missing common/PF/VF/mailbox/TLV objects would be fatal.

## Test signals
Build `CONFIG_FM10K=m` and `=y` with and without `CONFIG_DEBUG_FS`/`CONFIG_DCB`. Confirm `modinfo`, module load, and optional debugfs/DCB interfaces match the selected config.
