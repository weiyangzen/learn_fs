# `sources/distributed-fs/ceph-client/include/linux/usb/iowarrior.h`

## Purpose

`iowarrior.h` defines the userspace ioctl ABI for Code Mercenaries IOWarrior USB devices. It describes read/write ioctls and the legacy-compatible information structure returned by `IOW_GETINFO`.

## Important APIs, Types, and Constants

- `CODEMERCS_MAGIC_NUMBER` is the ioctl type value.
- `IOW_WRITE` and `IOW_READ` pass `__u8 *` buffers for device report writes and reads.
- `struct iowarrior_info` exposes vendor, product, nine-byte serial string, revision, USB speed, power draw, interface number, and report size.
- `IOW_GETINFO` returns `struct iowarrior_info` to userspace.

## Control Flow and Lifetimes

Userspace opens the IOWarrior character device and issues ioctls. The driver copies data between userspace buffers and USB reports, or fills the info structure from probed descriptor/interface state. This header only fixes the ABI; implementation handles USB URB submission and device lifetime.

## State and Persistence Behavior

The ioctl definitions are persistent ABI. Device information is runtime state derived from descriptors and driver bookkeeping. There is no on-disk state.

## Dependencies and Integration Points

It depends on ioctl encoding macros and fixed-size UAPI integer types. It integrates the USB IOWarrior driver with legacy 2.4-era userspace tools that expect this info ioctl.

## Risks and Edge Cases

ABI changes would break userspace. The `serial[9]` field is fixed and may be empty. Read/write ioctls use raw pointers, so driver implementation must validate copy sizes and disconnected-device paths carefully.

## Test Signals

Compile the IOWarrior driver, run ioctl ABI tests for all commands, verify 32/64-bit userspace compatibility, disconnect during ioctl, inspect info fields against descriptors, and test devices with and without serial numbers.
