## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.c

### Purpose
This file implements OrangeFS sysfs controls and counters under `/sys/fs/orangefs`, including local timeout settings, daemon-backed cache/performance tunables, readahead settings, and simple read/write stats.

### Important APIs, types, and functions
- `struct orangefs_attribute` wraps sysfs attributes with OrangeFS-specific show/store callbacks.
- `orangefs_attr_show()` and `orangefs_attr_store()` dispatch generic sysfs operations and deny writes to `perf_counters` and `stats`.
- `sysfs_int_show()` and `sysfs_int_store()` expose kernel-local timeout and stats values.
- `sysfs_service_op_show()` sends `ORANGEFS_VFS_OP_PARAM` or `ORANGEFS_VFS_OP_PERF_COUNT` to the daemon to retrieve daemon-side settings and counters.
- `sysfs_service_op_store()` validates input and sends `ORANGEFS_PARAM_REQUEST_SET` operations to the daemon.
- Many `orangefs_attribute` instances define root, `acache`, `capcache`, `ccache`, `ncache`, `perf_counters`, and `stats` files.
- `orangefs_sysfs_init()` creates all kobjects and `orangefs_sysfs_exit()` releases them.

### Control flow
Module init creates `/sys/fs/orangefs`, cache subdirectories, `perf_counters`, and `stats` kobjects. Reads of local integer attributes return kernel globals directly. Reads/writes of daemon-backed attributes allocate a param/perf op, require the daemon in service, map the kobject/name to a protocol operation enum, call `service_operation()`, and format or store the returned value. Readahead attributes are rejected if `ORANGEFS_FEATURE_READAHEAD` was not negotiated.

### State and persistence behavior
Kernel-local timeout attributes mutate module globals immediately. Daemon-backed attributes mutate userspace client-core state through service operations and are not persisted by this file. Read/write stats are volatile counters updated in `file.c`.

### Dependencies and integration points
Depends on kobject/sysfs APIs, `op_alloc()`, `service_operation()`, `is_daemon_in_service()`, protocol param/perf enums, feature flags, and timeout/stat globals. Exposed controls directly influence cache invalidation, slot waits, operation waits, daemon cache behavior, and readahead.

### Risks
Mapping string attribute names to protocol operations is verbose and easy to drift. Some invalid user values are converted to `-EINVAL` after internal `rc == 0` handling. Daemon-backed sysfs operations can block and fail when the daemon is down. Cleanup must handle partially initialized kobjects and release callbacks free the global object pointers.

### Test signals
Test sysfs tree creation/removal, read/write of local timeout attributes, daemon-down behavior for service-backed files, validation ranges for cache limits and readahead settings, feature-gated readahead rejection, perf counter output, stats reads after file I/O, and failure injection during kobject creation.
