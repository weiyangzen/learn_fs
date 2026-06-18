# sources/cloud-native/composefs/libcomposefs/lcfs-mount.h

## Purpose
`lcfs-mount.h` is the public libcomposefs mount API. It defines mount flags, option structure, public error aliases, and entry points for mounting from a path or fd.

## Important APIs, Types, And Functions
Error aliases are `ENOVERITY`, `EWRONGVERITY`, and `ENOSIGNATURE`. `enum lcfs_mount_flags_t` includes require-verity, readonly, idmap, and try-verity bits plus a mask. `struct lcfs_mount_options_s` contains object dirs, upper/work dirs, expected fs-verity digest, flags, idmap fd, image mount dir, and reserved ABI fields. Public functions are `lcfs_mount_image` and `lcfs_mount_fd`.

## Control Flow
Callers populate options, pass an image path or fd and mountpoint, and receive `0` or `-1` with `errno` set. Lower-level mount sequencing is implemented in `lcfs-mount.c`.

## State And Persistence
This header defines no state itself. Option fields drive mount creation and transient kernel mount state.

## Dependencies And Integration Points
It includes standard C and system stat headers and is installed by `libcomposefs/meson.build`. Tools such as `mount.composefs` use it.

## Risks
Reserved fields are part of ABI padding and should not be repurposed casually. Flags outside `LCFS_MOUNT_FLAGS_MASK` are rejected.

## Test Signals
Mount digest behavior in `test-units.sh` and integration mounting validate this API indirectly.
