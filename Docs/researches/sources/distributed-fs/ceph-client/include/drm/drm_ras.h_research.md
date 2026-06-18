# sources/distributed-fs/ceph-client/include/drm/drm_ras.h

## Purpose
`drm_ras.h` declares DRM reliability/availability/serviceability node registration for exposing driver error counters through the DRM RAS netlink/UAPI layer.

## Important APIs, types, and functions
`struct drm_ras_node` contains dynamically assigned `id`, driver-provided `device_name` and `node_name`, a UAPI `enum drm_ras_node_type`, an inclusive `error_counter_range`, a mandatory `query_error_counter` callback for error-counter nodes, and driver-private `priv`. APIs are `drm_ras_node_register` and `drm_ras_node_unregister`, with no-op success stubs when `CONFIG_DRM_RAS` is disabled.

## Control flow
A driver fills a node, including supported error ID range and query callback, then registers it. Netlink queries iterate IDs from `first` to `last`; `-ENOENT` means skip an unsupported non-contiguous ID, while other errors terminate the query. Unregister removes the node from the RAS service.

## State and persistence
State is runtime node registration and counter values queried live from the driver. Error counts may be hardware-maintained, but this header only describes access and registration state.

## Dependencies and integration points
It depends on `uapi/drm/drm_ras.h` and integrates with the DRM RAS generic netlink family plus driver error counter providers.

## Risks and test signals
Risks include registering nodes with invalid ranges, callbacks returning inconsistent names/values, failure to unregister before driver data is freed, treating `-ENOENT` as fatal, and config-disabled stubs hiding missing runtime support. Test signals include CONFIG_DRM_RAS on/off builds, node register/unregister, contiguous and sparse error ranges, netlink query error handling, device removal during query, and UAPI enum compatibility.
