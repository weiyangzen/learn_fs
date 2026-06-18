# sources/distributed-fs/ceph-client/include/linux/root_dev.h

## Purpose
`root_dev.h` exposes the kernel's selected root block device identifier.

## Important APIs, types, and functions
The header declares the global `ROOT_DEV` device number used by boot and mount code to locate the initial root filesystem device.

## Control flow, state, and persistence
Boot parsing and early block-device discovery assign `ROOT_DEV`; root-mount code consumes it when mounting the real root. The value persists as global kernel state for the booted system but the header itself has no logic.

## Dependencies and integration points
It depends on `dev_t` from kernel types and integrates with init/do_mounts code, root= command-line parsing, initramfs/rootfs handoff, and block-device naming.

## Risks and test signals
Risks include stale or unset `ROOT_DEV`, mismatched major/minor numbers after device discovery races, and confusion between initramfs root and real root. Test signals are boot tests with root by device number, UUID/PARTUUID, NFS/initramfs configurations, and failure-path diagnostics for missing root devices.
