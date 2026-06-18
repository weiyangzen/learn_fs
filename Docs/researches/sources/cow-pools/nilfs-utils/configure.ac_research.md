# File Research: sources/cow-pools/nilfs-utils/configure.ac

Autoconf configuration for `NILFS utils` version `2.4.0-dev`. It initializes Automake, Libtool, config headers, and optional git revision embedding controlled by `NILFS_UTILS_USE_GITID`.

It detects core tools, libraries, and headers for UUID, POSIX message queues, POSIX semaphores, timers, blkid, libmount, SELinux, mmap, large-file support, and many libc functions. It includes custom macros to prefer pkg-config with manual library fallback.

Install layout handling includes usrmerge detection and configuration of `core_sbindir`, `sbindir`, `badblocksdir`, `/etc`, `/var`, architecture libdir detection, optional pkg-config output, and optional installation of bundled UAPI headers.
