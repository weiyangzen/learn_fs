## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_types.h

### Purpose
`dml2_dc_types.h` is a wrapper header for DC-owned types used by DML2.

### Important APIs, Types, And Functions
It does not define functions. It includes `resource.h`, `core_types.h`, `dsc.h`, `clk_mgr.h`, and `dc_state_priv.h`, which provide `dc_state`, `pipe_ctx`, stream/plane state, resource, DSC, and clock-manager types.

### Control Flow
There is no runtime flow.

### State, Persistence, And Dependencies
There is no state in the wrapper. It centralizes external DC type dependencies so DML2 code can include one header.

### Integration Points
`dml2_internal_types.h` and `dml2_dc_resource_mgmt.h` include this file before using DC resource types. The comment notes that standalone builds may provide these types differently.

### Risks
This wrapper ties DML2 compilation to private DC headers such as `dc_state_priv.h`. Changes in DC type definitions can ripple through DML2 even when DML2 source does not change.

### Test Signals
Build tests in both DC-integrated and standalone/unit-test configurations should verify this wrapper resolves the same required type names.
