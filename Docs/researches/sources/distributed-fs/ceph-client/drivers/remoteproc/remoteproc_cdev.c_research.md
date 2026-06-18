# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_cdev.c

Purpose: provides the character device control interface for the remoteproc framework. Each rproc gets a cdev whose write commands start, stop, or detach the remote, and whose ioctls configure/query shutdown-on-release behavior.

Important APIs/types/functions: file operations are `rproc_cdev_write()`, `rproc_device_ioctl()`, and `rproc_cdev_release()`. Framework-facing functions are `rproc_char_device_add()`, `rproc_char_device_remove()`, and `rproc_init_cdev()`. The UAPI ioctls are `RPROC_SET_SHUTDOWN_ON_RELEASE` and `RPROC_GET_SHUTDOWN_ON_RELEASE`; write commands are `"start"`, `"stop"`, and `"detach"`.

Control flow: framework init allocates a static major range for up to 64 devices. When an rproc is registered, `rproc_char_device_add()` initializes `rproc->cdev`, assigns `rproc->dev.devt` from the major and rproc index, sets the device kobject parent, and adds the cdev. Userspace writes a short command; the driver copies it from user memory and dispatches to `rproc_boot()`, `rproc_shutdown()`, or `rproc_detach()`. Ioctl set/get accesses `rproc->cdev_put_on_release`. On final close, release shuts down a running remote or detaches an attached remote when that flag is set.

State and persistence: global state is only `rproc_major`. Per-rproc state lives in the remoteproc core object: `cdev`, `dev.devt`, `index`, `state`, and `cdev_put_on_release`. The shutdown-on-release flag is in-memory only and resets with device lifetime.

Dependencies and integration: depends on Linux cdev/fs/uaccess, compat ioctl forwarding, the remoteproc core lifecycle functions, `remoteproc_internal.h`, and the UAPI header `linux/remoteproc_cdev.h`. `remoteproc_core.c` calls `rproc_char_device_add()` during registration.

Risks and test signals: command parsing uses `strncmp(cmd, "start", len)`, so prefixes such as `"sta"` match and commands with trailing newline do not match the literal length as intended; userspace ABI tests should capture accepted strings. There is no open-time rproc reference visible here, so lifetime relies on cdev/device core integration. Test invalid lengths, copy failures, unsupported ioctls, 32-bit compat ioctls, release behavior in RUNNING/ATTACHED/other states, repeated stop/detach, cdev allocation failure, and indices beyond the 64-device major range.
