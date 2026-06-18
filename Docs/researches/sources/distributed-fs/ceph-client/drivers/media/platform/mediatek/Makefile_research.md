# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Makefile

## Purpose
This Makefile descends into MediaTek media platform subdirectories so their local Makefiles can add objects according to their own Kconfig symbols.

## Important APIs, Types, And Functions
There are no runtime APIs. The build rules are unconditional directory recursion entries: `obj-y += jpeg/`, `mdp/`, `vcodec/`, `vpu/`, and `mdp3/`.

## Control Flow And State
The parent media build always visits these subdirectories when this Makefile is included. Actual object inclusion remains controlled by each child Makefile's config symbols.

## Dependencies And Integration Points
The file mirrors `mediatek/Kconfig` source entries. For this work item, it routes the build to `mediatek/jpeg/Makefile`, where `CONFIG_VIDEO_MEDIATEK_JPEG` controls JPEG driver objects.

## Risks
Unconditional `obj-y` directory traversal requires all listed directories and Makefiles to exist. If a child Makefile has side effects or unconditional objects, they will be evaluated even when no child driver is selected.

## Test Signals
Run standard kernel builds with all MediaTek media symbols disabled and enabled. Confirm that disabling `VIDEO_MEDIATEK_JPEG` prevents JPEG objects from building despite directory traversal.
