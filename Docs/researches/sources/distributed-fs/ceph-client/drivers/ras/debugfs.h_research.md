# sources/distributed-fs/ceph-client/drivers/ras/debugfs.h

Purpose: declares the RAS debugfs root accessor with a no-debugfs fallback. It is the small integration header used by RAS subcomponents that want to add debugfs files without directly owning the top-level root.

Important APIs: when `CONFIG_DEBUG_FS` is enabled, it declares `struct dentry *ras_get_debugfs_root(void)`. Otherwise it provides a static inline stub returning NULL.

Control flow: none beyond compile-time selection. Callers should test the returned pointer and skip debugfs creation when NULL.

State and persistence: no state is stored in the header. Runtime root state lives in `debugfs.c`.

Dependencies and integration: includes `<linux/debugfs.h>`. Used by `cec.c`, `amd/fmpm.c`, and other RAS code that creates debugfs nodes under `/sys/kernel/debug/ras`.

Risks: the header only stubs `ras_get_debugfs_root()`, not `ras_userspace_consumers()` or setup helpers; code using those must be guarded elsewhere. Callers that assume a non-NULL root will fail on kernels without debugfs.

Test signals: compile with and without `CONFIG_DEBUG_FS`, verify callers handle NULL root, and build modules that include the header without pulling debugfs-only symbols into no-debugfs builds.
