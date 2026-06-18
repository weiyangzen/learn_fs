# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.h

## Purpose
`link_dp_dpia_bw.h` exposes USB4 DPIA DP bandwidth allocation APIs and the per-router aggregation structure used during validation.

## Important Types And APIs
- `enum bw_type` names estimated, allocated, and invalid host-router bandwidth categories.
- `struct usb4_router_validation_set` stores router grouping state: validity, connection-manager ID, DPIA count, required bandwidth, allocated bandwidth, estimated bandwidth, and remaining bandwidth.
- `link_dpia_enable_usb4_dp_bw_alloc_mode()` enables DPTX BW allocation mode and initializes link allocation state.
- `link_dp_dpia_allocate_usb4_bandwidth_for_stream()` sends per-stream allocation requests.
- `dpia_handle_usb4_bandwidth_allocation_for_link()` handles plug/unplug allocation behavior for a link.
- `link_dpia_get_dp_overhead()` computes DP tunneling overhead.
- `link_dp_dpia_handle_bw_alloc_status()` handles status bits from DP tunneling IRQ.
- `link_dpia_validate_dp_tunnel_bandwidth()` validates aggregate bandwidth requests.

## Control Flow And Integration
The header is used by HPD IRQ code, USB4 tunnel validation, and stream/link management code. It bridges DPCD-based allocation mechanics with higher-level `dc_validation_dpia_set` validation.

## State, Risks, And Test Signals
The APIs mutate `link->dpia_bw_alloc_config` and read tunnel settings. Risks include keeping declarations synchronized with DPCD status semantics and validation structures. Test signals include compile coverage for validation, HPD IRQ status dispatch, stream allocation, and plug/unplug paths.
