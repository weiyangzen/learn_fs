<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/remoteproc_cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/remoteproc_cdev.h

Purpose: defines the remoteproc character-device ioctl ABI for controlling whether a remote processor is automatically shut down when a controlling userspace file descriptor is closed.

Important APIs and types: `RPROC_MAGIC` is the ioctl magic. `RPROC_SET_SHUTDOWN_ON_RELEASE` accepts an `__s32` where zero disables automatic shutdown and nonzero enables it. `RPROC_GET_SHUTDOWN_ON_RELEASE` returns the current setting as an `__s32`.

Control flow: userspace opens a remoteproc cdev and sets or queries the shutdown-on-release policy. When the file is later closed, remoteproc cdev code uses that policy to decide whether the remote processor should be shut down automatically.

State and persistence: the exposed state is a runtime per-cdev control flag. It affects remote processor lifetime on close but is not durable across driver reset or reboot.

Dependencies and integration points: integrates with remoteproc core, firmware_class, rpmsg/virtio, SoC-specific remote processor drivers, and administrative tooling.

Risks and test signals: risks include accidentally stopping critical co-processors when the last controller closes, inconsistent policy across multiple opens, and permission-policy mistakes. Test set/get round trips, close behavior with shutdown enabled and disabled, multiple file descriptors, remoteproc removal while open, and permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/remoteproc_cdev.h -->
