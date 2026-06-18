# sources/distributed-fs/ceph-client/include/linux/dtpm.h

## Purpose
This header declares Dynamic Thermal Power Management hierarchy support. It models powercap zones as DTPM nodes and provides registration and hierarchy creation APIs.

## Important APIs, types, and functions
`struct dtpm` embeds `struct powercap_zone` and stores parent/child/sibling links, ops, flags, power limit/max/min, and weight. `struct dtpm_ops` provides set/get/update power and release callbacks. `struct dtpm_subsys_ops` declares subsystem init/exit/setup. `enum DTPM_NODE_TYPE` distinguishes virtual and device-tree nodes, and `struct dtpm_node` describes static hierarchy nodes. APIs include `to_dtpm()`, `dtpm_update_power()`, `dtpm_release_zone()`, `dtpm_init()`, `dtpm_unregister()`, `dtpm_register()`, `dtpm_create_hierarchy()`, and `dtpm_destroy_hierarchy()`.

## Control flow, state, and persistence
DTPM state persists as a powercap-zone hierarchy. Parent/child lists model aggregate and leaf power zones; ops update current power and limits. Hierarchy creation consumes OF match tables and subsystem setup callbacks.

## Dependencies and integration points
It depends on `linux/powercap.h` and device-tree types. It integrates with thermal/powercap control, SoC energy models, and platform-specific DTPM subsystems.

## Risks and test signals
Risks include inconsistent parent/child accounting, missing release callbacks, unit mistakes for microwatts, and hierarchy teardown leaks. Tests should cover registration/unregistration, aggregate power updates, power limit propagation, OF hierarchy creation, and release paths.
