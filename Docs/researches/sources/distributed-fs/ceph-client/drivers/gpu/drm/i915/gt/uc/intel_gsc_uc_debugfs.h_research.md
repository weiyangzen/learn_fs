# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.h

### Purpose
`intel_gsc_uc_debugfs.h` declares the GSC debugfs registration helper.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gsc_uc` and `struct dentry`, and declares `intel_gsc_uc_debugfs_register()`.

### Control Flow
There is no runtime flow in the header.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and integrates GT debugfs setup with the implementation. Risks are limited to prototype drift. Compile coverage and `gsc_info` registration provide signals.
