# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/base.c

## Purpose
Implements OMAP DSS base helpers for DSS device registration, output iteration, device connection, and component readiness discovery from device tree graph links.

## Important APIs, Types, And Functions
Important APIs include `dispc_get_dispc()`, `omapdss_device_register()`, `omapdss_device_unregister()`, `omapdss_device_get()`, `omapdss_device_put()`, `omapdss_find_device_by_node()`, `omapdss_device_next_output()`, `omapdss_device_connect()`, `omapdss_device_disconnect()`, `omapdss_gather_components()`, and `omapdss_stack_is_ready()`.

## Control Flow
DSS devices register on a global protected list. Output iteration returns registered devices with IDs and bridges while managing references. Component gathering walks the DSS node, children, and remote graph endpoints into a component list; readiness checks that OMAPDSS-specific external components have registered.

## State, Persistence, And Dependencies
State includes the global `omapdss_devices_list` protected by `omapdss_devices_lock` and the component list built with devm allocations. Device references are managed through `get_device()`/`put_device()`.

## Integration Points
Depends on OF graph helpers, platform device data, DSS/OMAPDSS structures, bridge-bearing output devices, and Linux device reference counting.

## Risks
Some list traversals such as `omapdss_find_device_by_node()` assume caller-side serialization. Component list is global and reinitialized during gather, so concurrent gather/use would be unsafe. Connect rejects already connected devices with `-EBUSY`.

## Test Signals
Signals include complete component discovery from device tree, stack-ready only after external OMAPDSS components register, balanced device references during output iteration, and successful connect/disconnect logs.
