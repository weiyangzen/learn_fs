<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.h

## Purpose

`xe_tile_sriov_pf_debugfs.h` declares the PF SR-IOV per-tile debugfs population hook.

## Important APIs, Types, and Functions

The single public function is `xe_tile_sriov_pf_debugfs_populate(struct xe_tile *tile, struct dentry *parent, unsigned int vfid)`.

## Control Flow

PF SR-IOV debugfs setup calls this for every tile under the PF directory and under each VF directory.

## State and Persistence Behavior

The function creates debugfs dentries tied to live tile and VF configuration state. The header owns no state.

## Dependencies and Integration Points

It forward-declares `dentry` and `xe_tile` and is consumed by PF SR-IOV debugfs setup.

## Risks and Test Signals

Callers must pass a parent dentry with the private-data layout expected by the implementation. Debugfs layout tests should catch misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.h -->
