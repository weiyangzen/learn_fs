# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Makefile

Purpose: top-level build dispatcher for Raspberry Pi media platform driver subdirectories.

Important APIs/types/functions: unconditional `obj-y += pisp_be/` and `obj-y += rp1-cfe/` let child Makefiles decide whether to produce objects based on Kconfig symbols.

Control flow: kbuild descends into both subdirectories during the media platform build.

State and persistence: no runtime state; build graph only.

Dependencies and integration: relies on child Makefiles for `CONFIG_VIDEO_RASPBERRYPI_PISP_BE` and `CONFIG_VIDEO_RP1_CFE` object selection.

Risks: unconditional descent is normal but requires child directories to remain build-clean even when symbols are disabled.

Test signals: allmodconfig and disabled-config builds should both parse these directories without missing-object or missing-header failures.
