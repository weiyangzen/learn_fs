## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.c

### Purpose
`dml2_top_legacy.c` is currently a stub translation unit for the legacy top implementation.

### Important APIs, Types, And Functions
It includes `dml2_top_legacy.h`, the core and PMO factories, and legacy display mode core structs, but defines no functions.

### Control Flow
There is no runtime flow in this file.

### State, Persistence, And Dependencies
There is no state. The includes indicate intended dependencies on legacy core and PMO creation and legacy display-mode structures.

### Integration Points
The companion header declares `dml2_top_legacy_initialize_instance()`, but this source file does not define it. Current top dispatch in this subset routes supported projects to SOC15 instead.

### Risks
If a build target expects `dml2_top_legacy_initialize_instance()`, this source file will not satisfy the symbol. The file may be a placeholder for removed or future legacy support, so stale includes should be watched for build churn.

### Test Signals
Build/link tests should confirm no active configuration requires the legacy initializer from this file, or else add/restore the implementation.
