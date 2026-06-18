# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.h

## Purpose
Provides the declaration for GSC debugfs registration.

## Important API
- `xe_gsc_debugfs_register(struct xe_gsc *gsc, struct dentry *parent)` installs GSC diagnostic files beneath an existing debugfs directory.

## Integration and Risks
The header keeps dependencies minimal with forward declarations. Callers must pass a valid parent dentry and a fully initialized `struct xe_gsc`; the implementation tolerates allocation failure by omitting debugfs output.
