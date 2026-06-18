# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.h

## Purpose
Provides the public declaration for GuC debugfs registration.

## Important APIs, Types, And Functions
It forward-declares `struct dentry` and `struct xe_guc`, then declares `xe_guc_debugfs_register`.

## Control Flow
No runtime control flow lives in the header; callers pass the GuC object and parent debugfs directory to the implementation.

## State And Persistence
The header owns no state. Debugfs entry lifetime is managed by DRM/debugfs infrastructure in the implementation.

## Dependencies And Integration Points
Included by GuC or GT debugfs setup code when the `uc` debugfs subtree is populated.

## Risks And Test Signals
The interface is narrow. Compile-time include coverage and debugfs registration/read smoke tests are the practical validation signals.
