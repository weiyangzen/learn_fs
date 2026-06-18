# sources/distributed-fs/ceph-client/include/linux/usb_usual.h

## Purpose
This header centralizes USB mass-storage unusual-device quirk flags and exposes shared device ID and ignore helpers.

## Important APIs, types, and functions
`US_DO_ALL_FLAGS` enumerates quirk flags such as single-LUN behavior, bad sense, capacity quirks, no report opcodes, ignore-residue, no UAS, and others by expanding `US_FLAG`. It exports `usb_usual_ignore_device()` and `usb_storage_usb_ids[]`.

## Control flow, state, and persistence
USB storage and UAS probing use the shared ID table and quirk flags to decide whether a device should bind and which protocol workarounds apply. There is no local runtime state; flags are static driver metadata.

## Dependencies and integration points
It includes USB storage definitions and integrates usb-storage, UAS, and device ID matching.

## Risks and test signals
Risks include conflicting quirk bits, misapplied ignore behavior, and duplicate device IDs across storage transports. Tests should probe devices with known unusual entries, verify selected flags, and ensure UAS is suppressed where required.
