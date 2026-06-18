<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.h

Purpose: exposes register whitelist processing and dump helpers.

Important APIs: `xe_reg_whitelist_process_engine()` fills per-engine whitelist/save-restore state; `xe_reg_whitelist_print_entry()` formats one whitelist entry; `xe_reg_whitelist_dump()` prints all entries in a save/restore table.

Dependencies and risks: depends on `struct xe_hw_engine`, `struct xe_reg_sr`, and DRM printers. Tests should compare dumped access/range strings with expected hardware flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_reg_whitelist.h -->
