
# sources/distributed-fs/ceph-client/net/devlink/port.c

## Purpose
This file implements devlink port registration, discovery, mutation, notification, netdevice association, physical-port naming, switch-id compatibility, split/unsplit operations, dynamic port creation/deletion, and port-function attributes. It is the core glue between driver-owned port objects and user-visible devlink port netlink commands.

## Important APIs, Types, And Functions
Port lookup helpers are `devlink_port_get_by_index()`, `devlink_port_get_from_attrs()`, and `devlink_port_get_from_info()`. Netlink serialization uses `devlink_nl_port_handle_fill()`, `devlink_nl_port_handle_size()`, `devlink_nl_port_attrs_put()`, `devlink_nl_port_function_attrs_put()`, and `devlink_nl_port_fill()`.

Function attributes cover hardware address, administrative state and operational state, capabilities, max IO event queues, and peer devlink handles. Capability support includes RoCE, migratable, IPsec crypto, and IPsec packet toggles, with VF-only checks for several capabilities. Setters flow through `devlink_port_function_set()` after nested policy parsing and operation validation.

Command handlers include `devlink_nl_port_get_doit()`, `devlink_nl_port_get_dumpit()`, `devlink_nl_port_set_doit()`, `devlink_nl_port_split_doit()`, `devlink_nl_port_unsplit_doit()`, `devlink_nl_port_new_doit()`, and `devlink_nl_port_del_doit()`.

Driver-facing APIs include `devlink_port_init()`, `devlink_port_fini()`, `devl_port_register_with_ops()`, `devlink_port_register_with_ops()`, `devl_port_unregister()`, `devlink_port_unregister()`, `devlink_port_type_eth_set()`, `devlink_port_type_ib_set()`, `devlink_port_type_clear()`, `devlink_port_attrs_set()`, PCI PF/VF/SF attribute helpers, `devl_port_fn_devlink_set()`, and `devlink_port_linecard_set()`.

## Control Flow
A driver initializes or embeds a `struct devlink_port`, optionally sets immutable attributes, then registers it into `devlink->ports` under the devlink lock. Registration initializes type locking and reporter lists, schedules a delayed warning if the type remains unset for normal port flavours, inserts the port in the xarray, and sends `DEVLINK_CMD_PORT_NEW`.

Get and dump paths serialize the current type under `type_lock`, then append static attrs, function attrs obtained from driver callbacks, optional nested peer devlink handles, and linecard linkage. Set paths may change the desired port type through `port_type_set`, and may update function attributes. Function state is intentionally applied last so MAC/capability/max-queue changes can land before activation.

Netdevice notifier integration updates devlink port type and netdev references on `NETDEV_POST_INIT`, `REGISTER`, `CHANGENAME`, `UNREGISTER`, and `PRE_UNINIT`. For net namespace moves, the type can remain while the netdev pointer is cleared or reattached only when it belongs to the same devlink net namespace.

## State And Persistence
State is in memory in `struct devlink_port` and `devlink->ports`: index, registration flag, type/desired type, type-specific netdev or IB device references, attrs, function relationship index, linecard pointer, reporter list, resource/region lists, and delayed work. No state is persisted to disk by this file; hardware changes are delegated to driver ops and may have driver-specific persistence.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, xarray, netdevice notifier semantics, RTNL assertions for netdev name/index capture, RDMA `ib_device` names, and nested devlink relationship helpers. Drivers integrate by providing `struct devlink_port_ops` callbacks for type setting, splitting, function attributes, dynamic port creation/deletion, and optional peer devlink linkage.

## Risks And Edge Cases
Function attribute updates are sequential and not rolled back as a transaction. A request setting multiple capabilities can partially apply if a later driver callback fails. `devlink_nl_port_new_doit()` delegates object creation to the driver, then attempts to reply; on reply failure it calls the port delete callback, so driver `port_new`/`port_del` must tolerate that cleanup path.

The delayed warning is a quality signal for drivers that register ports without setting type, but it depends on correct cancellation during unregister or type set. Attribute helpers require being called before registration; violating that is detected with warnings rather than hard recovery.

Physical-port name generation is fixed by flavour and attrs. Buffer exhaustion returns `-EINVAL`, and CPU/DSA/unused flavours warn if asked for a name because they should not have associated netdevices.

## Test Signals
Relevant tests include devlink port split selftests under `tools/testing/selftests/drivers/net/hw/devlink_port_split.py`, plus driver-specific coverage for PCI SF/VF function attributes in mlx5/ice reports elsewhere in this tree. Strong regression cases are port registration/unregistration ordering, netdev rename/netns transitions, split-count validation, multi-attribute function set failure, and dynamic SF port add/delete.
