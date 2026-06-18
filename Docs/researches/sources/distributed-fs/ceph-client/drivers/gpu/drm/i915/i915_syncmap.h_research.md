<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.h

## Purpose
Declares the opaque i915 syncmap used to remember latest synchronized fence seqnos per context.

## Important APIs, types, and functions
- Opaque `struct i915_syncmap`.
- `KSYNCMAP` defines the radix fanout as 16.
- APIs initialize, set, query, and free syncmaps.

## Control flow
No implementation control flow exists in the header. Callers pass a pointer to their root/cache pointer so the implementation can update it after lookups and inserts.

## State and persistence
The root pointer is caller-owned and is reset to NULL by init/free. Tree contents persist until freed.

## Dependencies and integration points
Depends only on Linux types. Used by timeline code and request dependency setup.

## Risks
Callers must treat the structure as opaque and must not copy root pointers without understanding ownership. `KSYNCMAP` must remain a power-of-two compatible with implementation bitmap assumptions.

## Test signals
Build coverage plus syncmap selftests and timeline dependency-squashing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.h -->
