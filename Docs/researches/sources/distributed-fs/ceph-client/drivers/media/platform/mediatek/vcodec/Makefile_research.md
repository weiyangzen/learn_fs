# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Makefile

## Purpose
This top-level Makefile includes the MediaTek vcodec common, encoder, and decoder subdirectories.

## Important APIs, Types, And Functions
It adds `common/`, `encoder/`, and `decoder/` to `obj-y`, delegating actual module object selection to each subdirectory Makefile and Kconfig symbols.

## Control Flow
During kernel build traversal, this file ensures all vcodec subdirectories are visited so their `obj-$(CONFIG_VIDEO_MEDIATEK_VCODEC)` rules can contribute objects.

## State, Persistence, And Dependencies
There is no runtime state. Build state depends on Kbuild and `CONFIG_VIDEO_MEDIATEK_VCODEC`.

## Integration Points
This file links the vcodec subtree into `drivers/media/platform/mediatek` build traversal. The common library objects are then shared by encoder and decoder modules.

## Risks
Using `obj-y` means subdirectory traversal always happens when the parent directory is visited; incorrect subdirectory Makefiles would still be evaluated. Omitting a subdir would silently remove that driver half from builds.

## Test Signals
Kbuild coverage that produces `mtk-vcodec-common`, `mtk-vcodec-dec`, `mtk-vcodec-dec-hw`, and encoder objects for enabled configs.
