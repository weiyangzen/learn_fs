# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.h

### Purpose
`amdgpu_dm_psr.h` declares the AMDGPU DM Panel Self Refresh interface and defines the page-flip entry-delay constant used by PSR policy.

### Important APIs, Types, And Functions
It defines `AMDGPU_DM_PSR_ENTRY_DELAY` and declares PSR capability setup, link setup, enable, disable, global disable, active-allowed query, and wait-disable helpers.

### Control Flow
There is no executable flow. The header defines the boundary used by connector/link setup and atomic commit code to call the PSR implementation.

### State, Persistence, And Dependencies
No state is stored in the header. It includes `amdgpu.h` and references `dc_link`, `dc_stream_state`, and `amdgpu_display_manager` structures supplied by other DM/DC headers.

### Integration Points
Consumers use these declarations when configuring eDP links, entering or leaving PSR around display updates, and disabling PSR globally during modesets or power events.

### Risks
The entry-delay constant is policy visible; changing it affects PSR entry aggressiveness and flicker/power tradeoffs. Signature changes require coordinated edits in PSR callers.

### Test Signals
Build with PSR enabled, run eDP modeset/page-flip tests, and verify callers can disable and wait for PSR around atomic updates.
