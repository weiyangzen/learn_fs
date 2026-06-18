# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.h

Purpose: declares HuC debugfs registration.

Important API: `xe_huc_debugfs_register(struct xe_huc *huc, struct dentry *parent)`.

Control flow/state: called by debugfs setup code to publish HuC information below a parent dentry. It owns no types beyond forward declarations.

Dependencies/integration: bridges debugfs setup with HuC firmware status printing.

Risks/test signals: incorrect parent or HuC pointer would affect only diagnostics. Verify `huc_info` appears when debugfs is enabled.
