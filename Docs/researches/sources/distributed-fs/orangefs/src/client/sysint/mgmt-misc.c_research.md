# sources/distributed-fs/orangefs/src/client/sysint/mgmt-misc.c
## sources/distributed-fs/orangefs/src/client/sysint/mgmt-misc.c

**Purpose:** Provides convenience management helpers for address/handle mapping, all-server statfs, all/single-server parameter setting, and server array/count queries.

**APIs and control flow:** `PVFS_mgmt_map_addr` and `PVFS_mgmt_map_handle` wrap cached-config mapping. `PVFS_mgmt_statfs_all()` counts all IO/meta servers, validates caller capacity, allocates an address array, fills it, and calls `PVFS_mgmt_statfs_list`. `PVFS_mgmt_setparam_all()` follows the same count/array/list pattern for `PVFS_mgmt_setparam_list`. `PVFS_mgmt_setparam_single()` looks up a BMI address string and calls list mode for one server. Server array/count functions directly delegate to cached config.

**State and dependencies:** No persistent state. Depends on BMI address lookup, cached config, management list operations, credentials, hints, and error details.

**Risks and tests:** Caller-provided counts must be correct; overflow is reported only before allocation. Single-server lookup silently returns `-PVFS_EINVAL` for bad strings. Tests should include empty filesystems, IO-only/meta-only server filters, count too small, allocation failures, bad server address strings, and details array propagation.
