# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.c

## Purpose
`amdgpu_dm_debugfs.c` builds the Display Manager debugfs surface for connector, CRTC, and device-wide diagnostics and override controls. It exposes DP link/PHY settings, test patterns, DSC parameters, MST status and hotplug simulation, HDCP sink capability, eDP PSR/Replay and backlight state, DMUB trace buffers, IPS residency, secure-display CRC windows, and DTN/DCC logging.

## Important APIs, types, and functions
Initialization entry points are `connector_debugfs_init()`, `crtc_debugfs_init()`, and `dtn_debugfs_init()`. Common parsing is in `parse_write_buffer_into_params()`. DP and connector controls include `dp_link_settings_read/write()`, `dp_mst_link_setting()`, `dp_phy_settings_read/write()`, `dp_phy_test_pattern_debugfs_write()`, `trigger_hotplug()`, `dp_max_bpc_read/write()`, and `edp_ilr_show/write()`. DSC controls include the `dp_dsc_*` read/write helpers and `dp_dsc_fec_support_show()`. Device/debug hooks include DMUB trace/state/mask handlers, MST topology and HPD controls, IPS residency controls, and secure-display CRC window setters under `CONFIG_DRM_AMD_SECURE_DISPLAY`.

## Control flow
Connector setup selects debugfs entries by connector type: DP/eDP get link, PHY, MST, DSC, HDCP, SDP, max-BPC, and DPIA controls; eDP adds PSR/Replay, backlight, ILR, and self-refresh toggles; HDMI-A gets HDCP and CEC controls. Writes generally copy and parse userspace buffers, validate ranges, lock `dc_lock` or DRM mode objects as needed, then mutate DC link settings, connector state, CRTC state, DPCD registers, or DM debug flags. Device setup creates root files for MST topology, DC capabilities, DMUB tracing, timing sync, HPD toggles, DCC bits, and IPS.

## State and persistence behavior
The file exposes live kernel and hardware-facing state only: `dc_link` settings, DPCD and lane-drive values, `aconnector->dsc_settings`, connector force/status, `adev->dm` debug booleans, DMUB framebuffer windows/shared state, CRTC CRC parameters, and DC debug fields. Nothing is saved to disk; state disappears on reset, hotplug, driver unload, or reboot except for effects written into connected sinks/firmware.

## Dependencies and integration points
It depends on debugfs, DRM connector/CRTC locking, AMD DC link APIs, DP AUX/DPCD, DSC hardware callbacks, MST topology manager APIs, DMUB services, eDP PSR/Replay helpers, CEC notifier support, and optional secure-display CRC plumbing. It is a privileged test/diagnostic interface used by developers and IGT-style validation.

## Risks and edge cases
Forced link settings, DSC overrides, HPD simulation, and test patterns can intentionally desynchronize software, hardware, and sink state. Several read paths scan pipe arrays and require valid active pipe state. The parser truncates to fixed argument counts and parses base-16 values. Locking crosses `dc_lock`, mode-config, CRTC, HPD, and event locks, making lockdep coverage important.

## Test signals
Check debugfs file creation per connector type, valid and invalid write handling, DP test-pattern HPD behavior, MST topology and hotplug paths, DSC override followed by modeset, max-BPC updates, DMUB trace/mask reads, IPS residency start/stop/query, HDMI-CEC toggles, eDP PSR/Replay reads, ILR forcing, secure CRC windows, and concurrent hotplug/modeset/debugfs access.
