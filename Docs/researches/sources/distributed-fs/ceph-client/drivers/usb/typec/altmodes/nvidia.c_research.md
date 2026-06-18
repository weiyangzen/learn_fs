# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/nvidia.c

## Purpose

`nvidia.c` implements the NVIDIA USB Type-C Alternate Mode wrapper for VirtualLink devices. It binds NVIDIA's SVID and delegates behavior to the DisplayPort altmode implementation.

## Important APIs, Types, and Functions

`nvidia_altmode_probe()` checks `alt->svid` for `USB_TYPEC_NVIDIA_VLINK_SID` and calls `dp_altmode_probe()`. `nvidia_altmode_remove()` calls `dp_altmode_remove()` for the same SVID. The file defines a Type-C ID table and registers `typec_nvidia` through `module_typec_altmode_driver()`.

## Control Flow

When the Type-C altmode bus discovers the NVIDIA SVID, probe delegates to DisplayPort because VirtualLink carries DisplayPort semantics. Remove delegates cleanup to the same DisplayPort helper. Unsupported SVIDs return `-ENOTSUPP`, though the ID table should only match the NVIDIA SVID.

## State and Persistence Behavior

This wrapper stores no private state. Any runtime state is the `struct dp_altmode` allocated by `displayport.c` and attached to the altmode device. There is no persistence.

## Dependencies and Integration Points

It depends on `TYPEC_NVIDIA_ALTMODE`, `TYPEC_DP_ALTMODE`, Type-C altmode APIs, NVIDIA VirtualLink SVID constants, and `displayport.h`. It integrates VirtualLink devices with the DisplayPort driver module.

## Risks and Edge Cases

The wrapper assumes VirtualLink can be treated exactly as DisplayPort altmode by the shared implementation. If NVIDIA-specific VDM behavior diverges, this delegation would be insufficient. Kconfig dependency on DisplayPort is required for linking and behavior.

## Test Signals

Build `typec_nvidia`, verify the module ID table matches `USB_TYPEC_NVIDIA_VLINK_SID`, attach or emulate a VirtualLink altmode, and confirm DisplayPort negotiation, sysfs attributes, HPD, and cleanup function through the delegated path.
