# sources/distributed-fs/ceph-client/net/dsa/devlink.c

## Purpose
This file adapts DSA switch and port objects to the generic devlink subsystem. It provides devlink ops callbacks that forward to optional `dsa_switch_ops`, helper exports for DSA drivers to register params/resources/regions, and per-port devlink port lifecycle during DSA port setup.

## Important APIs, Types, And Functions
`dsa_devlink_ops` implements devlink info and shared-buffer callbacks by translating from `struct devlink` or `struct devlink_port` back to `struct dsa_switch` and port index. Exported helpers include `dsa_devlink_param_get()`, `dsa_devlink_param_set()`, `dsa_devlink_params_register()`, `dsa_devlink_params_unregister()`, resource register/unregister and occupancy helpers, region create/destroy helpers, `dsa_port_devlink_setup()`, `dsa_port_devlink_teardown()`, `dsa_switch_devlink_alloc()`, `dsa_switch_devlink_free()`, `dsa_switch_devlink_register()`, and `dsa_switch_devlink_unregister()`.

## Control Flow
Switch setup allocates a devlink with `devlink_alloc()`, stores the owning `struct dsa_switch` in private data, lets switch setup add devlink objects, then registers devlink after the switch is ready. Port setup initializes a `devlink_port`, optionally calls driver `port_setup`, sets attributes with tree index as switch ID and flavour based on DSA port type, then registers the port. Teardown unregisters the devlink port, calls optional driver `port_teardown`, and finalizes the port object.

Driver-facing resource helpers lock `ds->devlink` for devl resource operations. Param helpers are thin callback shims and registration wrappers. Region helpers attach either to the switch devlink or a specific DSA devlink port.

## State And Persistence
The main state is `ds->devlink` and each `dp->devlink_port`. Devlink params, resources, regions, and shared-buffer objects persist while registered by drivers and are removed during switch/port teardown.

## Dependencies And Integration Points
This integrates DSA with `net/devlink.h`, driver callbacks in `struct dsa_switch_ops`, devlink resources, devlink params, devlink regions, and devlink ports. It is called from `dsa.c` port and switch setup paths.

## Risks And Edge Cases
Most devlink ops return `-EOPNOTSUPP` when a switch driver lacks a callback; userspace must handle optional capability. Port setup must call driver `port_teardown` on devlink port registration failure, and this file does. The switch ID is derived from the tree index only, so multi-tree uniqueness relies on that index.

## Test Signals
Tests should verify devlink registration for switches and all port flavours, callback forwarding, optional callback absence, param/resource/region registration from drivers, and failure rollback in port registration.
