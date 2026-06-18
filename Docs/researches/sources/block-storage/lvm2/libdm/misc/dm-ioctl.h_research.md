# File Research: sources/block-storage/lvm2/libdm/misc/dm-ioctl.h

## Summary
Defines the userspace-visible device-mapper ioctl ABI version 4 structures, command numbers, ioctl macros, constants, and flags. It mirrors the kernel device-mapper ioctl interface used by libdm.

## Main Contents
- Device-mapper naming limits and directory/control-node constants.
- `struct dm_ioctl`, the header for all ioctl payloads.
- Table/status payload structs: `dm_target_spec`, `dm_target_deps`, `dm_name_list`, `dm_target_versions`, `dm_target_msg`.
- Command enum values from `DM_VERSION_CMD` through `DM_GET_TARGET_VERSION_CMD`.
- `_IOWR` ioctl definitions such as `DM_DEV_CREATE`, `DM_TABLE_LOAD`, and `DM_TARGET_MSG`.
- ABI version constants: `DM_VERSION_MAJOR 4`, `DM_VERSION_MINOR 45`, `DM_VERSION_PATCHLEVEL 0`.
- Device/table/status flags including read-only, suspend, buffer-full, uevent, secure-data, deferred-remove, internal-suspend, and IMA measurement flags.

## Important Behavior
Every ioctl uses one contiguous memory buffer beginning with `struct dm_ioctl`. `data_size` is total buffer size and `data_start` points to payload offset.

`dm_ioctl.version` is in/out and recognized commands fill it even on command failure. Device lookup can use UUID instead of name if UUID is provided.

`dm_target_spec.next` has different offset semantics for table load versus status retrieval, and parameter strings immediately follow the struct with alignment padding before the next target.

`dm_name_list` includes optional event number, flags, and UUID storage after the null-terminated name, aligned to an 8-byte boundary.

## State and Lifetime
This header is ABI, not implementation. Consumers allocate and populate buffers according to these layouts before issuing ioctls to the device-mapper control node.

## Risks
Layout and command-number stability are critical; changes must match kernel `dm-ioctl.c`. Flexible array members use legacy zero-length arrays in several structs, so callers must compute buffer sizes carefully.
