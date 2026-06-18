# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_debug_os.h

Libzpool debug OS header. It defines:
- `SET_ERROR(err)` as a wrapper that calls `__set_error(__FILE__, __func__, __LINE__, err)` and returns `err`.

This preserves source-location error tracing in userland ZFS debug builds.
