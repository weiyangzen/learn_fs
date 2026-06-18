# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.c

### Purpose
`amdgpu_dm_replay.c` manages AMD eDP Panel Replay capability detection, configuration, enable, disable, and global disable. Replay is a panel power-saving feature gated by FreeSync/adaptive-sync, DPCD, VSDB, and DMUB support.

### Important APIs, Types, And Functions
Important functions are `amdgpu_dm_link_supports_replay`, `amdgpu_dm_set_replay_caps`, `amdgpu_dm_link_setup_replay`, `amdgpu_dm_replay_enable`, `amdgpu_dm_replay_disable`, and `amdgpu_dm_replay_disable_all`. It uses replay configuration fields such as `replay_supported`, `replay_enable_option`, fast resync/coasting support, timing sync support, and debug visual-confirm flags.

### Control Flow
Capability support first requires connector FreeSync capability, VSDB replay mode, eDP 1.3 or later, AUX wake ALPM, adaptive-sync SDP support, and populated pixel-deviation data. Set-caps rejects non-embedded signals, panel replay disallow flags, missing DMUB replay firmware support, then initializes the replay config. Link setup enables static-screen replay options, sets power optimization support, computes fast-resync support from min/max vertical frequency, disables general UI when timing sync is unsupported, and marks the feature enabled. Runtime enable checks connector disallow state, programs replay setup/coasting vtotal through `link_srv`, and allows active replay; disable clears active replay.

### State, Persistence, And Dependencies
State lives in `link->replay_settings`, connector `vsdb_info`, FreeSync range fields, `disallow_edp_enter_replay`, DPCD capability caches, and DMUB feature caps. No filesystem persistence exists. Dependencies include DC link service callbacks, DMUB firmware capability reporting, adaptive-sync DPCD parsing, and power-helper initialization.

### Integration Points
Replay setup is part of embedded-panel link configuration and atomic/display power-management paths. It is mutually adjacent to PSR policy and uses `dc_set_replay_allow_active` for display-manager-wide disabling.

### Risks
Replay gating spans multiple capability sources; stale connector state or missing VSDB parsing can misclassify support. Enabling replay when `disallow_edp_enter_replay` is set is explicitly blocked to avoid known panel issues. Link service callbacks must exist and match firmware support. Timing-sync options are conservative and may limit power savings.

### Test Signals
Test eDP panels with replay-capable VSDB and adaptive-sync data, panels without replay, FreeSync disabled states, DMUB firmware without replay support, fast-resync min/max vfreq cases, runtime disallow flags, suspend/resume, and visual-confirm debug mode.
