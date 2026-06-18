# sources/distributed-fs/ceph-client/drivers/s390/virtio/Makefile

Purpose: builds the s390 virtio-ccw transport driver when s390 guest support is enabled.

Important APIs/types/functions: the sole build rule is `obj-$(CONFIG_S390_GUEST) += virtio_ccw.o`, mapping the `CONFIG_S390_GUEST` Kconfig symbol to `virtio_ccw.c`.

Control flow: during kernel build, kbuild includes `virtio_ccw.o` only for configurations that enable s390 guest drivers. There is no runtime behavior in this file.

State and persistence: no state; this is build metadata.

Dependencies and integration: ties the driver under `drivers/s390/virtio` to the s390 guest configuration and the wider virtio/ccw subsystem.

Risks and test signals: incorrect gating would either omit virtio devices for s390 guests or compile the driver for unsupported configs. Test signals are build coverage for `CONFIG_S390_GUEST=y/m/n` and that `virtio_ccw.o` links with required virtio, CCW, and s390 channel I/O symbols.
