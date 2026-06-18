# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Kconfig

Purpose: top-level Kconfig menu entry for Raspberry Pi media platform drivers.

Important APIs/types/functions: declares a comment label and sources `drivers/media/platform/raspberrypi/pisp_be/Kconfig` and `drivers/media/platform/raspberrypi/rp1-cfe/Kconfig`.

Control flow: Kconfig inclusion only; it delegates actual symbols to child directories.

State and persistence: no runtime state. It affects kernel configuration state by making child driver options visible.

Dependencies and integration: integrated from the media platform Kconfig tree. Child symbols provide their own dependency and select clauses.

Risks: if source paths drift, Raspberry Pi drivers disappear from menuconfig/builds. Ordering is simple and has no symbol dependency between the two children.

Test signals: `make menuconfig` visibility and `make olddefconfig` parsing with `CONFIG_VIDEO_RASPBERRYPI_PISP_BE` and `CONFIG_VIDEO_RP1_CFE`.
