# sources/distributed-fs/ceph-client/include/linux/mtio.h

Purpose: supplies compat ioctl helpers for magnetic tape drivers that need to return `MTIOCGET` and `MTIOCPOS` data correctly to 32-bit userspace running on a 64-bit kernel.

Important APIs and types: `struct mtget32` and `struct mtpos32` define the 32-bit layouts for incompatible tape status/position structures, with ioctl numbers `MTIOCGET32` and `MTIOCPOS32`. `put_user_mtget()` converts a native `struct mtget` into the compat layout when `in_compat_syscall()` is true and copies the native structure otherwise. `put_user_mtpos()` writes the block number as either `u32` or `long` depending on syscall mode.

Control flow: tape ioctl implementations populate native kernel `struct mtget` or `struct mtpos` data, then call these helpers to copy results to the user pointer in the ABI shape selected by the current syscall context. Copy failures are converted to `-EFAULT`.

State and persistence: no state is kept. The helpers only marshal transient ioctl response data from kernel memory to userspace.

Dependencies and integration points: depends on compat detection, UAPI tape structures, and user access helpers. It integrates SCSI/IDE tape-style drivers with the generic compat ioctl layer.

Risks and test signals: risks include truncating fields that exceed signed 32-bit ranges, returning native layout to compat callers, incorrect user pointer type in `put_user_mtpos()`, and missing `-EFAULT` propagation. Test native and compat `MTIOCGET`/`MTIOCPOS`, invalid user pointers, large block/file numbers, and all tape drivers that share the helper.
