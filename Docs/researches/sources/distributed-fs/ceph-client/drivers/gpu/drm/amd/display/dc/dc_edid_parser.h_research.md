# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.h

## Purpose
`dc_edid_parser.h` declares the DMCU-backed EDID parser forwarding API for sending CEA data and receiving parser acknowledgements or AMD VSDB data.

## Important APIs
The header exports `dc_edid_parser_send_cea`, `dc_edid_parser_recv_cea_ack`, and `dc_edid_parser_recv_amd_vsdb`. The APIs use `struct dc *` from `core_types.h`, integer offsets and lengths, mutable byte buffers, and output pointer parameters for acknowledgements and frame-rate data.

## Control Flow And State
There is no implementation in the header. State is external: the current DC resource pool must provide an initialized DMCU with matching function pointers. The API returns `bool` to indicate whether firmware communication succeeded.

## Dependencies And Integration Points
It includes `core_types.h` rather than the wider public `dc.h`, keeping the declaration tied to DC internals. EDID code and DMCU firmware service implementations are its primary integration points.

## Risks
The API exposes raw `uint8_t *data` without `const` for send operations, so ownership and mutation expectations are not explicit. Length and pointer validation are not expressible in the prototype and must be handled by callers/implementation.

## Test Signals
Compilation of EDID parser users, DMCU mock callback coverage, and EDID fixture tests using AMD VSDB blocks are the key signals.
