# sources/distributed-fs/ceph-client/include/uapi/linux/exfat.h

This UAPI header defines the exFAT-specific filesystem shutdown ioctl. It is a narrow ABI for forcing an exFAT filesystem into a shutdown/down state for testing, administration, and error-handling workflows.

The main export is `EXFAT_IOC_SHUTDOWN`, encoded as `_IOR('X', 125, __u32)`, plus shutdown mode flags `EXFAT_GOING_DOWN_DEFAULT`, `EXFAT_GOING_DOWN_FULLSYNC`, and `EXFAT_GOING_DOWN_NOSYNC`.

Control flow is ioctl-based: privileged or otherwise authorized userspace passes a shutdown flag to an open exFAT file or mount-related fd; the filesystem implementation interprets the mode, optionally syncs metadata/data, and transitions the superblock/mount into a state where further operations fail or are restricted. State and persistence live in the exFAT superblock and mounted filesystem structures, not this header. Disk persistence depends on the selected sync mode.

Dependencies include `linux/types.h`, `linux/ioctl.h`, and the exFAT filesystem driver. Integration points include generic shutdown semantics shared with `FS_IOC_SHUTDOWN`/ext4-style flag values, mount lifecycle handling, and filesystem error injection tests.

Risks are destructive administrative misuse, incomplete sync semantics causing data loss, and ABI collision with other `'X',125` shutdown ioctls. Test signals include exFAT ioctl tests for each flag, post-shutdown operation failure checks, remount/fsck behavior, and sync/no-sync persistence validation.
