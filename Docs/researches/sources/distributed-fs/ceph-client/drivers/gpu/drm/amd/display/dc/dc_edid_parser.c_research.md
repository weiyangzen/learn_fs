# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.c

## Purpose
`dc_edid_parser.c` is a thin DMCU forwarding layer for EDID CEA and AMD VSDB parsing assistance. It does not parse EDID locally; it sends chunks to firmware and receives acknowledgements or parsed AMD VSDB frame-rate data when the DMCU supports the operations.

## Important APIs, Types, And Functions
`dc_edid_parser_send_cea` fetches `dc->res_pool->dmcu` and calls `dmcu->funcs->send_edid_cea` only when the DMCU exists, is initialized, and exposes that callback. `dc_edid_parser_recv_cea_ack` similarly forwards to `recv_edid_cea_ack`. `dc_edid_parser_recv_amd_vsdb` forwards to `recv_amd_vsdb` and returns version, minimum frame rate, and maximum frame rate through caller-provided pointers.

## Control Flow And State
Each function is guard-then-forward. Failure to find an initialized DMCU or required callback returns `false` without side effects. Persistent state, if any, lives in DMCU firmware and `dc->res_pool->dmcu`; this file only passes buffers and output pointers.

## Dependencies And Integration Points
It includes `dce/dce_dmcu.h` and `dc_edid_parser.h`. It integrates with EDID handling paths that need firmware assistance for CEA extension scanning or AMD vendor-specific data and with older DCE/DMCU platforms rather than DMUB-only paths.

## Risks
The code dereferences `dc->res_pool` and `dmcu->funcs` after only checking `dmcu`, so callers are expected to pass fully constructed `struct dc`. Input ranges `offset`, `total_length`, and `length` are not validated here; firmware callback implementations must enforce EDID bounds. Output pointer validity is caller-owned.

## Test Signals
Mock DMCU tests should cover no DMCU, uninitialized DMCU, missing callbacks, successful callback propagation, and callback failure propagation. EDID integration tests should verify CEA chunk offsets and AMD VSDB frame-rate values match known EDID fixtures.
