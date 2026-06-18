# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dm_cp_psp.h

## Purpose
Defines the Display Core interface to content-protection/PSP services for ASSR and stream configuration updates. It lets DC describe display stream encoder/link/PHY state to the HDCP/PSP integration layer without depending on implementation details.

## Important APIs, Types, And Functions
`struct cp_psp_stream_config` carries OTG, DIG backend/frontend, link encoder, stream encoder, DIO output, PHY, ASSR, MST, DP2, USB4, DM stream context, and DPMS-off state. `struct cp_psp_funcs` declares `enable_assr()` and `update_stream_config()` callbacks. `struct cp_psp` stores an opaque handle and callback table.

## Control Flow
The header has no implementation. DC or HDCP modules populate `cp_psp` callbacks, and Display Core invokes them when ASSR must be enabled or stream topology changes need to be reported.

## State And Persistence
Persistent state is external: `cp_psp.handle` points to owner state, and each `cp_psp_stream_config` is a transient description passed to callbacks. The header itself stores no state.

## Dependencies And Integration Points
Forward-declares `struct dc_link` and is included by `dc_types.h` and HDCP/DM code. Implementations appear in AMDGPU DM HDCP integration, where callbacks connect DC stream/link state to HDCP workqueue and PSP operations.

## Risks
The config uses compact `uint8_t` identifiers, so invalid instance values or truncation can misidentify hardware blocks. `dm_stream_ctx` is opaque and ownership/lifetime must be managed by the caller. Missing callbacks or stale stream updates can break ASSR/content-protection sequencing, especially for MST, DP2, USB4, or DPMS transitions.

## Test Signals
HDCP/ASSR tests should verify `enable_assr()` is called for supported links and `update_stream_config()` receives correct OTG/DIG/PHY/stream ids across enable, disable, MST, DP2, USB4, and DPMS-off transitions. Compile coverage ensures the callback signatures stay aligned with DM implementations.
