# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_quirks.c

### Purpose
`amdgpu_dm_quirks.c` applies DMI-based display-manager quirks for specific systems. It currently flags selected Dell desktops for AUX HPD disconnect behavior and selected HP notebooks/thin clients for eDP0-on-DP1 support.

### Important APIs, Types, And Functions
The file defines `struct amdgpu_dm_quirks`, static `quirk_entries`, DMI callbacks `edp0_on_dp1_callback` and `aux_hpd_discon_callback`, the `dmi_quirk_table`, and the exported `retrieve_dmi_info` function.

### Control Flow
`retrieve_dmi_info` resets quirk flags in `amdgpu_display_manager`, calls `dmi_check_system`, then copies the matching callback-updated global quirk bits into `dm->aux_hpd_discon_quirk` and `dm->edp0_on_dp1_quirk` with informational logs.

### State, Persistence, And Dependencies
State is process-global `quirk_entries` plus per-device flags in `amdgpu_display_manager`. There is no filesystem persistence. It depends on Linux DMI matching, DRM logging, and downstream code that reads the two DM quirk flags.

### Integration Points
`aux_hpd_discon_quirk` is consumed by the DP AUX transfer path to treat specific HPD-disconnect errors during MST sideband writes as successful. `edp0_on_dp1_quirk` is consumed by connector/link detection policy elsewhere in AMDGPU DM.

### Risks
The global `quirk_entries` bits are sticky after the first match, which is acceptable for typical single-system DMI evaluation but should be considered if reused in unusual multi-device scenarios. DMI product strings are exact and can miss BIOS naming variants. Over-broad quirks can hide real AUX disconnects.

### Test Signals
Boot listed Dell/HP systems and nearby non-listed variants, confirm the expected log messages and quirk flags, and retest MST AUX sideband handling and eDP connector assignment on affected platforms.
