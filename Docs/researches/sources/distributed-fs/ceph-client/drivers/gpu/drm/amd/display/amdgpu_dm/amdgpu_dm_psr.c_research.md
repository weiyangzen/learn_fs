# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.c

### Purpose
`amdgpu_dm_psr.c` manages Panel Self Refresh capability discovery, link setup, enable/disable, global disable, and wait-for-exit behavior for embedded DisplayPort panels.

### Important APIs, Types, And Functions
Important functions are `amdgpu_dm_set_psr_caps`, `amdgpu_dm_link_setup_psr`, `amdgpu_dm_psr_enable`, `amdgpu_dm_psr_disable`, `amdgpu_dm_psr_disable_all`, `amdgpu_dm_psr_is_active_allowed`, and `amdgpu_dm_psr_wait_disable`. The internal `link_supports_psrsu` checks PSR-SU capability but currently always returns false after gating due to a temporary disable.

### Control Flow
Capability setup rejects non-eDP, disconnected links, missing PSR DPCD support, and panel instance 1, then marks PSR1 or PSR-SU capability. Link setup computes power PSR config, toggles SMU and multi-display optimization flags, optionally derives PSR-SU DSC slice height, and calls `dc_link_setup_psr`. Enable computes a static-frame delay from refresh rate, programs static-screen triggers, enables PSR active permission, and enables DC idle optimizations when available. Disable clears PSR active permission, and wait-disable polls `dc_link_get_psr_state` until PSR exits or a 500 ms timeout is reached.

### State, Persistence, And Dependencies
State lives in `link->psr_settings`, DC current state, panel DPCD capability caches, and firmware PSR state. No filesystem persistence exists. Dependencies include DC link PSR APIs, DMUB/DMCUB capability, panel power helpers, feature/debug masks, udelay polling, and embedded-panel detection.

### Integration Points
The file is called during eDP connector capability setup, stream/link programming, atomic commit power optimization, and global display-manager disable paths. It interacts with DC idle optimizations and SMU optimization policy.

### Risks
Incorrect capability gating can enable PSR on panels that glitch or disable it on working panels. Refresh-rate-derived static-frame delay depends on valid timing totals. PSR-SU is deliberately disabled despite capability checks, so future re-enablement must retest vstartup/vblank behavior. Busy polling for exit can delay callers up to 500 ms.

### Test Signals
Test eDP panels with and without PSR, PSR1 versus PSR-SU-capable panels, multi-display configurations, static screen entry/exit, cursor and overlay updates, suspend/resume, and forced debug masks. Useful signals include PSR state transitions, visual corruption, vblank event continuity, and timeout logs from wait-disable callers.
