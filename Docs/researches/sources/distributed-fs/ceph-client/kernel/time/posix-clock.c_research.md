# sources/distributed-fs/ceph-client/kernel/time/posix-clock.c

Purpose: implements dynamic POSIX clock devices, allowing character devices such as PTP hardware clocks to provide file operations and `clock_gettime/settime/adjtime/getres` through encoded file-descriptor clock ids.

Important APIs and flow: `posix_clock_register()` initializes the rwsem and cdev, registers the device, and binds ownership/dev pointers. `posix_clock_unregister()` removes the cdev/device, marks the clock zombie under write lock, and drops the device reference. File operations open a per-file `posix_clock_context`, call optional driver ops for read/poll/ioctl/release, and guard operations with `get_posix_clock()` so stale zombie clocks return `-ENODEV`. Dynamic clock callbacks decode fd clock ids with `clockid_to_fd()`, validate the file is a posix clock, hold the file and rwsem, enforce write mode for set/adjust, and call driver clock ops.

State and persistence: each `posix_clock` owns a cdev, rwsem, zombie flag, device pointer, and driver ops. Each open file owns `posix_clock_context` and a device reference until release.

Dependencies and integration: cdev/device core, file descriptor references, POSIX timer `k_clock` dispatch, uaccess, driver-provided posix clock ops, and module ownership.

Risks and test signals: risks include use-after-unregister, missing private data, stale fd clock ids, write permission bypass, and driver op absence. Test register/open/read/poll/ioctl/release, unregister while fds remain open, clock id operations on invalid fds, read-only set/adj denial, strict timespec validation, and missing-op `-EOPNOTSUPP`.
