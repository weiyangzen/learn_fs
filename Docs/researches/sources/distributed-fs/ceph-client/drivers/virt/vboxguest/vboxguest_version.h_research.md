# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_version.h

## Purpose
`vboxguest_version.h` defines the VirtualBox Guest Additions version values reported by the in-kernel guest driver to the VirtualBox host. It is a small protocol/versioning header rather than executable logic.

## Important APIs, types, and functions
The exported compile-time constants are `VBG_VERSION_MAJOR`, `VBG_VERSION_MINOR`, `VBG_VERSION_BUILD`, `VBG_SVN_REV`, and `VBG_VERSION_STRING`. `vboxguest_core.c` uses them in `vbg_report_guest_info` to fill `struct vmmdev_guest_info2`.

## Control flow
There is no runtime control flow in this header. During core initialization, the version constants are copied into a VMMDev guest-info request and sent to the host before the driver reports itself active.

## State and persistence
The constants become runtime protocol data only when included in the guest-info request. They do not persist in the guest, but the host can use them to decide which guest-addition features to enable or assume.

## Dependencies and integration points
The header is consumed by the VirtualBox guest core and must stay synchronized with the upstream/out-of-tree VirtualBox versioning expectations when features are ported.

## Risks and test signals
Risks are stale or misleading version values that cause host-side feature gating mismatches, especially if the mainline driver diverges from upstream VirtualBox capabilities. Test signals include host version negotiation across old/new VirtualBox hosts and validating the host sees the expected additions version string and feature behavior.
