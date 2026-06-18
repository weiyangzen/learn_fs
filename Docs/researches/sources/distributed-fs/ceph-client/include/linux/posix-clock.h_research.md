# sources/distributed-fs/ceph-client/include/linux/posix-clock.h

Purpose: declares the dynamic POSIX clock character-device framework used by PTP and similar clock drivers.

Important APIs and types: `struct posix_clock_operations` exposes clock methods (`clock_adjtime`, `clock_gettime`, `clock_getres`, `clock_settime`) and optional character-device file operations (`open`, `release`, `ioctl`, `read`, `poll`). `struct posix_clock` embeds ops, `cdev`, backing device, rwsem, and zombie flag. `struct posix_clock_context` passes per-open context, file pointer, and driver private file data. APIs register and unregister dynamic clocks.

Control flow: a driver embeds and initializes `struct posix_clock`, provides an initialized device with release method, and calls `posix_clock_register()`. The clock device layer owns initial file-operation dispatch, checks zombie/lifetime state, then forwards clock and optional character operations to driver callbacks. Unregister marks the clock inactive while outstanding references drain.

State and persistence: runtime state includes the cdev/device lifetime, zombie flag under rwsem, and per-open context private data. Hardware clock time persists only if the device provides it; this header stores no persistent time.

Dependencies and integration points: integrates with cdev, device model lifetime, VFS file operations, poll, POSIX timer clock IDs, rwsems, modules, and dynamic clock consumers such as PTP.

Risks and test signals: risks include missing device release callback, freeing embedded private structures before open references close, failing to handle zombie state in callbacks, and access-mode mistakes in ioctl/read. Test register/unregister with open fds, adjtime/gettime/settime/res callbacks, poll/read/ioctl paths, module refcounting, and device removal races.
