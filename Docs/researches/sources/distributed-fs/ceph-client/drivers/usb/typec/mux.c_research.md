<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux.c

## Purpose

`mux.c` implements the generic USB Type-C orientation switch and mode mux framework. It lets port/controller drivers find one or more fwnode-linked switch/mux devices and lets hardware drivers register switch or mux devices under the `typec_mux` class.

## Important APIs, Types, and Functions

Exported APIs include `fwnode_typec_switch_get()`, `typec_switch_get()` via public wrappers, `typec_switch_put()`, `typec_switch_register()`, `typec_switch_unregister()`, `typec_switch_set()`, switch drvdata accessors, and equivalent mux APIs `fwnode_typec_mux_get()`, `typec_mux_put()`, `typec_mux_register()`, `typec_mux_unregister()`, `typec_mux_set()`, and mux drvdata accessors. Private aggregate handles store up to `TYPEC_MUX_MAX_DEVS` underlying devices.

## Control Flow

Lookup uses `fwnode_connection_find_matches()` and class searches. Graph endpoints are filtered by `orientation-switch` or `mode-switch` properties, duplicates are skipped, missing but referenced devices return `-EPROBE_DEFER`, and matched parent modules are pinned. Set calls fan out to all devices and ignores `-EOPNOTSUPP` so composite paths can tolerate devices that do not implement a specific mode. Registration allocates a device, assigns parent/fwnode/class/type/driver data/name, and calls `device_add()`. Put reverses module and device references.

## State and Persistence Behavior

Aggregate `struct typec_switch`/`struct typec_mux` handles are heap allocations containing referenced switch/mux device pointers. Registered device state lives in `struct typec_switch_dev` and `struct typec_mux_dev` until device unregister/release. No persistent state exists.

## Dependencies and Integration Points

The file integrates Linux class/device core, fwnode graph connections, module refcounts, Type-C class private device-type checks, and public Type-C mux APIs. It is used by `class.c`, controller drivers, and all chip-specific mux/retimer drivers in this subset.

## Risks and Test Signals

Risks include duplicate-skip logic dereferencing a NULL `dev` in this snapshot, duplicated `IS_ERR_OR_NULL(sw)` check in `typec_switch_set()`, module owner assumptions through parent driver pointers, max-device truncation at three entries, and handling of mixed devices returning `-EOPNOTSUPP`. Test signals include fwnode lookup with no connection, deferred probe, duplicate graph edges, multiple chained muxes, unregister/put module ref balancing, and registration failure after device initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux.c -->
