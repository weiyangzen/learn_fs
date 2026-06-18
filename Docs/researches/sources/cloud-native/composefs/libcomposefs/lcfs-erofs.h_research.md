# sources/cloud-native/composefs/libcomposefs/lcfs-erofs.h

## Purpose
`lcfs-erofs.h` defines the public composefs-on-EROFS image header. It is the magic/version/flags contract that lets readers identify composefs images before interpreting the embedded EROFS filesystem.

## Important APIs, Types, And Functions
`LCFS_EROFS_VERSION` is `1`, `LCFS_EROFS_MAGIC` is `0xd078629aU`, and `LCFS_EROFS_FLAGS_HAS_ACL` records whether ACL xattrs are present. `struct lcfs_erofs_header_s` stores magic, version, flags, composefs format version, and unused reserved words in a packed layout.

## Control Flow
Writers emit this header before the EROFS superblock. Loaders and mounters read it first, validate magic/version, inspect flags, and use `composefs_version` for compatibility reporting.

## State And Persistence
This header is persistent on disk at the beginning of every composefs EROFS image. Its packed layout and endian conversion in writer/reader paths are part of the image ABI.

## Dependencies And Integration Points
It is included by writer, loader, mounter, and tests. `lcfs-mount.c` uses flags to decide whether to mount EROFS with `noacl`; `lcfs-writer.c` uses the header to report image version.

## Risks
Changing field order, size, magic, or version breaks image compatibility. Reserved fields should remain zeroed until a documented extension consumes them.

## Test Signals
Image checksum fixtures, `lcfs_version_from_fd`, `test-lcfs.c` handcrafted image setup, and mount tests all validate this header path indirectly.
