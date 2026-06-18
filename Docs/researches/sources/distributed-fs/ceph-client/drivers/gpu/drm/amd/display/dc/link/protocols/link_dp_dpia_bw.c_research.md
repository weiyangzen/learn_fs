# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.c

## Purpose
`link_dp_dpia_bw.c` implements USB4 DPIA DisplayPort bandwidth allocation. It enables DPTX bandwidth allocation mode, reads allocation granularity and estimates, sends requested bandwidth values, handles tunneling IRQ status, resets state on unplug, calculates MST overhead, and validates aggregate DP tunnel bandwidth per USB4 router.

## Important APIs And Helpers
- `link_dp_is_bw_alloc_available()` gates allocation on DP tunneling, DPIA BW allocation support, and driver/connection-manager support.
- `reset_bw_alloc_struct()` clears `link->dpia_bw_alloc_config`, including per-remote-sink requested bandwidth.
- `get_bw_granularity()`, `get_estimated_bw()`, `get_non_reduced_max_link_rate()`, and `get_non_reduced_max_lane_count()` read DPCD bandwidth allocation fields.
- `retrieve_usb4_dp_bw_allocation_info()` resets and repopulates allocation state.
- `link_dpia_send_bw_alloc_request()` rounds a requested bandwidth to DPCD granularity, caps it to estimated bandwidth, stores `allocated_bw`, and writes `REQUESTED_BW`.
- `link_dpia_enable_usb4_dp_bw_alloc_mode()` writes `DPTX_BW_ALLOCATION_MODE_CONTROL`, reads allocation info, updates reported link cap from non-reduced fields, marks allocation enabled, and optionally sends a zero-allocation patch.
- `link_dp_dpia_handle_bw_alloc_status()` handles success/failure/capability/estimate changed bits and clears the DPCD tunneling status.
- `dpia_handle_usb4_bandwidth_allocation_for_link()` requests peak bandwidth or resets on unplug.
- `link_dp_dpia_allocate_usb4_bandwidth_for_stream()` refreshes estimate and requests stream bandwidth when available.
- `link_dpia_get_dp_overhead()` adds MST MTP overhead for 8b/10b MST branches.
- `link_dpia_validate_dp_tunnel_bandwidth()` aggregates per-router required/allocated/estimated bandwidth and validates requested bandwidth against available capacity.

## Control Flow
On plug or capability setup, callers enable BW allocation mode. The enable path writes mode/IRQ bits, resets and reads bandwidth state, updates reported link cap if non-reduced max link/lane fields are present, and may issue a zero request to release connection-manager preallocation. Stream allocation paths refresh estimated bandwidth, convert requested kbps to a DPCD register value using `bw_granularity`, round up to the next granularity, cap to `estimated_bw`, update `allocated_bw`, and write `REQUESTED_BW`.

At runtime, HPD IRQ handling reads `DP_TUNNELING_STATUS` and forwards bandwidth bits here. Failed requests trigger a request for the full estimated bandwidth. Changed granularity or estimate bits cause fresh reads. The status byte is then written back to clear the sink/adapter status.

Validation groups `dc_validation_dpia_set` entries by connection-manager/router ID. For each link it rounds required bandwidth up to tunnel granularity, adds MST overhead when needed, accumulates required and allocated bandwidth, tracks remaining and max estimated bandwidth, then checks whether required bandwidth fits either the single-DPIA estimate or the aggregate allocated-plus-remaining budget.

## State And Persistence
The owner state is `link->dpia_bw_alloc_config`: `bw_alloc_enabled`, verified/max/allocated/estimated bandwidth, granularity, overhead, non-reduced max link/lane, and remote sink requests. The file also updates `link->reported_link_cap` from USB4 non-reduced capabilities and clears DP tunneling status DPCD bits after IRQ handling.

## Dependencies And Integration Points
This file depends on DPCD helpers, DMUB service headers, USB4/DPIA DPCD definitions, `dc_validation_dpia_set`, `dc_tunnel_settings`, MST link types, and current link caps. It is called by DPIA capability setup, stream validation, HPD IRQ handling, plug/unplug handling, and MST bandwidth update paths.

## Risks And Edge Cases
- `link_dpia_send_bw_alloc_request()` has integer rounding/capping behavior; incorrect granularity creates over- or under-allocation.
- A zero `bw_granularity` aborts allocation but leaves previous state except for logs.
- Failed requests immediately ask for `estimated_bw`, which may be aggressive on congested routers.
- `link_dpia_validate_dp_tunnel_bandwidth()` breaks out on null data rather than reporting hard failure, so malformed sets can lead to partial validation.
- Router aggregation assumes `cm_id` is the right grouping key and relies on fixed `MAX_HOST_ROUTERS_NUM`.
- MST overhead is only added for 8b/10b MST branches.

## Test Signals
Test USB4 tunnel plug/unplug, enable mode DPCD writes, zero-allocation debug patch, allocation rounding for 0.25/0.5/1 Gbps granularities, allocation failure IRQ handling, estimated/granularity changed IRQs, MST overhead calculation, multi-DPIA same-router validation, different-router validation, and null/zero validation inputs.
