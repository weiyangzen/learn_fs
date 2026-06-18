# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.h

Purpose: internal header for rpmsg character endpoint helpers shared by `rpmsg_char.c` and `rpmsg_ctrl.c`.

Important APIs, types, and functions: when `CONFIG_RPMSG_CHAR` is enabled, it declares `rpmsg_chrdev_eptdev_create(struct rpmsg_device *, struct device *, struct rpmsg_channel_info)` and `rpmsg_chrdev_eptdev_destroy(struct device *, void *)`. When disabled, inline stubs return `-ENXIO`.

Control flow: there is no runtime control flow beyond compile-time selection. `rpmsg_ctrl.c` can call the helper unconditionally and receive `-ENXIO` if char endpoints are not built.

State and persistence: no state is stored in this header.

Dependencies and integration points: depends on `struct rpmsg_device`, `struct device`, and `struct rpmsg_channel_info` definitions from rpmsg/device headers included by users. It is the contract between the control device and endpoint char-device implementation.

Risks: stale prototypes here would break cross-file builds. The disabled stubs make runtime ioctl failures possible if control support is enabled without endpoint char support.

Test signals: compile with `CONFIG_RPMSG_CHAR=y/m` and disabled; verify `rpmsg_ctrl.c` builds and `RPMSG_CREATE_EPT_IOCTL` reports `-ENXIO` through the helper when endpoint char support is absent.
