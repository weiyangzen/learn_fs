# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm_internal.h

### Purpose
`amdgpu_dpm_internal.h` is a narrow internal header for common DPM implementation details. In this snapshot it exposes only the internal display-configuration helper needed within the PM/DPM implementation area.

### Important APIs, Types, And Functions
The single declaration is `void amdgpu_dpm_get_display_cfg(struct amdgpu_device *adev);`. It is intentionally not part of the broader public `amdgpu_dpm.h` interface.

### Control Flow
The header has no implementation. Its declared helper is expected to collect or refresh display-related PM configuration for an `amdgpu_device`, likely feeding the `adev->pm.pm_display_cfg` state used by DPM/display clock policy.

### State, Persistence, And Dependencies
There is no state in the header. It depends on the caller having visibility of `struct amdgpu_device`. Persistent effects, if any, are in the implementation of `amdgpu_dpm_get_display_cfg()`, not here.

### Integration Points
This header separates an implementation-private DPM helper from the external PM API. It should be included by DPM source files that need to refresh display configuration without exposing that helper to unrelated driver components.

### Risks
The main risk is interface drift: if more internal helpers are added here, the boundary between public DPM API and internal PM implementation can become unclear. Callers also need to ensure display hardware and PM state are initialized before invoking the helper.

### Test Signals
Build coverage of DPM implementation files using this declaration is the primary test signal. Runtime display reconfiguration, monitor hotplug, suspend/resume, and clock/watermark updates are indirect signals that the helper's implementation and call sites remain valid.
