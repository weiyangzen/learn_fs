# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.h

### Purpose
`amdgpu_dm_mst_types.h` declares the public MST/DSC interface used by AMDGPU DM code and centralizes branch-device constants for Synaptics/Panamera DSC workarounds and PBN FEC overhead factors.

### Important APIs, Types, And Functions
The header defines `DP_BRANCH_DEVICE_ID_90CC24`, Synaptics remote-control and vendor-specific DPCD offsets, `IS_SYNAPTICS_PANAMERA`, `IS_SYNAPTICS_CASCADED_PANAMERA`, FEC overhead multipliers, `enum mst_msg_ready_type`, and `struct dsc_mst_fairness_vars`. It declares MST initialization, sideband handling, fake encoder creation, DSC prevalidation/configuration, PBN divider, and mode-support checks.

### Control Flow
There is no executable flow in the header. It shapes call flow by exposing MST connector setup to connector initialization, sideband processing to HPD paths, and DSC computation/prevalidation to atomic-check paths.

### State, Persistence, And Dependencies
The only state shape defined here is `dsc_mst_fairness_vars`, carrying PBN, DSC enablement, target bpp, and connector association during DSC fairness calculations. It forward-declares AMDGPU DM types and relies on DC and DRM types included by users. No persistent storage exists.

### Integration Points
Consumers include `amdgpu_dm_mst_types.c` and broader DM atomic code that needs to initialize MST-capable DP connectors, precompute DSC, or validate MST port mode support. The macros encode branch-vendor assumptions also used when reading DPCD vendor fields.

### Risks
Changing constants or structure fields affects hardware-specific workarounds and the ABI between MST computation code and atomic validation callers. The macro-style Synaptics detection assumes stable branch-device name layout and vendor data offsets.

### Test Signals
Build coverage should include `CONFIG_DRM_AMD_DC_FP` and non-FP configurations, MST DSC-capable hubs, Synaptics cascaded hubs, and atomic check paths that allocate `dsc_mst_fairness_vars`.
