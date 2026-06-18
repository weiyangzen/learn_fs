# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.c

### Purpose
`amdgpu_dm_mst_types.c` implements AMDGPU Display Manager support for DisplayPort MST connectors, AUX transactions, MST HPD sideband processing, fake MST encoders, remote sink creation, bandwidth/PBN helpers, and DSC-over-MST validation/precomputation. It is the bridge between DRM MST topology helpers and DC link/stream state.

### Important APIs, Types, And Functions
Key exported APIs are `amdgpu_dm_initialize_dp_connector`, `dm_dp_create_fake_mst_encoders`, `dm_handle_mst_sideband_msg_ready_event`, `dm_mst_get_pbn_divider`, `compute_mst_dsc_configs_for_state`, `pre_validate_dsc`, `needs_dsc_aux_workaround`, and `dm_dp_mst_is_port_support_mode`. Important internal paths include `dm_dp_aux_transfer`, MST connector `get_modes`/`detect`/`atomic_check`, `dm_dp_add_mst_connector`, DSC helpers such as `validate_dsc_caps_on_connector`, `compute_mst_dsc_configs_for_link`, `increase_dsc_bpp`, and `try_disable_dsc`, plus Synaptics/Panamera branch workarounds.

### Control Flow
DP connector initialization wires a DRM AUX adapter to DC DDC, initializes the MST topology manager, and registers DP subconnector properties. MST topology callbacks allocate dynamic DRM connectors, attach all fake MST encoders, inherit root connector properties, and retain the topology port. Mode probing reads MST EDID, creates or replaces DC remote sinks, restores HDCP state, updates FreeSync/DSC/downstream-port capability caches, and publishes EDID modes. HPD IRQ handling loops over ESI bits, asks DRM MST helpers to process sideband messages, ACKs handled events, and caps the loop at 30 iterations. Atomic validation releases time slots and separately computes DSC/PBN assignments when required.

### State, Persistence, And Dependencies
State is in `amdgpu_dm_connector` fields such as `dc_sink`, `drm_edid`, `mst_output_port`, `mst_root`, `mst_status`, `dsc_aux`, `mst_local_bw`, `vc_full_pbn`, `branch_ieee_oui`, and topology-manager state. No filesystem persistence exists. It depends on DRM DP MST helpers, DRM atomic state, DC link/sink/DSC APIs, DPCD reads, DM HDCP workqueue state, debugfs hooks, and AMD-specific DPCD branch quirks.

### Integration Points
This file is called from AMDGPU DM connector setup, hotplug handling, atomic check, and stream validation. It integrates with `amdgpu_dm.c` for connector state and DC stream creation, with DRM MST for topology/time-slot accounting, with DC resource allocation for DSC hardware, and with `amdgpu_dm_mst_types.h` declarations consumed by the broader DM atomic pipeline.

### Risks
MST state is highly race-prone: remote sinks can be removed by CSN, connectors can unregister while hotplug work runs, and AUX failures can mimic disconnects. DSC precomputation mutates PBN requests and temporary stream timing; mistakes can leave time-slot state inconsistent or allocate DSC unnecessarily. Bandwidth conversion depends on FEC overhead, 8b/10b versus 128b/132b encoding, and branch-specific throughput limits. Quirk paths for Synaptics hubs and HPD-disconnect AUX errors are hardware-specific and easy to regress.

### Test Signals
Exercise MST hub plug/unplug, cascaded Synaptics docks, HPD IRQ storms, remote EDID failure fallback, HDCP state restoration, multi-monitor atomic modesets, DSC and non-DSC bandwidth exhaustion, DP 1.4 and UHBR link encodings, and debugfs forced DSC settings. Useful signals include DRM MST time-slot validation, `DRM_DEBUG_DRIVER` `MST_DSC` logs, no leaked remote sinks, and successful suspend/resume with MST displays attached.
