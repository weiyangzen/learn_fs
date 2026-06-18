# sources/distributed-fs/ceph-client/drivers/powercap/dtpm.c

## Purpose
`dtpm.c` implements the generic Dynamic Thermal Power Management powercap hierarchy. It creates virtual and device-backed powercap zones, aggregates child power, distributes power limits down the tree by weights, and exports hierarchy creation/destruction APIs.

## Important APIs, Types, And Functions
Global state is protected by `dtpm_lock` and includes the powercap control type `pct` and `root`. Public APIs are `dtpm_init()`, `dtpm_register()`, `dtpm_unregister()`, `dtpm_update_power()`, `dtpm_release_zone()`, `dtpm_create_hierarchy()`, and `dtpm_destroy_hierarchy()`. Powercap callbacks include `get_power_uw()`, `set_power_limit_uw()`, `get_power_limit_uw()`, `get_max_power_range_uw()`, and constraint-name helpers. Hierarchy setup uses `dtpm_setup_virtual()`, `dtpm_setup_dt()`, `dtpm_for_each_child()`, and the subsystem table from `dtpm_subsys.h`.

## Control Flow
`dtpm_create_hierarchy()` registers a `dtpm` control type, obtains a platform hierarchy via `of_machine_get_match_data()`, walks child descriptors recursively, creates virtual nodes directly, and asks each enabled subsystem to bind DT nodes as leaves. Leaf nodes provide `dtpm_ops`; virtual nodes aggregate children. Limit writes are clamped to a node's min/max, then `__set_power_limit_uw()` either calls a leaf's `set_power_uw()` or divides the request among children by 1024-based weights. `dtpm_update_power()` subtracts old values from ancestors, refreshes leaf power, restores unconstrained limit to max, adds values back, and rebalances weights.

## State, Persistence, And Dependencies
The framework stores the tree in `struct dtpm` parent/child lists and power values (`power_min`, `power_max`, `power_limit`, `weight`, flags). No nonvolatile state persists. Dependencies are the generic powercap framework, OF machine match data, DTPM backend ops, mutex/list helpers, and exported `linux/dtpm.h` contracts.

## Integration Points
DTPM backends are listed in `dtpm_subsys.h`; CPU and devfreq leaves call `dtpm_register()` and implement ops. Sysfs appears under the `dtpm` powercap control type. Virtual nodes must not have ops; leaves must have complete ops.

## Risks
`set_power_limit_uw()` does not take `dtpm_lock`, so external synchronization is not obvious despite comments saying the node lock must be held. `__set_power_limit_uw()` uses `table[i - 1]` style assumptions in backends and expects valid ranges. If a child limit update fails midway, already-updated siblings are not rolled back. `dtpm_create_hierarchy()` initializes subsystems after hierarchy creation, so backend setup callbacks run before backend init hooks. Destroy assumes `root` is valid when `pct` exists.

## Test Signals
Test single root enforcement, virtual and DT node hierarchy creation, backend setup failures, limit distribution at min/max/intermediate values, weight rebalance after hotplug power updates, failed child set operations, release denial for nodes with children, repeated create/destroy, and sysfs powercap operations.
