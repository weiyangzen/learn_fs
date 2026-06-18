# sources/distributed-fs/ceph-client/drivers/thunderbolt/xdomain.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/xdomain.c` implements Thunderbolt XDomain host-to-host discovery and service enumeration. It exchanges UUID, link-state, lane-bonding, properties, and properties-changed messages over the Thunderbolt control channel; creates `thunderbolt_xdomain` devices; enumerates remote service devices from property directories; exposes sysfs attributes; manages XDomain DMA path HopIDs; and provides registration APIs for XDomain service drivers and protocol handlers. The source was read as a complete 2597-line file for this report.

## Important APIs, Types, and Functions

Public APIs include `tb_is_xdomain_enabled`, `tb_xdomain_request`, `tb_xdomain_response`, `tb_register_protocol_handler`, `tb_unregister_protocol_handler`, `tb_register_service_driver`, `tb_unregister_service_driver`, `tb_xdomain_alloc`, `tb_xdomain_add`, `tb_xdomain_remove`, `tb_xdomain_lane_bonding_enable`, `tb_xdomain_lane_bonding_disable`, `tb_xdomain_alloc_in_hopid`, `tb_xdomain_alloc_out_hopid`, `tb_xdomain_release_in_hopid`, `tb_xdomain_release_out_hopid`, `tb_xdomain_enable_paths`, `tb_xdomain_disable_paths`, `tb_xdomain_find_by_uuid`, `tb_xdomain_find_by_link_depth`, `tb_xdomain_find_by_route`, `tb_xdomain_handle_request`, `tb_register_property_dir`, `tb_unregister_property_dir`, `tb_xdomain_init`, and `tb_xdomain_exit`.

Key local mechanisms are the `XDOMAIN_STATE_*` handshake states, `struct xdomain_request_work`, `xdomain_lock`, `xdomain_property_dir`, `protocol_handlers`, `tb_xdp_fill_header`, `tb_xdp_handle_error`, `tb_xdp_*_request/response` helpers, `update_property_block`, `tb_xdp_handle_request`, `populate_properties`, `enumerate_services`, `tb_xdomain_state_work`, and `tb_xdomain_properties_changed`.

## Control Flow

Outbound request/response paths allocate `struct tb_cfg_request`, install matching/copy callbacks that verify route and UUID, submit through `tb_cfg_request_sync` or `tb_cfg_request`, and translate control-layer errors to Linux errno values. XDomain discovery protocol helpers build typed packets with `tb_xdp_fill_header`, send them as `TB_CFG_PKG_XDOMAIN_REQ` or `RESP`, and parse returned error responses.

Inbound control packets enter `tb_xdomain_handle_request`. Packets with the XDomain discovery UUID are scheduled to process asynchronously in `tb_xdp_handle_request`; packets for other UUIDs are offered to registered protocol handlers under `xdomain_lock`. The work handler resolves the route, finds the matching XDomain, updates local property blocks, and responds to UUID, properties, properties-changed, link-state status, and link-state change requests.

Discovery is a delayed-work state machine. It starts in `INIT`, optionally reads the remote UUID, optionally probes link status and negotiates lane bonding, sends a properties-changed notification, fetches remote properties, parses them, adds the XDomain device, and enumerates service child devices. Retryable failures reschedule the same state; non-retryable discovery failures move to `ERROR` and stop handshake work.

Service enumeration walks the remote property directory. Missing services are unregistered, existing service keys are retained, and new `struct tb_service` devices are allocated, populated from protocol properties, assigned IDs from `ida`, registered on `tb_bus_type`, and made discoverable through modalias and sysfs attributes.

## State and Persistence Behavior

Important state lives in `struct tb_xdomain`: local and remote UUIDs, route, local/remote HopID limits, link speed and width, lane-bonding flags, work items, retry counters, property blocks, parsed remote properties, service IDA, HopID IDAs, vendor/device IDs, names, and device registration state. Global mutable state includes the local property template, its generation counter, the protocol handler list, and the `xdomain` module parameter. State is in memory only, but it controls hardware link width, lane adapter bonding, and approved DMA paths. Remote property changes are represented by generation counters and uevents, not by filesystem persistence.

## Dependencies and Integration Points

The file depends on Thunderbolt control-channel request APIs, topology lookup, `tb_property` formatting/parsing, `tb_bus_type`, runtime PM, workqueues, UUID helpers, IDA allocation, PM sleep callbacks, link speed/width helpers, lane bonding helpers, debugfs hooks, and domain path approval/disconnection callbacks. It integrates with service drivers through `tb_register_service_driver`, with service advertisement through `tb_register_property_dir`, with cross-domain data protocols through `tb_register_protocol_handler`, and with userspace through `thunderbolt_xdomain` and `thunderbolt_service` sysfs devices and modalias uevents.

## Risks and Edge Cases

The handshake is asynchronous and route-based, so stale packets, unplug races, or UUID changes can cause retries, device replacement, or `is_unplugged` handling. Properties are length-delimited and chunked; offset, generation, and maximum-length validation are critical to avoid malformed remote input. Lock ordering requires `xdomain_lock` before `xd->lock`. Lane bonding has a split-brain avoidance rule based on UUID ordering; failures intentionally fall back to unbonded operation. HopID allocation must respect local and remote maximums. Service enumeration must handle partial allocation failures without leaving broken child devices.

## Test Signals

Useful signals include host-to-host attach and detach; XDomain disabled by module parameter or ACPI policy; UUID request/response retries and loopback detection; property block parsing, generation updates, and properties-changed notifications; service modalias uevents and driver binding; lane-bonding negotiation with lower and higher UUID sides; suspend/resume restarting the handshake; HopID allocation exhaustion and release; DMA path enable/disable for XDomain services; and malformed XDomain packet length/UUID/route rejection.
