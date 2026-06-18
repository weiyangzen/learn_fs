# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.h

### Purpose
`amdgpu_dm_wb.h` declares the AMDGPU DM writeback connector initialization entry point.

### Important APIs, Types, And Functions
It includes DRM writeback definitions and declares `amdgpu_dm_wb_connector_init(struct amdgpu_display_manager *dm, struct amdgpu_dm_wb_connector *dm_wbcon, uint32_t link_index)`.

### Control Flow
There is no executable flow. The declaration lets display-manager initialization register writeback connectors implemented in `amdgpu_dm_wb.c`.

### State, Persistence, And Dependencies
No state is stored here. Callers provide the display manager, writeback connector storage, and DC link index. It depends on `drm_writeback.h` and AMDGPU DM type definitions.

### Integration Points
Used by AMDGPU DM device/link initialization when DWB/writeback hardware is exposed.

### Risks
Signature drift affects writeback initialization callers. The header does not expose supported formats or job helpers, so callers must treat initialization as the only public contract.

### Test Signals
Build writeback-enabled DM configurations and confirm writeback connector registration succeeds.
