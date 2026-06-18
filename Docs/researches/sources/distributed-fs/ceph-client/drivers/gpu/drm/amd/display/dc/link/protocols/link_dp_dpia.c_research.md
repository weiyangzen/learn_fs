# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.c

## Purpose
`link_dp_dpia.c` implements DP tunneling over USB4 DisplayPort-in-Adapter (DPIA) support that is not specific to bandwidth allocation. It reads USB4 tunneling DPCD registers, queries DPIA HPD state through DMUB, and derives stream tunnel settings from previously detected DPCD/DPIA bandwidth state.

## Important APIs
- `dpcd_get_tunneling_device_data()` reads tunneling support, adapter info, USB4 driver/router IDs, optional bandwidth capability/tunnel info, and topology ID into `link->dpcd_caps.usb4_dp_tun_info`.
- `dpia_query_hpd_status()` sends `DMUB_CMD__QUERY_HPD_STATE` with `AUX_CHANNEL_DPIA`, updates `link->hpd_status`, and returns the current HPD state.
- `link_decide_dp_tunnel_settings()` populates `struct dc_tunnel_settings` for DP SST/MST streams, including whether tunneling and DP bandwidth allocation should be used.

## Control Flow
Capability retrieval starts by reading three DPCD bytes at the DP tunneling support block. If DP tunneling is not advertised or a read fails, the function exits with the current status. If bandwidth allocation is advertised, it reads `USB4_DRIVER_BW_CAPABILITY` and `DP_IN_ADAPTER_TUNNEL_INFO`. It logs router/adapter IDs and then reads the USB4 topology ID byte array.

HPD query builds a DMUB ring-buffer command using the link enum ID as the DPIA instance. Success updates `link->hpd_status` from DMUB; failure logs and forces the link HPD state false.

Tunnel settings are decided only for DP SST/MST streams. The function copies bandwidth allocation identifiers and current `dpia_bw_alloc_config` values when both DPIA and connection manager bandwidth allocation are supported.

## State And Persistence
State written here includes `link->dpcd_caps.usb4_dp_tun_info`, `link->hpd_status`, and per-stream `dc_tunnel_settings`. It reads persistent `link->dpia_bw_alloc_config` values that are maintained by `link_dp_dpia_bw.c`.

## Dependencies And Integration Points
The file depends on DPCD helpers, DMUB command infrastructure, DM helpers, DP training headers, and link HWSS definitions. Capability data is consumed by `link_dp_capability.c`, bandwidth management, validation, and stream commit code that configures DP tunnels.

## Risks And Test Signals
Risk areas are stale or partial DPCD tunneling data after early `goto err`, DMUB HPD query failure forcing HPD low, instance numbering via `enum_id - ENUM_ID_1`, and consistency between DPCD bandwidth metadata and `dpia_bw_alloc_config`. Test with USB4 DPIA docks that support no tunneling, tunneling without BW allocation, full BW allocation, DMUB query failure, and MST tunnel settings.
