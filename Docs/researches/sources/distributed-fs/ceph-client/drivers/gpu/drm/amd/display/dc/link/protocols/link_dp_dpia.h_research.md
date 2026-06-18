# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.h

## Purpose
`link_dp_dpia.h` declares the USB4 DPIA tunneling interface: DPCD capability retrieval, HPD querying, and stream tunnel setting selection.

## Important APIs
- `dpcd_get_tunneling_device_data(struct dc_link *link)` updates link DPCD tunneling capability state.
- `dpia_query_hpd_status(struct dc_link *link)` returns true when the DPIA HPD state is high.
- `link_decide_dp_tunnel_settings(struct dc_stream_state *stream, struct dc_tunnel_settings *dp_tunnel_setting)` fills stream tunnel settings from link capability and allocation state.

## Control Flow And Integration
DP capability detection calls the DPCD retrieval function, HPD detection paths can query DMUB through `dpia_query_hpd_status()`, and stream validation/commit uses the tunnel settings decision helper. The header includes only `link_service.h`, keeping DPIA internals out of consumers.

## State, Risks, And Test Signals
The functions operate on `dc_link` and `dc_stream_state` state owned elsewhere. Risk is mainly that callers must only rely on tunnel settings after successful capability detection. Compile and runtime tests should cover USB4 DPIA links with and without bandwidth allocation and HPD state changes reported through DMUB.
