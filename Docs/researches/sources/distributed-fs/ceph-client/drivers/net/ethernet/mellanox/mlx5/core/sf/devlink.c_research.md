# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/devlink.c

## Purpose

`sf/devlink.c` implements devlink PCI SF port management for mlx5. It creates and deletes SF devlink ports, maps user SF numbers to hardware function IDs, activates/deactivates SF HCAs through devlink port function state, updates operational state from VHCA events, and cleans up SFs when eswitch mode changes.

## Important APIs, Types, and Functions

`struct mlx5_sf` is the per-devlink-port object: it embeds `struct mlx5_devlink_port`, stores devlink port index, controller, software table id, hardware function id, and cached VHCA state. `struct mlx5_sf_table` holds the parent device, xarray lookup by hardware function id, and `sf_state_lock`.

Public devlink operations are `mlx5_devlink_sf_port_new()`, `mlx5_devlink_sf_port_del()`, `mlx5_devlink_sf_port_fn_state_get()`, and `mlx5_devlink_sf_port_fn_state_set()`. Lifecycle functions are `mlx5_sf_notifiers_init()`, `mlx5_sf_table_init()`, `mlx5_sf_notifiers_cleanup()`, `mlx5_sf_table_cleanup()`, and `mlx5_sf_table_empty()`.

## Control Flow

New-port validation requires `DEVLINK_PORT_FLAVOUR_PCI_SF`, no user-selected port index, a valid user `sfnum`, valid controller support, correct PF number, SF hardware table support, and switchdev eswitch mode. Allocation uses `mlx5_sf_hw_table_sf_alloc()` to reserve a software id and firmware function, converts it to a hardware function id, derives a devlink port index, inserts the object into the xarray, and loads the eswitch SF vport. Delete unloads the eswitch vport and deallocates the SF.

Function state set is serialized by `sf_state_lock`. ACTIVE enables the SF HCA, optionally sets default max IO EQs on the devlink port, and moves cached state to ACTIVE. INACTIVE disables the HCA and changes cached state to TEARDOWN_REQUEST. VHCA events update cached state only for valid transitions: ACTIVE<->IN_USE and TEARDOWN_REQUEST->ALLOCATED. Deallocation frees immediately if the hardware state is still ALLOCATED; otherwise it requests disable if needed and calls deferred hardware-table free so the function id is recycled only after firmware reports ALLOCATED.

The file registers notifiers for eswitch mode changes, VHCA events, and parent mdev peer-devlink events. Legacy eswitch mode deletes all SF ports. Peer-devlink events attach the child SF devlink to the parent devlink port.

## State and Persistence Behavior

Driver state is `dev->priv.sf_table`, the xarray by function id, each `mlx5_sf` object, vport `max_eqs_set`, and cached hardware state. Firmware state includes allocated SF function IDs, HCA enable/disable, VHCA state, and eswitch vports. Devlink state includes PCI SF ports, function state/opstate, and child peer devlink linkage.

## Dependencies and Integration Points

Dependencies include devlink port APIs, mlx5 eswitch load/unload, SF hardware table APIs, VHCA event APIs, SF command wrappers, max IO EQ devlink helpers, notifier chains, and SF tracepoints. It is the main user-facing integration point for `devlink port add/del` and `devlink port function set state`.

## Risks and Edge Cases

State transitions are asynchronous and split between user commands and firmware events; missing or delayed VHCA events leave entries pending deferred free. Deleting an ACTIVE SF treats it as possibly IN_USE and always waits for firmware confirmation before recycling the id. On eswitch legacy transition, `mlx5_sf_del_all()` iterates the xarray while deleting entries, which relies on xarray iteration semantics and deletion safety. Peer devlink notifier returns `NOTIFY_DONE` when no SF is found, so child probe can proceed without peer linkage if ordering is wrong.

## Test Signals

Run devlink SF add/delete with duplicate `sfnum`, invalid controller, invalid PF, and non-switchdev mode. Test ACTIVE, INACTIVE, IN_USE, and teardown transitions with child driver attached. Verify deferred free after child detach, eswitch legacy cleanup, peer devlink association, max IO EQ default programming, and tracepoints for add/free/activate/deactivate/update.
