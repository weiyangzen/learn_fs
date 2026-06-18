# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.h

## Purpose
This header defines vcodec debugfs data structures and exposes debugfs lifecycle helpers, with no-op stubs when debugfs is disabled.

## Important APIs, Types, And Functions
`enum mtk_vdec_dbgfs_log_index` defines decoder report selectors for picture info and format. `struct mtk_vcodec_dbgfs_inst` links a decoder context into the debugfs instance list. `struct mtk_vcodec_dbgfs` stores the list, root dentry, mutex, command buffer, buffer size, and instance count. Public functions are `mtk_vcodec_dbgfs_create()`, `mtk_vcodec_dbgfs_remove()`, `mtk_vcodec_dbgfs_init()`, and `mtk_vcodec_dbgfs_deinit()`, with inline stubs under `!CONFIG_DEBUG_FS`.

## Control Flow
No direct execution. The API lets probe initialize the tree, open/release add or remove decoder instances, and remove tear the tree down.

## State, Persistence, And Dependencies
Debugfs state is runtime-only and stored inside codec device structs. The header forward-declares decoder device/context types to avoid broad include dependency.

## Integration Points
Included by decoder driver state and common debugfs implementation. Encoder state uses the same aggregate debugfs struct.

## Risks
Stub functions must match the real prototypes exactly to keep non-debugfs builds compiling. The command buffer has a fixed 1024-byte size.

## Test Signals
Builds with and without `CONFIG_DEBUG_FS`, decoder open/release list lifecycle, and debugfs deinit during module removal.
