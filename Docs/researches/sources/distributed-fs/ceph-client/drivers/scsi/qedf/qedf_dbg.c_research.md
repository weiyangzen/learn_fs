# sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_dbg.c

Purpose: provides non-debugfs diagnostic primitives for QEDF: log formatting helpers, GRC dump buffer allocation/free/get wrappers, GRC uevent emission, and generic sysfs binary attribute create/remove loops.

Important APIs/types/functions: `qedf_dbg_err()`, `qedf_dbg_warn()`, `qedf_dbg_notice()`, and `qedf_dbg_info()` implement the `QEDF_ERR/WARN/NOTICE/INFO` macros with function, line, PCI device name, and host number context. Warning, notice, and info logs are gated by the global `qedf_debug` bitmask; errors always print. `qedf_alloc_grc_dump_buf()` and `qedf_free_grc_dump_buf()` manage vmalloc-backed dump storage. `qedf_get_grc_dump()` validates the buffer and calls `common->dbg_all_data()`. `qedf_uevent_emit()` constructs the `GRCDUMP=<host_no>` environment entry for `KOBJ_CHANGE`. `qedf_create_sysfs_attr()` and `qedf_remove_sysfs_attr()` iterate `struct sysfs_bin_attrs` arrays.

Control flow: logging helpers build a `va_format`, check the optional debug mask, and print through the kernel log with either PCI/host context or a placeholder PCI BDF when no context is available. GRC helpers are thin allocation and QED-common wrappers. Sysfs creation iterates until a null `name`, attempts each binary file, logs failures, and returns the last error encountered.

State and persistence: mutable state is limited to the global `qedf_debug` read by log gates and caller-owned GRC dump pointers. The helpers do not persist data; buffers remain attached to `qedf_ctx` until freed by driver teardown. Uevents are transient.

Dependencies and integration: depends on kernel printk, vmalloc, kobject uevents, SCSI host generic device kobject, QED common debug ops, and the declarations in `qedf_dbg.h`. It is used by core driver, sysfs, and debugfs code without requiring `CONFIG_DEBUG_FS`.

Risks and test signals: log-mask changes affect runtime observability and can hide warning/notice/info diagnostics. `qedf_get_grc_dump()` returns `-EINVAL` if called before allocation but otherwise trusts QED to fill the supplied buffer size. Sysfs creation can partially succeed if a later file fails; teardown must tolerate that. Test signals include dynamic debug-mask writes, GRC dump allocation/capture failure paths, uevent content, and sysfs binary file create/remove on probe failure unwind.
