# subset-b-006189 Research

Grouped code research for the devlink generated netlink registration layer and devlink parameter, port, rate, region, resource, shared-buffer, and shared-devlink support. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/netlink_gen.c -->
# sources/distributed-fs/ceph-client/net/devlink/netlink_gen.c

## Purpose
This auto-generated YNL kernel source binds the devlink generic-netlink family to the command handlers implemented across `net/devlink/*.c`. It is generated from `Documentation/netlink/specs/devlink.yaml` and should not be edited directly. Its primary responsibilities are attribute policy declaration, sparse enum validation, and construction of the `devlink_nl_ops[75]` split-ops table consumed by the devlink family registration code.

## Important APIs, Types, And Functions
The file exports common nested policies used by hand-written handlers: `devlink_dl_port_function_nl_policy`, `devlink_dl_rate_tc_bws_nl_policy`, and `devlink_dl_selftest_id_nl_policy`. It defines per-command `nla_policy` arrays for get/set/new/delete/read/dump commands covering core devlink devices, ports, shared buffers, dpipe, resources, reload, params, regions, health reporters, flash update, traps, rates, linecards, selftests, and notification filters.

`devlink_attr_param_type_validate()` is the notable custom validator. It accepts only the sparse `DEVLINK_VAR_ATTR_TYPE_*` values used for reload-action statistics and rejects unknown enum values with an extended-ack message. `devlink_attr_index_range` gives `DEVLINK_ATTR_INDEX` full unsigned 32-bit range validation through `NLA_POLICY_FULL_RANGE`.

The central exported object is `const struct genl_split_ops devlink_nl_ops[75]`. Each entry maps a `DEVLINK_CMD_*` command to a policy, max attribute number, optional `pre_doit`/`post_doit`, a `doit` or `dumpit` handler, capability flags, and legacy validation suppression flags.

## Control Flow
At runtime, generic netlink dispatches an incoming devlink command through the table. For `doit` operations the selected pre-hook resolves and locks the target devlink object, and sometimes a port, before calling the implementation handler. Common hooks include `devlink_nl_pre_doit`, `devlink_nl_pre_doit_port`, `devlink_nl_pre_doit_port_optional`, and `devlink_nl_pre_doit_dev_lock`; post hooks unlock the same state. Dump operations generally call handler-specific dump functions and rely on `devlink_nl_dumpit()` for iteration across registered instances.

Administrative operations are marked with `GENL_ADMIN_PERM`; read-only get/dump paths usually have only `GENL_CMD_CAP_DO` or `GENL_CMD_CAP_DUMP`. Region read and some health dump paths use dump-specific validation flags because their request attributes are read from dump context rather than a normal `doit` request.

## State And Persistence
This file owns no mutable runtime state. Policies and the ops table are static const data. Persistence is indirect: whatever handler mutates device, port, param, region, resource, rate, or shared-buffer state does so after this layer validates and dispatches the request.

## Dependencies And Integration Points
The file includes netlink/genetlink headers, `netlink_gen.h`, and UAPI `linux/devlink.h`. It is built into devlink core by `net/devlink/Makefile` and references all handler symbols declared in `netlink_gen.h`. The generated policy constants are consumed by hand-written nested parsers in files such as `port.c` and `rate.c`.

## Risks And Edge Cases
The largest risk is spec drift. Because the file is generated, local edits would be overwritten and changes should be made in the YAML spec and regenerated. Handler declarations, policy max attributes, and `devlink_nl_ops` size must remain synchronized with `netlink_gen.h` and the UAPI enum values.

Several ops retain `GENL_DONT_VALIDATE_STRICT` or dump validation bypasses for compatibility. That is intentional for legacy devlink clients but means detailed semantic validation remains in handlers. Policy validation catches types and simple ranges only; cross-field requirements such as "region direct read cannot use a snapshot id" or "rate TC bandwidth must include every traffic class" are enforced later.

## Test Signals
Coverage for this file is mostly integration-level: successful registration of the devlink family and devlink selftests/scripts exercising commands through generic netlink. Local selftest references include hardware-driver tests for devlink port splitting, rate traffic-class bandwidth, and mlxsw resources. The best regression signal for this generated layer is that command dispatch reaches the expected `devlink_nl_*` handlers with the expected policy behavior after regenerating from the YAML spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/netlink_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/netlink_gen.h -->
# sources/distributed-fs/ceph-client/net/devlink/netlink_gen.h

## Purpose
This auto-generated YNL header is the declaration boundary between the generated devlink generic-netlink table in `netlink_gen.c` and the hand-written devlink implementation files. It declares exported nested policies, the split-ops table, pre/post dispatch hooks, and every `devlink_nl_*` command handler referenced by the generated ops table.

## Important APIs, Types, And Functions
The header exports three common nested policies: `devlink_dl_port_function_nl_policy`, `devlink_dl_rate_tc_bws_nl_policy`, and `devlink_dl_selftest_id_nl_policy`. It declares `extern const struct genl_split_ops devlink_nl_ops[75]`, which is the command table installed by the devlink family.

Pre/post hooks declared here are `devlink_nl_pre_doit()`, `devlink_nl_pre_doit_port()`, `devlink_nl_pre_doit_port_optional()`, `devlink_nl_pre_doit_dev_lock()`, `devlink_nl_post_doit()`, and `devlink_nl_post_doit_dev_lock()`. They are implemented outside this header and provide object lookup and lock management around command handlers.

The handler declarations span all devlink feature areas: device get/reload/info/flash/selftests/notify-filter, port get/set/new/del/split/unsplit and port params, shared buffers, eswitch, dpipe, resources, params, regions, health reporters, traps/groups/policers, rates, and linecards.

## Control Flow
The header has no runtime control flow. Its declarations allow `netlink_gen.c` to compile references to functions implemented in other translation units and allow `devl_internal.h` to include the generated interface. The actual flow is generic-netlink dispatch into `devlink_nl_ops`, then into these declared handlers.

## State And Persistence
No state is owned here. The only state-like declaration is the static ops table exported from `netlink_gen.c`; all mutable devlink state lives in `struct devlink`, `struct devlink_port`, xarrays, lists, and driver callbacks in the hand-written implementation.

## Dependencies And Integration Points
The file includes `<net/netlink.h>`, `<net/genetlink.h>`, and UAPI `<uapi/linux/devlink.h>`. It is included by `devl_internal.h`, which means most devlink core implementation files see the generated policies and handler prototypes through the internal header. It must stay synchronized with `netlink_gen.c` and the YAML netlink spec.

## Risks And Edge Cases
Because this header is generated, manual edits create a high maintenance risk and may be lost on regeneration. The fixed `devlink_nl_ops[75]` declaration must match the generated source exactly; a command-table size mismatch would be caught at compile time. Function prototype drift between hand-written handler implementations and this header is also compile-time visible.

## Test Signals
The test signal is compile/link coverage plus devlink generic-netlink command execution. If any handler prototype, exported policy, or table size diverges, the devlink object will fail to build. Runtime selftests that call devlink commands indirectly validate that the declarations match generated dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/netlink_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/param.c -->
# sources/distributed-fs/ceph-client/net/devlink/param.c

## Purpose
This file implements devlink configuration parameters. It lets drivers register typed parameters, exposes them over generic netlink, validates user updates, stores driver-init values that take effect on reload, and sends notifications when parameter definitions or values change.

## Important APIs, Types, And Functions
`devlink_param_generic[]` is the built-in catalog of generic parameter IDs, names, and types, including SR-IOV enablement, region snapshot control, firmware-load policy, enablement toggles for RoCE/RDMA/VNET/iWARP/ETH/PHC, queue sizes, clock ID, VF totals, doorbell counts, and max MACs per VF.

Lookup helpers operate on `struct devlink`'s `params` xarray: `devlink_param_find_by_name()`, `devlink_param_find_by_id()`, and `devlink_param_get_from_info()`. Validation is split between `devlink_param_generic_verify()`, `devlink_param_driver_verify()`, and `devlink_param_verify()`.

Netlink read paths are `devlink_nl_param_get_doit()` and `devlink_nl_param_get_dumpit()`. They use `devlink_nl_param_fill()` to emit the parameter name, generic flag, type, supported cmodes, current values, and optional defaults. `devlink_nl_param_value_put()` handles all supported scalar, string, and bool encodings.

Netlink write flow is handled by `devlink_nl_param_set_doit()` through `__devlink_nl_cmd_param_set_doit()`. It validates the supplied type, parses `DEVLINK_ATTR_PARAM_VALUE_DATA`, calls a driver `validate` callback when provided, checks the requested configuration mode, and either stores a pending driver-init value or calls the driver's runtime `set`/`reset_default` callback.

Exported registration and driver-facing APIs include `devl_params_register()`, `devlink_params_register()`, `devl_params_unregister()`, `devlink_params_unregister()`, `devl_param_driverinit_value_get()`, `devl_param_driverinit_value_set()`, `devlink_params_driverinit_load_new()`, and `devl_param_value_changed()`.

## Control Flow
Drivers register parameters under the devlink lock. Registration verifies IDs/names, checks that driver-init-only parameters do not provide runtime get/set callbacks, inserts a `struct devlink_param_item` into `devlink->params`, and emits a `DEVLINK_CMD_PARAM_NEW` notification. Multi-parameter registration rolls back already inserted items if a later insert fails.

Reads iterate supported cmodes. For `DRIVERINIT`, values are served from cached `driverinit_value_new`, `driverinit_value`, and `driverinit_default` fields. For runtime modes, the driver `get` callback is called and, if available, `get_default` supplies default values.

Writes are deliberately two-path. Runtime cmodes call the driver immediately. Driver-init cmode only updates `driverinit_value_new` and marks it valid; `devlink_params_driverinit_load_new()` later promotes pending values into active driver-init values during reload-oriented flows.

## State And Persistence
State lives in memory in `devlink->params` and per-parameter `struct devlink_param_item`. Driver-init state is cached as current value, default value, pending new value, and validity flags. This is not disk persistence; it survives only for the lifetime of the devlink instance and is intended to influence driver initialization/reload.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, the devlink lock, xarray storage, generic netlink helpers, `devlink_nl_notify_send()`, and driver-provided callbacks in `struct devlink_param`. It integrates with reload support through `devlink_reload_supported()` and with command dispatch through generated `DEVLINK_CMD_PARAM_*` handlers.

Port parameter handlers are stubs that return unsupported, so this tree exposes device-level parameters here but not per-port params.

## Risks And Edge Cases
Driver parameter definitions are checked with `WARN_ON()` but registration can continue after warnings; invalid driver tables should be treated as driver bugs. Runtime multi-attribute writes can partially affect external hardware only through one parameter value, but failures inside driver callbacks must leave driver state coherent.

String values are copied only if NUL-terminated and shorter than `__DEVLINK_PARAM_MAX_STRING_VALUE`. Bool values use flag encoding, with defaults encoded as `u8` so false can be distinguished from absence. Driver-init pending values are visible as the effective value before reload, which can surprise callers expecting hardware state rather than requested next-init state.

## Test Signals
Devlink parameter behavior is exercised indirectly by drivers in this repository that register generic params, such as `zl3073x` using `CLOCK_ID`, and by driver reload paths that call `devl_param_driverinit_value_get()`. Useful tests are netlink get/set/reset-default for every type, driver-init promotion across reload, duplicate name/ID registration, and notification replay on devlink registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/port.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/rate.c -->
# sources/distributed-fs/ceph-client/net/devlink/rate.c

## Purpose
This file implements devlink rate objects. Rate leaves are attached to devlink ports, while rate nodes are named hierarchy objects. The API exposes transmit share/max limits, priority, weight, parent-node assignment, and per-traffic-class bandwidth arrays through devlink netlink commands and driver callbacks.

## Important APIs, Types, And Functions
Object classification uses `devlink_rate_is_leaf()` and exported `devlink_rate_is_node()`. Lookup helpers resolve leaves from `DEVLINK_ATTR_PORT_INDEX` and nodes from `DEVLINK_ATTR_RATE_NODE_NAME`, rejecting empty or all-decimal node names.

Netlink output is built by `devlink_nl_rate_fill()`, which emits device handle, rate type, leaf port index or node name, tx share/max, priority, weight, optional parent name, and all `DEVLINK_RATE_TCS_MAX` traffic-class bandwidth values via `devlink_rate_put_tc_bws()`.

Command handlers are `devlink_nl_rate_get_doit()`, `devlink_nl_rate_get_dumpit()`, `devlink_nl_rate_set_doit()`, `devlink_nl_rate_new_doit()`, and `devlink_nl_rate_del_doit()`. Driver-facing creation/destruction APIs are `devl_rate_node_create()`, `devl_rate_leaf_create()`, `devl_rate_leaf_destroy()`, and `devl_rate_nodes_destroy()`. `devlink_rates_check()` lets other code reject teardown while rate nodes exist.

## Control Flow
Set operations first resolve the target object, check that every requested attribute has the corresponding leaf or node operation in `struct devlink_ops`, then apply fields one by one in `devlink_nl_rate_set()`. Each successful callback updates the cached devlink value. Parent changes call the relevant parent-set callback, prevent self-parenting and cycles, and maintain parent refcounts.

Creating a node requires driver support for both `rate_node_new` and `rate_node_del`. The code rejects duplicate valid names, allocates a node, calls the driver's create callback, applies any requested initial rate attributes, initializes the refcount, links the node into `devlink->rate_list`, and notifies userspace. Deleting a node requires `refcnt == 1`, which means no children currently reference it.

Traffic-class bandwidth updates parse every repeated `DEVLINK_ATTR_RATE_TC_BWS` nest, reject duplicate TC indexes, require all traffic classes to be specified, call the driver TC bandwidth setter, and then copy the full array into cached state.

## State And Persistence
Rate state is in memory on `devlink->rate_list` and on `devlink_port->devlink_rate`. Each object caches type, parent pointer, refcount, driver private pointer, name for nodes, and configured bandwidth/rate/priority/weight values. The file does not persist settings itself; driver callbacks may program hardware or persistent firmware policies.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, `struct devlink_ops` rate callbacks, generated nested TC bandwidth policy from `netlink_gen.c`, and the port lookup helpers from `port.c`. Drivers create leaves during port setup and may create nodes themselves or allow userspace-created nodes through `DEVLINK_CMD_RATE_NEW`.

## Risks And Edge Cases
Set operations are not transactional. If `tx_share` succeeds and `tx_max` fails, cached and hardware state retain the first change. Parent reassignment updates refcounts only after driver callbacks succeed, but failures inside driver callbacks must leave hardware topology unchanged.

`devl_rate_node_create()` increments the parent refcount before duplicating the node name; if name allocation fails, the parent refcount is not decremented in this implementation. That is a leak risk on the driver-created node path. The netlink-created path does not have that exact ordering.

`devl_rate_nodes_destroy()` assumes parent-set and delete callbacks are available and ignores callback errors during cleanup, which is common for teardown but means hardware cleanup failures are not reported to userspace.

## Test Signals
The local tree references `tools/testing/selftests/drivers/net/hw/devlink_rate_tc_bw.py`, which is directly relevant to the all-TC bandwidth parsing and validation path. Additional useful tests cover hierarchy cycle rejection, deleting a node with children, parent clear/reassign, leaf create/destroy under port lifecycle, and partial failure behavior of multi-attribute sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/rate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/region.c -->
# sources/distributed-fs/ceph-client/net/devlink/region.c

## Purpose
This file implements devlink regions: named address/data areas that drivers can expose for snapshots or direct reads. It supports device-level and port-level regions, snapshot ID allocation and reference tracking, snapshot create/delete notifications, region listing, and chunked region reads over netlink.

## Important APIs, Types, And Functions
`struct devlink_region` stores owning devlink, optional port, list linkage, ops or port ops, `snapshot_lock`, snapshot list, snapshot limits, current snapshot count, and region size. `struct devlink_snapshot` stores list linkage, region pointer, data pointer, and snapshot ID.

Lookup helpers are `devlink_region_get_by_name()`, `devlink_port_region_get_by_name()`, and `devlink_region_snapshot_get_by_id()`. Snapshot ID internals use `devlink->snapshot_ids` xarray through `__devlink_region_snapshot_id_get()`, `__devlink_snapshot_id_insert()`, `__devlink_snapshot_id_increment()`, and `__devlink_snapshot_id_decrement()`.

Netlink handlers are `devlink_nl_region_get_doit()`, `devlink_nl_region_get_dumpit()`, `devlink_nl_region_new_doit()`, `devlink_nl_region_del_doit()`, and `devlink_nl_region_read_dumpit()`. Driver APIs are `devl_region_create()`, `devlink_region_create()`, `devlink_port_region_create()`, `devl_region_destroy()`, `devlink_region_destroy()`, `devlink_region_snapshot_id_get()`, `devlink_region_snapshot_id_put()`, and `devlink_region_snapshot_create()`.

## Control Flow
Drivers create regions with a name, size, destructor, optional snapshot callback, and optional direct read callback. Creation links the region into either `devlink->region_list` or a port's `region_list` and sends a region-new notification.

Userspace can request an immediate snapshot with `DEVLINK_CMD_REGION_NEW`. The handler resolves the region, checks snapshot support and capacity, obtains a user-specified or allocated snapshot ID, calls the driver snapshot callback to allocate/fill data, and then stores a snapshot under `snapshot_lock`. If the ID was auto-allocated, the handler replies with the chosen ID.

Reads are dump operations. A read can target a stored snapshot or use direct read mode if no snapshot ID is supplied. Data is returned as nested chunks of up to `DEVLINK_REGION_READ_CHUNK_SIZE` bytes, and dump state tracks `start_offset` so multi-part netlink dumps continue from the last emitted offset.

Destroying a region takes the snapshot lock, deletes all snapshots using the registered destructor for each data buffer, removes the region from its list, sends a delete notification, and frees the region.

## State And Persistence
All state is in kernel memory. Region definitions live until driver teardown. Snapshot data persists only until explicitly deleted, region destruction, or devlink teardown. Snapshot IDs are globally tracked per devlink instance in an xarray with reference counts so the same ID can be shared by snapshots taken across multiple regions.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, devlink lock discipline, port lookup from `port.c`, xarray snapshot ID tracking, and driver-provided `devlink_region_ops` or `devlink_port_region_ops`. It integrates with drivers such as DSA switches and NICs that expose register tables or diagnostic dumps through devlink regions.

## Risks And Edge Cases
Port regions store ops in a union, but several paths use `region->ops` for common fields such as name and destructor. This relies on device and port region ops layouts being compatible for those members. Any layout divergence would be dangerous.

`devlink_nl_region_read_dumpit()` checks `region->ops->read` before selecting direct read, even for port regions where the actual callback is `port_ops->read`; this again relies on the unioned ops layout. Direct reads and snapshot reads are mutually exclusive and enforced at runtime.

Chunked reads guard against infinite loops by failing if no progress was made. Offset plus length arithmetic can conceptually overflow before clamping to region size if userspace supplies extreme values; practical netlink u64 handling should still be tested around boundaries.

## Test Signals
Driver-facing examples in this repository include DSA and NIC region setup/teardown and snapshot callbacks. Useful regression tests are snapshot create with explicit and auto IDs, duplicate IDs, max snapshot capacity, deleting shared IDs across multiple regions, direct read versus snapshot read validation, partial dump continuation, and port-region reads. Documentation references in `Documentation/networking/devlink/devlink-region.rst` describe expected userspace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/resource.c -->
# sources/distributed-fs/ceph-client/net/devlink/resource.c

## Purpose
This file implements devlink resources: hierarchical, driver-declared capacity objects with sizes, pending new sizes, validation constraints, optional occupancy callbacks, and device or port scope. Userspace can inspect resource trees and request new sizes, while drivers later consume pending sizes during reload or reconfiguration.

## Important APIs, Types, And Functions
`struct devlink_resource` contains name, ID, committed size, pending `size_new`, subtree validity, parent pointer, size constraints, child list, occupancy callback, and callback private data.

Recursive lookup uses `__devlink_resource_find()` and `devlink_resource_find()`. Size validity helpers are `devlink_resource_validate_size()` for min/max/granularity checks and `devlink_resource_validate_children()` for ensuring child pending sizes do not exceed parent pending size.

Netlink handlers are `devlink_nl_resource_set_doit()`, `devlink_nl_resource_dump_doit()`, and `devlink_nl_resource_dump_dumpit()`. Serialization is recursive through `devlink_resource_put()`, emitting name, size, ID, pending size when different, occupancy, size params, child list, and `DEVLINK_ATTR_RESOURCE_SIZE_VALID` for resources with children.

Driver APIs include `devl_resource_register()`, `devl_resources_unregister()`, `devlink_resources_unregister()`, `devl_resource_size_get()`, `devl_resource_occ_get_register()`, `devl_resource_occ_get_unregister()`, `devl_port_resource_register()`, and `devl_port_resources_unregister()`.

## Control Flow
Drivers register top-level resources or children under an existing parent ID while holding the devlink lock. Registration rejects duplicate IDs in the selected tree, verifies parents for non-top resources, initializes current and pending sizes to the same value, copies sizing params, and links the resource into the proper list.

Userspace size changes resolve a resource by ID, validate the requested size against min/max/granularity, update `size_new`, then recompute the child-sum validity flag for the resource and its parent. The actual committed size changes when a driver calls `devl_resource_size_get()`, which returns `size_new` and updates `size`.

Dump paths support both single request/reply style and generic netlink dump iteration. They can emit device resources, port resources, or both, controlled by optional `DEVLINK_ATTR_RESOURCE_SCOPE_MASK`. Dump state tracks the current resource index and port index across callbacks.

## State And Persistence
Resource state is in memory in `devlink->resource_list` and each `devlink_port->resource_list`. `size_new` persists as pending runtime state until a driver consumes it or resources are unregistered. Occupancy is not stored; it is sampled by calling the registered callback during dump.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, devlink lock discipline, port resources initialized by `devlink_port_init()`, generic netlink helpers, and driver-provided occupancy callbacks. Drivers use resource size getters during reload or reinitialization to apply pending allocations. DSA and NIC drivers in this tree register resources for VLAN/FDB/ATU/SF counts and similar capacities.

## Risks And Edge Cases
Only the changed resource and its immediate parent are revalidated on set. Because a parent's validity can affect higher ancestors, deeply nested trees may leave ancestor `size_valid` stale if grandchildren are resized in ways that change aggregate validity beyond one level.

`devlink_resource_fill()` assumes the selected resource list is non-empty before taking `list_first_entry()`, and callers enforce that for normal dump-doit. Any future caller must preserve that precondition.

`devlink_resource_validate_size()` divides by `size_granularity`; invalid zero granularity in driver-provided params would be a serious driver bug. Occupancy callbacks run during dump and should be fast and safe under devlink locking expectations.

## Test Signals
Relevant local selftests include mlxsw devlink resource scripts under `tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh`. Useful tests cover size min/max/granularity failures, pending size reporting, parent/child aggregate validity, scoped dump selection for device versus port resources, occupancy callback registration/unregistration, and driver reload consumption via `devl_resource_size_get()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/sb.c -->
# sources/distributed-fs/ceph-client/net/devlink/sb.c

## Purpose
This file implements devlink shared-buffer support. Shared buffers describe packet buffer pools and traffic-class bindings, expose pool and per-port thresholds, allow userspace to trigger occupancy snapshots or clear maxima, and delegate all hardware reads/writes to driver callbacks.

## Important APIs, Types, And Functions
`struct devlink_sb` stores list linkage, shared-buffer index, total size, ingress/egress pool counts, and ingress/egress traffic-class counts. Lookup and validation helpers include `devlink_sb_get_by_index()`, `devlink_sb_get_from_attrs()`, `devlink_sb_pool_index_get_from_attrs()`, `devlink_sb_pool_type_get_from_attrs()`, `devlink_sb_th_type_get_from_attrs()`, and `devlink_sb_tc_index_get_from_attrs()`.

Command handlers cover shared-buffer metadata (`devlink_nl_sb_get_doit()`, dump), pools (`devlink_nl_sb_pool_get_doit()`, dump, `devlink_nl_sb_pool_set_doit()`), port-pool thresholds (`devlink_nl_sb_port_pool_get_doit()`, dump, set), traffic-class pool bindings (`devlink_nl_sb_tc_pool_bind_get_doit()`, dump, set), occupancy snapshot (`devlink_nl_sb_occ_snapshot_doit()`), and max clear (`devlink_nl_sb_occ_max_clear_doit()`).

Driver-facing lifecycle APIs are `devl_sb_register()`, `devlink_sb_register()`, `devl_sb_unregister()`, and `devlink_sb_unregister()`.

## Control Flow
Drivers register each shared buffer with static counts and size. Get/dump commands enumerate registered SBs and call driver callbacks to fetch pool, port-pool, and TC binding state. Set commands validate indexes/types/required attributes, then call the corresponding driver setter.

Pool dumps iterate each registered shared buffer and every pool index. Port-pool dumps iterate every registered port for every pool. TC binding dumps iterate every port, all ingress TCs, and all egress TCs. Dump state uses a flat index so generic netlink can resume after message-size limits.

Occupancy information is optional. If `sb_occ_port_pool_get` or `sb_occ_tc_port_bind_get` exists, fill paths append current and max occupancy values unless the callback returns `-EOPNOTSUPP`. Snapshot and max-clear commands directly call `sb_occ_snapshot` and `sb_occ_max_clear` when provided.

## State And Persistence
The file stores only SB descriptors in `devlink->sb_list`. Pool sizes, thresholds, bindings, and occupancy values are owned by hardware/driver state and retrieved or changed through callbacks. No persistent storage is written here; persistence depends on device firmware/driver behavior.

## Dependencies And Integration Points
The implementation depends on `devl_internal.h`, devlink port iteration, generic netlink helpers, and a broad set of `struct devlink_ops` shared-buffer callbacks. Drivers such as Ocelot/Felix and NFP in this repository provide concrete shared-buffer behavior.

## Risks And Edge Cases
The set paths validate index ranges against registered counts but do not enforce semantic consistency between pool type and pool index beyond what drivers do. A pool index spans ingress and egress pool counts as a flat range, while TC validation uses the supplied pool type.

In `devlink_nl_sb_tc_pool_bind_fill()`, an occupancy callback error other than `-EOPNOTSUPP` returns immediately without cancelling the in-progress generic-netlink message. That differs from the nearby port-pool fill path and is worth focused review because it can leave partially built skb state on error.

Dump loops can become large because they multiply SBs, ports, pools, and TCs. Correct flat-index resume behavior is important for devices with many ports or traffic classes.

## Test Signals
Driver-specific tests and reports for Ocelot/Felix and NFP shared buffers are relevant integration signals. Useful tests cover invalid SB/pool/TC indexes, pool get/set, port-pool thresholds, ingress and egress TC binding, optional occupancy unsupported paths, occupancy snapshot/max clear, and multi-part dumps on devices with enough ports/pools to exceed one skb.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/sb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/sh_dev.c -->
# sources/distributed-fs/ceph-client/net/devlink/sh_dev.c

## Purpose
This file implements shared devlink instances keyed by a string identifier such as a serial number. It lets multiple callers obtain the same devlink object and shared driver-private storage when they represent the same underlying device, while enforcing that all callers agree on ops, private size, and driver identity.

## Important APIs, Types, And Functions
`struct devlink_shd` is embedded in the devlink private area. It stores a global-list node, duplicated identifier string, reference count, private data size, and aligned flexible private-data bytes.

Internal helpers are `devlink_shd_lookup()`, `devlink_shd_create()`, and `devlink_shd_destroy()`. Exported APIs are `devlink_shd_get()`, `devlink_shd_put()`, and `devlink_shd_get_priv()`.

## Control Flow
`devlink_shd_get()` takes the global `shd_mutex`, looks for an existing shared object by ID, and creates one if absent. Creation allocates a devlink with `__devlink_alloc()` in `init_net`, duplicates the ID, sets refcount and private size, registers the devlink under the devlink lock, and adds it to the global list.

If an existing ID is found, `devlink_shd_get()` verifies that `ops`, `priv_size`, and `driver` match the existing devlink. A mismatch triggers `WARN_ON_ONCE()` and returns `NULL`. Otherwise it increments the shared refcount and returns the owning `struct devlink`.

`devlink_shd_put()` takes the same mutex, decrements the refcount, and destroys the shared devlink when the count reaches zero. Destruction removes it from the list, unregisters the devlink, frees the duplicated ID, and frees the devlink object. `devlink_shd_get_priv()` returns the private payload after the `struct devlink_shd` header.

## State And Persistence
Shared state is process-kernel memory only: the global `shd_list`, each shared devlink instance, the ID string, refcount, and private payload. There is no persistence across module unload or reboot. The shared devlink is registered while the first reference exists and unregistered when the last reference is put.

## Dependencies And Integration Points
The file depends on `net/devlink.h`, `devl_internal.h`, `__devlink_alloc()`, `devlink_priv()`, `priv_to_devlink()`, `devl_register()`, `devl_unregister()`, and `devlink_free()`. Drivers such as mlx5 shared-device support use this API to group physical functions by serial/VPD-derived identity.

## Risks And Edge Cases
All global-list and refcount manipulation is serialized by `shd_mutex`, so lookup/create/put are straightforward. The main risk is caller discipline: every successful `devlink_shd_get()` must be paired with `devlink_shd_put()`, and all callers for a given ID must pass identical ops, private size, and driver pointer.

`devlink_shd_create()` does not check the return value of `devl_register()`. In current devlink internals this may be expected to be void, but if registration semantics change this path would need revisiting. The API uses `init_net` and a `NULL` device, so consumers should be aware that the shared instance is not tied to an individual device object.

## Test Signals
Useful tests are paired get/put creating and destroying exactly one shared instance, repeated get with matching metadata increasing the refcount, mismatched metadata returning `NULL`, private pointer alignment and isolation, and driver unload paths that must release all references. Existing mlx5 shared-devlink usage in this tree is the main integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/devlink/sh_dev.c -->
