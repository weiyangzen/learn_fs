# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_helpers.c

## Purpose
`amdgpu_dm_helpers.c` implements AMDGPU Display Manager helper callbacks expected by DC core. It adapts DC requests to Linux DRM, DP MST, AUX/DPCD, I2C, EDID, DSC, DMUB, ACPI, VBIOS, panel, memory, MCCS, and adaptive-sync mechanisms.

## Important APIs, types, and functions
EDID/panel helpers include `dm_helpers_parse_edid_caps()`, `dm_helpers_read_local_edid()`, `dm_helpers_init_panel_settings()`, and `dm_helpers_override_panel_settings()`. MST helpers include `dm_helpers_dp_mst_write_payload_allocation_table()`, `dm_helpers_dp_mst_poll_for_allocation_change_trigger()`, `dm_helpers_dp_mst_send_payload_allocation()`, `dm_helpers_dp_mst_update_mst_mgr_for_deallocation()`, and topology-manager start/stop. AUX/I2C and DMUB helpers include `dm_helpers_dp_read_dpcd()`, `dm_helpers_dp_write_dpcd()`, `dm_helpers_submit_i2c()`, `dm_helpers_execute_fused_io()`, and DMUB sync wrappers. DSC, compliance, MCCS, logging, and memory helpers round out the adapter layer.

## Control flow
EDID reads try ACPI for internal panels, VBIOS hardcoded EDID when no DDC exists, or normal DDC reads, then update DRM connector info, copy raw EDID into the DC sink, and parse audio/HDMI/name/quirk data. MST helpers translate DRM atomic MST payload state into DC allocation tables and perform add/remove payload phases. AUX/I2C helpers locate the connector from `link->priv` and call Linux transport APIs. DSC enablement handles SST, MST virtual DPCD, pass-through AUX, DP-HDMI PCON, and Synaptics branch workarounds. Compliance test-pattern handling can alter timing color depth/encoding, update DSC config, force clock state, and program the link test pattern.

## State and persistence behavior
The file mutates live state owned elsewhere: DRM display info, `dc_sink` EDID/caps, link panel config, MST allocation tables, connector MST status bits, DPCD registers, DSC enable bits, stream timing/test-pattern state, DMUB commands, GPU memory allocations, idle workqueue flags, and MCCS capabilities. It has no disk persistence.

## Dependencies and integration points
It depends on DRM EDID and connector helpers, ACPI video EDID, VBIOS panel info, DRM DP MST, DP AUX/DPCD, Linux I2C, AMD DC core/link types, DMUB processing, clock manager, MST connector state, DSC, and MCCS DDC commands. It is the primary Linux platform adapter for DC helper callbacks.

## Risks and edge cases
EDID retry/fallback paths are sensitive to corrupt checksums, extension counts, force-off connectors, and fake EDIDs. MST helpers rely on atomic state lifetime guarantees and correct old-payload reconstruction. DSC programming order varies by topology and branch device. Several TODO helpers intentionally return false or no-op, so DC callers must tolerate missing support. MCCS uses raw retrying I2C messages and can be slow or unsupported.

## Test signals
Validate EDID good/bad/no-response, ACPI/VBIOS fallback, panel quirks, DP compliance checksum response, MST add/remove slot ordering, AUX/I2C failures, DSC enable/disable over SST/MST/PCON/Synaptics paths, DP test patterns, DMUB AUX/config commands, periodic detection toggles, MCCS FreeSync VCP request/set, and PCON adaptive-sync whitelist behavior.
