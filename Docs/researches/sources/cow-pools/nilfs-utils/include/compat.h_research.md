# File Research: sources/cow-pools/nilfs-utils/include/compat.h

Central compatibility header. It includes generated config, optional system headers, fallback definitions for GCC builtins, sparse `__force`, NILFS magic, `offsetof`, freeze/thaw ioctls, Linux clocks, timespec macros, endian conversion macros, `PATH_MAX`, device major/minor helpers, and `getprogname()` fallback.

It is important for user-space inclusion of Linux NILFS headers because it provides byte-order helpers expected by on-disk definitions, especially under Sparse.
