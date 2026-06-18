<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arcfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/arcfb.h

## Purpose
Defines two framebuffer ioctls used by the ARCFB driver for event wait and secondary control retrieval.

## Important APIs, Types, And Functions
`FBIO_WAITEVENT` is an `_IO` ioctl on framebuffer magic `F`. `FBIO_GETCONTROL2` is an `_IOR` ioctl returning a `size_t` control value.

## Control Flow
Userspace opens the framebuffer device, waits for a device event with `FBIO_WAITEVENT`, and reads auxiliary control state through `FBIO_GETCONTROL2`.

## State And Persistence
The header defines no storage. State is transient framebuffer/device event and control state.

## Dependencies And Integration Points
Integrates with Linux framebuffer ioctls and ARCFB-specific userspace tools.

## Risks And Edge Cases
`size_t` in an ioctl payload can be compat-sensitive across 32/64-bit userspace. Blocking wait semantics and signal interruption need userspace handling.

## Test Signals
Compat layout checks, ioctl availability tests, event wakeup behavior, and invalid fd/device rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arcfb.h -->
