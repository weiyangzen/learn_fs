# sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.c

## Purpose

This file implements the kernel-space core of the DPLL subsystem. It manages DPLL device and pin object identity, reference counting, registration with user-visible state, pin-to-DPLL and pin-to-parent relationships, notifier fanout, optional reference tracking, netdevice pin association, and generic-netlink family initialization.

## Important APIs, Types, and Functions

Global state consists of `dpll_lock`, `dpll_device_xa`, `dpll_pin_xa`, a raw notifier chain, an IDA for dynamically assigned pin indexes, and cyclic xarray allocation cursors. Internal registration records (`dpll_device_registration` and `dpll_pin_registration`) attach provider ops and private data to devices and references. Public exported APIs include `dpll_device_get/put/register/unregister`, `dpll_pin_get/put/register/unregister`, `dpll_pin_on_pin_register/unregister`, `dpll_pin_ref_sync_pair_add`, `dpll_pin_fwnode_set`, `fwnode_dpll_pin_find`, netdevice pin set/clear helpers, and DPLL notifier registration.

The core lookup helpers `dpll_priv()`, `dpll_device_ops()`, `dpll_pin_on_dpll_priv()`, `dpll_pin_on_pin_priv()`, and `dpll_pin_ops()` are used heavily by `dpll_netlink.c` to route user-space operations to the provider callbacks associated with a given DPLL or pin reference.

## Control Flow

`dpll_device_get()` and `dpll_pin_get()` search global xarrays for an existing object matching `(clock_id, index, module)`, increment its tracked refcount if found, or allocate a new object with a unique subsystem ID. Device registration validates required ops (`mode_get`, `lock_status_get`) and type range, adds a registration record, marks the object as `DPLL_REGISTERED` only for the first registration, and emits create notification. Unregistration removes the matching registration, drops the held reference, sends delete notification, and clears the registered mark when no registrations remain.

Pin allocation duplicates provider properties, including labels and supported frequency arrays, initializes xarrays for DPLL refs, parent refs, and reference-sync pins, and allocates a global pin ID. `dpll_pin_register()` validates required pin ops, enforces matching module/clock identity with the DPLL, adds reciprocal references between the DPLL and pin, marks the pin registered, and emits a create notification. `dpll_pin_on_pin_register()` supports child pins under mux parent pins by adding a parent reference and registering the child against every DPLL connected to the parent. Unregister paths delete notifications, remove reciprocal references, clear registration marks when no DPLL refs remain, and drop reference counts.

Reference-sync pairs are kept in each pin's `ref_sync_pins` xarray. Adding a pair inserts the sync pin and emits a change notification; unregistering a pin scans all pins and removes references to the departing pin. Module initialization registers the DPLL generic-netlink family at `subsys_initcall` time; exit unregisters it and destroys the mutex.

## State and Persistence

All subsystem state is volatile kernel memory. Device and pin identities live in global xarrays and are guarded by `dpll_lock`. Object lifetime uses refcounts plus optional `ref_tracker` allocations when `CONFIG_DPLL_REFCNT_TRACKER` is enabled. Pins use RCU freeing (`kfree_rcu`) after final put, while devices are freed directly after xarray removal and registration-list checks. Registration marks in the xarrays distinguish allocated objects from user-visible registered objects. No state survives reboot or module unload.

## Dependencies and Integration Points

The file depends on Linux xarray, IDA, refcount, optional ref_tracker, notifier chains, firmware-node references, rtnetlink for assigning `dev->dpll_pin`, and the generated DPLL generic-netlink family. It integrates with public provider APIs in `include/linux/dpll.h` and with `dpll_netlink.c`, which assumes these helpers run under the DPLL core's object model. Provider drivers supply `dpll_device_ops`, `dpll_pin_ops`, private pointers, and stable clock/index identities.

## Risks and Edge Cases

The code relies on strict lock discipline: most object graph mutations require `dpll_lock`, while netdevice assignment uses RTNL. Registration records can stack multiple providers/owners on one object, but helper functions return the first registration, so multi-registration semantics must stay intentional. `dpll_pin_on_pin_unregister()` iterates `pin->dpll_refs` while unregistering entries, a pattern that should be reviewed carefully for xarray iteration safety. Unregistering a directly registered pin warns if it still has parent refs, preventing removal while child topology remains. Dynamic pin indexes are mapped above `INT_MAX`, and explicit provider indexes above `INT_MAX` are rejected; tests should cover both paths.

## Test Signals

Useful tests include provider get/register/unregister/put sequences, duplicate registration returning `-EEXIST`, invalid ops/type/property validation, dynamic pin index allocation and free, pin-on-DPLL and pin-on-pin topologies, reference-sync add and cleanup on pin unregister, fwnode lookup with refcounting, notifier delivery for create/delete/change, ref-tracker leak reports when enabled, and generic-netlink registration/unregistration during module init/exit.
