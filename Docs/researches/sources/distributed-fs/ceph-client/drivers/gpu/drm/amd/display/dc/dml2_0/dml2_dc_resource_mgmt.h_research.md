## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.h

### Purpose
This header declares the DML2-to-DC pipe mapping API.

### Important APIs, Types, And Functions
It forward-declares `dml2_context`, `dml2_dml_to_dc_pipe_mapping`, and `dml_display_cfg_st`, includes DC wrapper types, and declares `dml2_map_dc_pipes()`.

### Control Flow
There is no runtime flow in the header. The comment documents that the implementation creates pipe linkage in `dc_state` from DML-calculated ODM and DPP-per-surface outputs.

### State, Persistence, And Dependencies
The header itself has no state. The declared function mutates `dc_state` and uses mapping/context state.

### Integration Points
Included by resource-management callers that need to convert DML outputs into DC pipe topology. It is shared by DML2.0 and DML2.1 wrapper flows.

### Risks
The API returns only a boolean even though much of the implementation asserts on invalid topology. Callers must pass a valid mapping covering all active stream and plane IDs.

### Test Signals
Compile tests should verify callers can include this header with DC types. Integration tests should assert `dc_state` topology after a successful `dml2_map_dc_pipes()` call.
