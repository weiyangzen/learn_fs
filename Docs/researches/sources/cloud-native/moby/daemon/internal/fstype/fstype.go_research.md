## sources/cloud-native/moby/daemon/internal/fstype/fstype.go

Purpose: Defines filesystem magic constants and a cross-platform `GetFSMagic` wrapper.

Important APIs/types: `FsMagic` is a `uint32`. Constants enumerate known filesystem IDs including aufs, btrfs, extfs, overlayfs, xfs, zfs, fuse, tmpfs, and `FsMagicUnsupported`. `FsNames` maps IDs to human-readable names. `GetFSMagic(rootpath)` delegates to the platform implementation.

Control flow and state: The file is pure definitions plus one delegation function. `FsNames` is mutable package-level state but is intended as a constant lookup table.

Dependencies and integration: Used by daemon storage/driver code that needs to branch or report based on backing filesystem type. Platform-specific logic lives in `fstype_linux.go` and `fstype_unsupported.go`.

Risks: Filesystem magic values must stay accurate. Unknown filesystems are not automatically present in `FsNames`. Because `FsNames` is exported mutable state, accidental writes could affect diagnostics or behavior.

Test signals: No tests are listed for this package in the requested set.
