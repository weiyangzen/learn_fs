# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.c

## Purpose
This file implements optional debugfs support for MediaTek vcodec decoder and encoder devices. Decoder debugfs can list active instances, picture information, output/capture formats, and runtime debug level controls.

## Important APIs, Types, And Functions
`mtk_vcodec_dbgfs_init()` creates either `vcodec-dec` or `vcodec-enc` debugfs roots. Decoder init creates `mtk_v4l2_dbg_level`, `mtk_vcodec_dbg`, and `vdec`. `mtk_vcodec_dbgfs_create()` and `mtk_vcodec_dbgfs_remove()` maintain the decoder instance list. `mtk_vdec_dbgfs_write()` stores command text; `mtk_vdec_dbgfs_read()` parses `-help`, `-picinfo`, and `-format`, then renders information for each instance. `mtk_vcodec_dbgfs_deinit()` removes the tree.

## Control Flow
Probe calls init. Each decoder open adds an instance and each release removes it. Userspace writes a command string to debugfs and reads back a synthesized report. Deinit removes the whole root.

## State, Persistence, And Dependencies
Debugfs state lives in `struct mtk_vcodec_dbgfs`: list head, root dentry, mutex, command buffer, command size, and instance count. It is runtime-only and disappears on driver unload. Dependencies include debugfs, decoder/encoder private headers, and common debug globals.

## Integration Points
Decoder probe/release and encoder probe paths call the exported functions. Common util exports the debug-level globals that debugfs exposes.

## Risks
Read buffer sizing is a fixed estimate of 200 bytes per instance, so long output can truncate silently. The instance list is protected by `dbgfs_lock` during reads but create/remove list updates are not explicitly locked in this file. The decoder debugfs file is created with write-only mode while a read handler is present, which deserves permissions review.

## Test Signals
Debugfs smoke tests with zero/multiple decoder instances, concurrent open/close while reading, command parsing for help/picinfo/format, and debugfs disabled builds.
