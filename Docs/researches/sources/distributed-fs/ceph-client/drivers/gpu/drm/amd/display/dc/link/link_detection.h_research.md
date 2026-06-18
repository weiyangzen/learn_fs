# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.h

## Purpose

`link_detection.h` declares the public link detection and sink-management interface installed into `struct link_service`.

## Important APIs, Types, And Functions

It declares `link_detect()`, `link_detect_connection_type()`, `link_add_remote_sink()`, `link_remove_remote_sink()`, `link_reset_cur_dp_mst_topology()`, `link_get_status()`, `link_is_hdcp14()`, `link_is_hdcp22()`, and `link_clear_dprx_states()`.

## Control Flow

The header has no runtime flow. The functions form the external entry points for local sink detection, MST remote sink management, connection-type probing, HDCP capability queries, and DPRX state clearing.

## State And Persistence Behavior

No state is held in the header. Implementations mutate `struct dc_link` sink, DPCD, HDCP, topology, and capability state and manage `struct dc_sink` references.

## Dependencies And Integration Points

It includes `link_service.h` for link, sink, status, and detection reason types. `link_factory.c` maps these declarations into `link_service` function pointers.

## Risks And Edge Cases

The API mixes queries with mutating operations. Callers must know that `link_detect()` and remote sink functions can allocate/release sinks and change topology state. HDCP helpers report cached capability state and depend on prior detection queries.

## Test Signals

Build coverage catches prototype drift. Runtime validation comes from hotplug, MST topology, remote sink add/remove, HDCP queries, and DPRX state clear paths.
