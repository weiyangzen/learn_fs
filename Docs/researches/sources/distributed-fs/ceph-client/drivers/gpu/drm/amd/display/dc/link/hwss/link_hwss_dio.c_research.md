# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.c

## Purpose

`link_hwss_dio.c` implements the Display Input Output link hardware sequencing surface for legacy DIO-backed links. It adapts generic `struct link_hwss` operations to DIO link encoders and stream encoders for DP, HDMI, DVI, LVDS, audio packets, MST allocation tables, lane settings, and DP PHY test patterns.

## Important APIs, Types, And Functions

- `setup_dio_stream_encoder()` connects DIG back end to front end for non-RGB signals, enables the stream encoder, maps it to a link encoder, sets DIO pixels-per-cycle input mode, and enables FIFO.
- `reset_dio_stream_encoder()` reverses FIFO/input/stream enable state and disconnects DIG FE/BE for non-RGB signals.
- `setup_dio_stream_attribute()` programs DP, HDMI TMDS, DVI, or LVDS timing attributes and DP trace points.
- `enable_dio_dp_link_output()` and `disable_dio_link_output()` call link encoder output enable/disable functions for SST/MST DP.
- `set_dio_dp_link_test_pattern()`, `set_dio_dp_lane_settings()`, and `update_dio_stream_allocation_table()` forward DP training/test/MST table operations to the link encoder.
- Audio APIs route DP audio setup/enable/disable or HDMI audio setup/disable through `stream_enc->funcs`.
- `can_use_dio_link_hwss()` and `get_dio_link_hwss()` expose the static DIO HWSS vtable.

## Control Flow

The vtable maps generic link programming to per-resource function pointers. Most entry points first resolve `link_enc` from `pipe_ctx->link_res.dio_link_enc`; if `unify_link_enc_assignment` is disabled, they instead query `link_enc_cfg_get_link_enc(link)`. Null link encoders assert and return.

DP stream setup order is significant: connect DIG FE/BE, trace, enable stream, map stream to link, set input mode, then enable FIFO. Reset runs the reverse subset and records DP trace after disconnect. Attribute programming dispatches by signal type and uses DPCD caps for DP split SDP support.

## State And Persistence Behavior

The file does not persist data. It mutates hardware through function pointers and updates observable in-memory/link state indirectly through encoder programming. DP trace source-sequence calls record source-side milestones. Audio packet enable/disable changes stream encoder packet and mute state. MST allocation updates affect link encoder allocation tables but the owning software table is maintained by DPMS code.

## Dependencies And Integration Points

It depends on `core_types.h`, `link_hwss_dio.h`, `link_enc_cfg.h`, stream encoder and link encoder function tables, `dc_is_*_signal()` helpers, DP trace service hooks, and `struct pipe_ctx` resource assignments. `link_dpms.c`, DP training, and `get_link_hwss()` dispatch through this vtable for DIO links and DIO-based DPIA variants.

## Risks And Edge Cases

- The non-unified encoder path relies on `link_enc_cfg_get_link_enc()` being valid at the moment of programming.
- Some stream encoder function pointers are optional while others are called unconditionally, so resource construction must match signal type.
- DP trace calls assume `link_srv` is populated.
- Audio mute is always toggled even if DP audio enable is skipped, which is intended but sensitive to stream encoder implementation.
- Mapping stream to link uses `transmitter - TRANSMITTER_UNIPHY_A`; unexpected transmitter values would produce bad indices.

## Test Signals

Build tests catch vtable signature drift. Runtime coverage should include DIO DP SST/MST, HDMI/DVI/LVDS, unified and dynamic link encoder assignment, audio enable/disable, MST payload table updates, DP test patterns, and lane setting changes. DP trace events around DIG connect/disconnect, stream attribute setup, link PHY enable/disable, and audio transitions are useful observability.
