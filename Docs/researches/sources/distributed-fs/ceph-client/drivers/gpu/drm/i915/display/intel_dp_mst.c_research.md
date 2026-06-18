# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.c

## Purpose
Implements i915 DisplayPort Multi-Stream Transport support. It creates per-pipe virtual MST stream encoders, dynamic MST connectors, computes bandwidth/TU/PBN/DSC configuration, checks topology bandwidth in atomic state, and sequences MST stream enable/disable around payload allocation and transcoder programming.

## Important APIs, types, and functions
- Exported setup/state APIs: `intel_dp_mst_encoder_init()`, `intel_dp_mst_encoder_cleanup()`, `intel_dp_mst_source_support()`, `intel_dp_mst_active_streams()`, `intel_dp_mst_add_topology_state_for_crtc()`, `intel_dp_mst_atomic_check_link()`, `intel_dp_mst_crtc_needs_modeset()`, `intel_dp_mst_prepare_probe()`, `intel_dp_mst_verify_dpcd_state()`, `intel_dp_mtp_tu_compute_config()`.
- Encoder helpers: `mst_stream_encoder_create()`, `mst_stream_compute_config()`, `mst_stream_pre_enable()`, `mst_stream_enable()`, `mst_stream_disable()`, `mst_stream_post_disable()`, PLL enable/disable hooks, and config/readout wrappers.
- Connector helpers: `mst_topology_add_connector()`, `mst_connector_mode_valid_ctx()`, `mst_connector_atomic_check()`, `mst_connector_detect_ctx()`, EDID and registration helpers.
- Bandwidth helpers compute overhead, M/N, TU, PBN, DSC slice count, DPT bottleneck bpp, and hblank expansion quirks.

## Control flow
Initialization skips unsupported platforms and eDP, creates one fake MST encoder per pipe, attaches callbacks, and initializes the DRM MST topology manager with i915 callbacks. Topology callbacks dynamically allocate MST connectors, attach every stream encoder, copy properties from the primary SST connector where needed, read decompression DSC caps, detect hblank expansion quirks, and initialize HDCP for the new connector.

Atomic compute starts from maximum link limits, chooses uncompressed or DSC mode, computes local M/N and remote TU/PBN, aligns slots, requests DRM MST time slots, and reduces bpp or enables DSC if needed. Joined-pipe candidates are tried for large modes. Late compute designates the lowest-numbered active transcoder on the MST link as the master transcoder.

Atomic topology checks add related connectors/CRTCs when one stream needs a modeset, release old time slots, verify DSC changes that require all topology pipes to be recomputed, and ask DRM MST core to validate total bandwidth. On ENOSPC, i915 link-bandwidth limits are updated and `-EAGAIN` forces recompute.

Enable sequencing increments active stream count, powers the sink path, enables decompression and primary encoder only for the first stream, adds payload part 1, enables transcoder clock as required by generation/stream order, writes DSC PPS and MSA, enables transcoder function, sets VC payload allocation, waits for ACT, adds payload part 2, handles FEC workaround state, enables transcoder/vblank, and enables HDCP. Disable performs the reverse: disables HDCP/decompression, removes payload in two parts, clears payload allocation, disables VRR/transcoder/DSC/scaler, powers down the MST PHY path, disables infoframes and clocks, and post-disables the primary encoder for the last stream.

## State and persistence
State is stored in `intel_dp->mst`: topology manager, active stream count, stream encoder pointers, and probed link parameters. Each dynamic connector stores `connector->mst.dp`, `connector->mst.port`, DSC aux/quirk data, and current encoder binding. CRTC state stores MST master transcoder, DP M/N/TU, DSC/FEC state, joiner pipes, lane count, link rate, and DP tunnel refs. DRM MST topology state stores payload/time-slot allocations and pending CRTC masks.

## Dependencies and integration points
Depends on DRM MST helpers, atomic helpers, EDID, DP bandwidth helpers, i915 DDI/transcoder/scaler/audio/PSR/VRR/DSC/FEC/HDCP/link bandwidth code, and DP tunnel bandwidth accounting. It integrates with hotplug via topology callbacks and with userspace through dynamically registered DRM connectors and connector properties.

## Risks
MST has high interaction risk: all streams on a topology share link bandwidth and sometimes a master transcoder, so a change for one connector can require modesets and recomputation for others. Bandwidth math mixes local TU, remote PBN, DSC, FEC, SSC, hblank quirks, and hardware alignment requirements. Incorrect active-stream accounting can disable the primary encoder or link while streams remain active. Dynamic connector lifetime and MST port references must stay balanced. Payload part1/part2 ordering and ACT waits are hardware-visible and timing-sensitive.

## Test signals
Signals include MST topology connector creation/removal, EDID reads through MST AUX, mode validation failures, DSC fallback logs, slot/PBN/TU logs, DRM MST atomic ENOSPC paths, ACT status checks, active stream count logs, HDCP enablement, and long hotplug/MST DPCD state reset detection. Test coverage should include multi-monitor MST hubs, SST with sideband support, DSC and non-DSC modes, UHBR MST, payload removal, branch-device resets, and bandwidth oversubscription retries.
