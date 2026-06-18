# sources/cloud-native/composefs/libcomposefs/lcfs-writer.h

## Purpose
`lcfs-writer.h` is the installed public API for constructing, inspecting, loading, and writing composefs node trees and fs-verity digests.

## Important APIs, Types, And Functions
It defines build flags, `LCFS_DIGEST_SIZE`, format/flags enums, version constants, inline/xattr limits, callback types, `struct lcfs_write_options_s`, `struct lcfs_read_options_s`, node lifecycle APIs, load APIs, xattr APIs, payload/content APIs, child/tree APIs, inode metadata APIs, digest APIs, `lcfs_build`, and `lcfs_write_to`.

## Control Flow
Users can build nodes manually or call `lcfs_build`, configure write options, then write an image through a callback. Image loading can use bytes, fd, or filtered read options.

## State And Persistence
The header defines the ABI contract for in-memory node manipulation and image generation options. Reserved fields preserve space for future ABI evolution.

## Dependencies And Integration Points
Installed by Meson under `libcomposefs`. It is included by tools, tests, internal headers, and potential external consumers.

## Risks
Some setters such as `lcfs_node_set_mode` do not validate; callers should prefer `lcfs_node_try_set_mode` or rely on write-time validation. Build flags have interactions such as skip-xattrs conflicting with user-xattrs.

## Test Signals
`test-lcfs.c` compiles directly against this header. All tool-based tests validate its ABI through libcomposefs.
