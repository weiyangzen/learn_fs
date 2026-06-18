# Research: subset-b-004558

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/resources.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/resources.h

## Purpose

`resources.h` defines the mlxsw resource catalog used by the Spectrum driver family to translate firmware-reported resource IDs into driver-visible capacity values. It is a compact state container and accessor layer for quantities such as KVD sizes, trap groups, counter pools, SPAN agents, FIDs, LAG limits, buffer dimensions, ACL TCAM and action limits, policers, virtual routers, RIFs, multicast eRIF list entries, and NVE multicast entries.

The header also carries three software-only resource IDs for computed KVD partition sizes: `KVD_SINGLE_SIZE`, `KVD_DOUBLE_SIZE`, and `KVD_LINEAR_SIZE`. These are not parsed from firmware; they are set internally by profile/resource registration code.

## Important APIs, Types, and Functions

`enum mlxsw_res_id` is the stable driver-side index namespace. `mlxsw_res_ids[]` maps queried hardware resource IDs, such as `0x1001` for `KVD_SIZE` and `0x2902` for `ACL_MAX_TCAM_RULES`, to the enum indexes.

`struct mlxsw_res` stores two parallel arrays, `valid[]` and `values[]`, indexed by `enum mlxsw_res_id`. The inline API is:

- `mlxsw_res_valid()` / `MLXSW_RES_VALID()` to test whether a resource was supplied or set.
- `mlxsw_res_get()` / `MLXSW_RES_GET()` to fetch a resource value, warning and returning zero when the value is not valid.
- `mlxsw_res_set()` / `MLXSW_RES_SET()` to mark a value valid and store it.
- `mlxsw_res_parse()` to consume a raw firmware ID/value pair and update the matching enum slot if the raw ID is known.

## Control Flow

Resource discovery code elsewhere queries firmware and calls `mlxsw_res_parse()` for each returned `(id, value)` pair. The parser linearly scans `mlxsw_res_ids[]`; on match it calls `mlxsw_res_set()` and returns. Unknown firmware IDs are ignored, which lets newer firmware expose resources older driver code does not understand.

Driver code later gates feature setup with `MLXSW_CORE_RES_VALID()` / `MLXSW_RES_VALID()` and reads limits with `MLXSW_CORE_RES_GET()` / `MLXSW_RES_GET()`. Spectrum resource registration in `spectrum.c`, KVDL setup in `spectrum1_kvdl.c` and `spectrum2_kvdl.c`, ACL setup, policers, counters, trap groups, RIFs, and port-range registers all rely on these values.

## State and Persistence Behavior

`struct mlxsw_res` is in-memory driver state populated during device bring-up. It persists for the life of the mlxsw core instance and is not a disk-backed configuration. Validity is explicit per resource; callers must not assume every enum entry is available on every ASIC or firmware version.

Because this is a header with `static` objects and inline functions, each translation unit gets its own private copy of `mlxsw_res_ids[]`. The array is read-only by convention, although it is not declared `const`.

## Dependencies and Integration Points

The header depends only on Linux kernel/types basics, but it is integrated through `core.h` and used broadly by Spectrum files. Resource IDs feed devlink resource registration, config profile sizing, ACL TCAM limits, KVDL allocator partition sizing, CPU policer/trap group programming, LAG limits, RIF capacities, and NVE capacities.

## Risks and Edge Cases

- `mlxsw_res_get()` warns on invalid resources but still returns zero. A caller that treats zero as a real capacity can silently disable or under-size a feature after a missing resource.
- `mlxsw_res_valid()`, `mlxsw_res_get()`, and `mlxsw_res_set()` do not bounds-check `res_id`; callers must pass only valid enum values.
- Unknown raw firmware IDs are ignored without logging, so resource discovery regressions require external tracing or later feature failures to notice.
- Software-only resources are intentionally absent from `mlxsw_res_ids[]`; they must be set by driver profile code, not expected from firmware.
- The non-`const` `mlxsw_res_ids[]` in a header creates a mutable per-translation-unit copy. Accidental writes would affect only one object file and be hard to diagnose.

## Test Signals

Useful validation includes booting Spectrum variants with resource query tracing, checking that required resources are valid before KVDL/ACL/router/trap initialization, and comparing `devlink resource show` output against firmware-reported KVD, counter, SPAN, policer, RIF, and port-range capacities. Static analysis should flag unchecked `MLXSW_RES_GET()` paths for resources that can be absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/resources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.c

## Purpose

`spectrum.c` is the main Mellanox/NVIDIA Spectrum Ethernet switch driver body. It binds Spectrum-1 through Spectrum-4 PCI/core drivers, selects generation-specific operation tables, initializes shared switch subsystems, creates and removes netdev ports, handles port split/unsplit, transmits and receives CPU-port packets, manages VLAN membership and PVID state, programs traps and CPU policers, registers devlink resources, tracks sampling triggers and shared IPv6 KVDL addresses, and reacts to Linux netdevice topology events for bridge, VLAN, LAG, OVS, macvlan, l3mdev, and VxLAN integration.

The file is the orchestration layer for many specialized modules. It does not implement every subsystem itself, but it owns the ordering and rollback between KVDL, PGT, LAG, FID, policer, trap, buffer, SPAN, switchdev, counter, ACL action, NVE, ACL, router, PTP, dpipe, port mapping, and netdev registration.

## Important APIs, Types, and Functions

Driver registration objects include `mlxsw_sp1_driver`, `mlxsw_sp2_driver`, `mlxsw_sp3_driver`, `mlxsw_sp4_driver`, matching PCI ID tables, firmware revision/filename declarations, config profiles, and `mlxsw_sp_module_init()` / `mlxsw_sp_module_exit()`.

Device lifecycle entry points are `mlxsw_sp1_init()`, `mlxsw_sp2_init()`, `mlxsw_sp3_init()`, `mlxsw_sp4_init()`, the common `mlxsw_sp_init()`, and `mlxsw_sp_fini()`. The generation-specific init functions populate operation pointers in `struct mlxsw_sp`, such as switchdev, KVDL, ACL key/action, ACL TCAM, multicast routing TCAM, NVE, shared-buffer, port-speed, PTP, SPAN, policer, trap, matchall, router, and FID core ops.

Port and netdev APIs include `mlxsw_sp_port_create()`, `mlxsw_sp_port_remove()`, `mlxsw_sp_ports_create()`, `mlxsw_sp_ports_remove()`, `mlxsw_sp_port_open()`, `mlxsw_sp_port_stop()`, `mlxsw_sp_port_xmit()`, `mlxsw_sp_port_change_mtu()`, `mlxsw_sp_port_set_mac_address()`, `mlxsw_sp_port_vlan_create()`, `mlxsw_sp_port_vlan_destroy()`, `mlxsw_sp_port_vlan_set()`, `mlxsw_sp_port_pvid_set()`, `mlxsw_sp_port_admin_status_set()`, and port split/unsplit helpers.

Networking integration is exposed through `mlxsw_sp_port_netdev_ops`, `mlxsw_sp_netdevice_event()`, `mlxsw_sp_port_dev_check()`, `mlxsw_sp_port_dev_lower_find()`, `mlxsw_sp_lower_get()`, parsing controls `mlxsw_sp_parsing_depth_inc()`, `mlxsw_sp_parsing_depth_dec()`, and `mlxsw_sp_parsing_vxlan_udp_dport_set()`.

State-sharing helpers include flow counter allocation/query/free, sampling trigger parameter set/unset/lookup, IPv6 address KVDL index get/put, trap initialization, LAG setup and membership transitions, and devlink resource registration.

## Control Flow

Module load registers four mlxsw core drivers, then their PCI drivers. On a device match, the generation-specific init function fills `struct mlxsw_sp` with the proper ops table and calls `mlxsw_sp_init()`.

Common initialization starts by storing core and bus pointers, initializing parsing state, and reading the base MAC. It then initializes KVDL, PGT, LAG, FID core, policers, traps, devlink traps, buffers, SPAN, switchdev, counter pool, ACL flexible actions, the IPv6-address hash table, NVE, port-range registers, ACL, router, optional PTP clock/state, netdevice notifier, dpipe, port module information, sampling trigger hash table, and finally ports. Each failure path unwinds in reverse order.

Port creation maps a module/lane set to a local port, assigns the Ethernet SWID, obtains port label information, initializes the core port and netdev, allocates per-CPU stats, sets MAC, features, MTU limits, TX headroom, system-port mapping, advertised speeds, maximum speed, admin-down state, buffers, ETS, multicast TC mode, DCB, FIDs, qdiscs, VLAN filters, NVE, default PVID, default VID 4095 VLAN, VLAN classification, PTP shaper work, overheat baseline, and finally registers the netdev and starts periodic stats work. Removal cancels work, unregisters the netdev, clears PTP configuration, flushes VLANs, and unwinds the same hardware state.

Transmit flow checks core queue availability, pads the skb, handles special PTP timestamp-as-data requirements, possibly inserts the default VLAN tag, transmits via `mlxsw_core_skb_transmit()`, and updates per-CPU TX counters. RX listeners attach the skb to the correct netdev, set forwarding marks for marked trap paths, update per-CPU RX counters, and pass traffic to GRO.

Netdevice notifier flow validates topology before linking uppers, applies bridge/LAG/OVS/VLAN/macvlan/VxLAN state on `NETDEV_CHANGEUPPER`, handles LAG lower-state distribution/collector changes, invalidates SPAN entries on unregister, and respins SPAN on every event. The VxLAN paths enforce bridge constraints and join/leave NVE offload on VxLAN device up/down or bridge membership changes.

## State and Persistence Behavior

Persistent in-kernel state lives in `struct mlxsw_sp`: port pointers, base MAC, MAC mask, LAG table, port mapping array and pending mapping events, sample-trigger rhashtable, subsystem handles, operation tables, parsing state, IPv6 address rhashtable, PGT flags, and LAG PGT base. Each `struct mlxsw_sp_port` stores netdev identity, per-CPU stats, DCB and link state, port mapping, delayed stats work, VLAN list/default VLAN, flow blocks, PTP port state, maximum speed, headroom, and module overheat baseline.

Hardware state is programmed through many registers: port admin, MAC, MTU, SWID, VLAN membership/PVID/classification/learning, STP, module lane mapping, system-port mapping, speed capabilities, ETS/shapers, trap groups, CPU policers, LAG hashing/membership, PGT base, parsing depth/VxLAN UDP port, flow counters, IPv6 address KVDL entries, and PTP timestamp forwarding. None of this is persisted across driver reload; it is rebuilt from firmware resources, devlink profile settings, current netdev topology, and kernel configuration.

Reference-counted state includes sampling trigger nodes, IPv6 KVDL address nodes, parsing-depth users, and LAG objects. Delayed work is used for periodic hardware stats and PTP shaper updates. Port mapping events are queued under a spinlock and processed in workqueue context.

## Dependencies and Integration Points

The file integrates with the mlxsw core, PCI bus glue, firmware/resource/profile infrastructure, devlink, Linux netdev, switchdev, bridge/VLAN/LAG/VxLAN APIs, traffic control offload APIs, PTP, psample, rhashtable, and all Spectrum subsystem files declared in `spectrum.h`. It calls register pack/query/write helpers from `reg.h`, CPU-port TX header helpers, environment/module helpers from `core_env`, and generation-specific ops from Spectrum-1/2/3/4 modules.

## Risks and Edge Cases

- Initialization ordering is fragile: moving KVDL, PGT, LAG, SPAN, switchdev, ACL, router, or notifier setup can break assumptions called out in comments.
- Several cleanup paths call hardware writes and ignore failures during teardown. That is typical for driver unwinding but can hide partially stale device state after error injection.
- `mlxsw_sp_port_lag_join()` returns immediately when no free LAG member index is found without dropping the reference acquired by `mlxsw_sp_lag_get()`, which is a leak-prone path worth checking against surrounding kernel history.
- PTP timestamp-as-data TX mutates skbs by adding VLAN tags; regressions here can affect checksum/headroom assumptions and default VID behavior.
- `mlxsw_sp_port_ovs_leave()` and related VLAN loops use unsigned `u16` decrement patterns that rely on break conditions; changes need care to avoid wraparound loops.
- Netdevice event replay and validation paths are complex and recursive over uppers. Missing a replay after de-enslavement can leave bridge/router/FID state inconsistent.
- Parsing-depth refcounting writes hardware only on first increment and final decrement. Leaked references keep the increased parsing depth indefinitely; premature decrement can disturb VXLAN/NVE users.
- Resource registration assumes core resource validity. Older firmware or partial resource discovery failures tend to surface as `-EIO` during feature initialization.

## Test Signals

High-value tests include Spectrum module load/unload for all supported PCI IDs, port creation/removal with module mapping events, devlink resource display and size override tests, port split/unsplit, netdev open/close, PTP TX/RX timestamping, VLAN add/kill, bridge join/leave with VLAN-aware and VLAN-unaware modes, LAG create/join/leave/lower-state changes, OVS master join/leave, VxLAN bridge join/up/down validation, TC flower/matchall/qdisc offload toggles, parsing-depth users, sampling trigger reference sharing, IPv6 NVE address KVDL refcounts, and fault injection across each init label to verify reverse unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.h

## Purpose

`spectrum.h` is the central public-private header for the Spectrum switch driver. It defines the core `struct mlxsw_sp` and `struct mlxsw_sp_port` state containers, resource names and IDs, shared constants, operation tables, inline helpers, enums, and cross-file prototypes used by the Spectrum Ethernet, switchdev, router, ACL, KVDL, multicast routing, NVE, traps, buffers, PGT, policer, qdisc, ethtool, PTP, and port-range modules.

The header is the integration contract between generation-neutral code in `spectrum.c` and generation-specific Spectrum-1/2/3/4 implementations.

## Important APIs, Types, and Functions

Important constants include `MLXSW_SP_DEFAULT_VID`, FID/MID limits, KVD linear size/granularity, and devlink resource names. `enum mlxsw_sp_resource_id` extends core resource IDs with Spectrum-specific devlink resources for KVD partitions, SPAN, counters, policers, RIF MAC profiles, RIFs, and port-range registers.

`struct mlxsw_sp` is the switch instance root. It stores port arrays, core/bus pointers, base MAC, LAGs, port mapping state, sample trigger hash table, subsystem pointers, generation-specific operation tables, parsing state, IPv6 address table, PGT state, and LAG PGT base.

`struct mlxsw_sp_port` is the per-front-panel-port state. It binds a netdev to a local port, per-CPU software stats, link/DCB settings, module/lane mapping, delayed hardware stats, VLAN list/default VLAN, qdisc/flow blocks, PTP port state, max speed, headroom, and overheat baseline.

Major operation tables include `mlxsw_sp_ptp_ops`, `mlxsw_sp_fid_core_ops`, `mlxsw_sp_port_type_speed_ops`, `mlxsw_sp_kvdl_ops`, `mlxsw_sp_acl_rulei_ops`, `mlxsw_sp_acl_tcam_ops`, `mlxsw_sp_mall_ops`, and `mlxsw_sp_mr_tcam_ops`. These allow `spectrum.c` and shared modules to call generation-specific backends.

The header also declares cross-module APIs for buffers, switchdev, router, KVDL, ACL rule/action handling, TC flow blocks, matchall/flower/qdisc offloads, FIDs, multicast routing TCAM, NVE, traps, ethtool, policers, PGT, parsing controls, sampling triggers, IPv6 address KVDL sharing, and port-range registers.

## Control Flow

The typical flow starts in a generation-specific init function in `spectrum.c`, which fills the operation pointers declared here. The common initialization then calls subsystem init functions declared here in a fixed order. Port creation uses `struct mlxsw_sp_port`, buffer/FID/qdisc/NVE prototypes, PVID/VLAN helpers, DCB stubs or real DCB functions depending on `CONFIG_MLXSW_SPECTRUM_DCB`, and ethtool/TC/netdev operations.

ACL and multicast routing use the operation tables as indirection. Shared ACL code asks `mlxsw_sp->acl_tcam_ops` to allocate region/chunk/entry private objects and perform entry add/delete/activity operations. KVDL users call `mlxsw_sp_kvdl_alloc()` and the selected `mlxsw_sp_kvdl_ops` handles Spectrum-1 fixed partitions or Spectrum-2 resource-backed partitions. Multicast routing calls `mlxsw_sp_mr_tcam_ops` for route create/destroy/update.

## State and Persistence Behavior

This header does not allocate storage by itself, but it defines the long-lived state shape for the driver. Most fields are in-memory reflections of hardware state and kernel topology. Examples include port VLAN membership lists, flow block counters, parsing reference counts, PTP configurations, LAG IDs, KVDL allocations, ACL rule info, FID references, and NVE bindings.

Several inline helpers mutate or inspect state: port bitmap init/fini allocate bitmaps sized by core max ports, flow block disable helpers adjust counters, and lookup helpers walk VLAN lists or bridge lower devices. Locking contracts are documented only by field comments in places, such as `port_mapping_events.queue_lock`, `parsing.lock`, and `ipv6_addr_ht_lock`.

## Dependencies and Integration Points

The header includes Linux networking, bridge, VLAN, DCB, rhashtable, notifier, namespace, psample, flow offload, and VXLAN headers, plus mlxsw `port.h`, `core.h`, ACL flex key/action headers, and register definitions. It is included by most Spectrum implementation files, so changes here have broad compile impact.

## Risks and Edge Cases

- `struct mlxsw_sp` is a large shared ownership object; adding fields without clear init/fini ownership can introduce leaks or stale generation-specific behavior.
- Many callbacks are assumed non-NULL after generation init. A missing op pointer typically fails later as a crash rather than a compile error.
- Inline helpers such as `mlxsw_sp_port_lagged_get()` index into `mlxsw_sp->ports[local_port]` based on core LAG mapping and assume local-port validity from the core.
- Flow-block disable counters are simple increments/decrements; unbalanced calls can permanently disable offload or underflow logically.
- The DCB stubs return success when the config option is disabled, so call sites must not assume DCB state exists.
- The broad include surface can make small header changes expensive and can hide dependencies that should remain local to implementation files.

## Test Signals

Compile coverage across Spectrum DCB enabled/disabled and all Spectrum generations is the primary header-level signal. Runtime coverage should exercise every selected op table: KVDL alloc/free, ACL TCAM region/entry operations, multicast route add/update/delete, FID init/fini, PTP ops, port speed conversion, SPAN, policers, traps, matchall, qdisc, NVE, and router paths. Static checks should flag unchecked callback pointers, unbalanced flow-block disable calls, and raw `mlxsw_sp->ports[]` indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_acl_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_acl_tcam.c

## Purpose

`spectrum1_acl_tcam.c` implements the Spectrum-1 ACL TCAM backend. It adapts shared ACL TCAM code to the older C-TCAM model, installs a per-region catchall continue rule, exposes region/chunk/entry private storage sizes, adds and deletes entries through common C-TCAM helpers, and reads rule activity through the `PTCE2` register.

## Important APIs, Types, and Functions

The exported object is `mlxsw_sp1_acl_tcam_ops`. Its key type is `MLXSW_REG_PTAR_KEY_TYPE_FLEX`, `priv_size` is zero, and its callbacks are backed by local wrappers.

Local private types are `mlxsw_sp1_acl_tcam_region`, `mlxsw_sp1_acl_tcam_chunk`, and `mlxsw_sp1_acl_tcam_entry`. The region embeds `struct mlxsw_sp_acl_ctcam_region`, stores the generic region pointer, and owns a catchall chunk, entry, and rule info pointer.

Important helpers include `mlxsw_sp1_acl_ctcam_region_catchall_add()`, `mlxsw_sp1_acl_ctcam_region_catchall_del()`, `mlxsw_sp1_acl_tcam_region_init()`, `mlxsw_sp1_acl_tcam_entry_add()`, `mlxsw_sp1_acl_tcam_entry_del()`, and `mlxsw_sp1_acl_tcam_entry_activity_get()`.

## Control Flow

TCAM initialization itself is a no-op for Spectrum-1. Region initialization initializes the embedded C-TCAM region, creates a catchall chunk at `MLXSW_SP_ACL_TCAM_CATCHALL_PRIO`, creates an ACL rule info object, adds a continue action, commits it, and inserts it into the C-TCAM region. On failure it destroys the rule info and finalizes the catchall chunk before finalizing the C-TCAM region.

Normal chunks simply wrap `mlxsw_sp_acl_ctcam_chunk_init()` and `mlxsw_sp_acl_ctcam_chunk_fini()`. Entry add wraps `mlxsw_sp_acl_ctcam_entry_add()` with `fillup_priority=false`; entry delete calls the matching C-TCAM delete helper. Action replacement returns `-EOPNOTSUPP`, so callers must delete/re-add or avoid replacement on this backend.

Activity reads derive the C-TCAM entry offset, pack a `PTCE2` query with clear-on-read operation, query hardware, and return the activity bit.

## State and Persistence Behavior

State is per ACL region/chunk/entry and lives in the private objects allocated by shared ACL code according to the sizes in `mlxsw_sp1_acl_tcam_ops`. The catchall rule is persistent hardware TCAM state for each region until region finalization. Activity reads are clear-on-read, so querying activity mutates hardware activity state.

## Dependencies and Integration Points

The backend depends on shared ACL TCAM helpers in `spectrum_acl_tcam.h`, ACL rule info creation/action/commit helpers from the ACL core, and register access to `PTCE2`. It is selected by `mlxsw_sp1_init()` in `spectrum.c` and used by shared ACL ruleset/rule code.

## Risks and Edge Cases

- Catchall rule creation has multiple failure labels; leaks or double-finalization here would affect every ACL region.
- `entry_action_replace` is unsupported. TC offload paths must handle `-EOPNOTSUPP` gracefully for rule action changes.
- Activity query clears the activity bit, so polling frequency changes user-visible `last_used` behavior.
- Region association is a no-op; shared code must not expect a hardware association step on Spectrum-1.
- The C-TCAM region entry insert/remove hooks are empty by design, unlike Spectrum-2 where mask/ERP state is allocated.

## Test Signals

Exercise TC flower rule add/delete on Spectrum-1, region creation/destruction with an empty ruleset, catchall continue behavior, activity polling, action replacement failure handling, and error injection for rule info allocation, commit, and C-TCAM entry add.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_acl_tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_kvdl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_kvdl.c

## Purpose

`spectrum1_kvdl.c` implements the Spectrum-1 KVD linear allocator. Spectrum-1 divides the linear KVD space into three fixed-granularity partitions: single entries, 32-entry chunks, and 512-entry large chunks. The file allocates and frees entries from bitmap-backed partitions, reports devlink resource occupancy, and registers Spectrum-1-specific devlink resources for the KVD linear sub-partitions.

## Important APIs, Types, and Functions

The exported operation table is `mlxsw_sp1_kvdl_ops`, with `init`, `fini`, `alloc`, `free`, and `alloc_size_query` callbacks. `mlxsw_sp1_kvdl_resources_register()` registers the devlink child resources for singles, chunks, and large chunks.

`struct mlxsw_sp1_kvdl_part_info` describes a partition's start/end index, allocation size, and devlink resource ID. `struct mlxsw_sp1_kvdl_part` stores a mutable copy of that info plus a flexible bitmap. `struct mlxsw_sp1_kvdl` stores the three partition pointers.

Allocation helpers select the smallest partition whose allocation size can hold the requested entry count, find the first zero usage bit, set it, and translate the bit index to a KVDL index. Freeing finds the owning partition by index and clears the corresponding usage bit.

## Control Flow

Initialization builds each partition in order. For each partition it tries to read an overridden devlink resource size. If a size is present, it updates that partition's start/end so partitions are packed consecutively according to configured sizes; otherwise it uses compile-time defaults. It allocates a usage bitmap sized by `resource_size / alloc_size`. After all parts are initialized, it registers occupancy callbacks for the aggregate linear resource and each child partition.

Allocation ignores entry type and is size-driven. `alloc_size_query` returns the selected partition allocation size so higher-level code can know how many entries a request consumes. Finalization unregisters occupancy callbacks in reverse order and frees all partitions.

## State and Persistence Behavior

Persistent state is in-memory usage bitmaps per partition. Occupancy is derived by scanning set bits and multiplying by partition allocation size. Hardware cleanup is not issued in this file when freeing; Spectrum-1 callers are responsible for overwriting or invalidating the hardware records they used.

Devlink resource sizes can affect partition boundaries at initialization. Those choices persist for the device lifetime but are not stored by this file.

## Dependencies and Integration Points

The allocator is selected through `mlxsw_sp->kvdl_ops` for Spectrum-1. It depends on `spectrum.h` constants and devlink resource APIs. Its allocations back ACL action sets, adjacency data, multicast/NVE structures, IPv6 addresses, and other KVDL users through the generic `mlxsw_sp_kvdl_*()` wrappers.

## Risks and Edge Cases

- Allocation is first-fit and always chooses the smallest sufficient allocation size. Long-running mixed workloads can fragment each fixed partition independently.
- `free()` silently returns if the index does not belong to a known partition, which prevents a crash but can hide double-free or corrupted-index bugs.
- The allocator does not use the entry type, so type-specific isolation is not enforced on Spectrum-1.
- Resource override sizes are packed sequentially; invalid or surprising devlink sizing can shift later partition ranges.
- Bitmap updates are not locally locked. Correctness depends on serialization in upper KVDL users or driver control paths.

## Test Signals

Validate devlink resource registration and occupancy for all three partitions, allocation-size queries for requests of 1, 32, 512, and oversized counts, exhaustion behavior, free/reallocate reuse, devlink size override boot paths, and stress with mixed ACL/action/NVE/router users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_kvdl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_mr_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_mr_tcam.c

## Purpose

`spectrum1_mr_tcam.c` implements Spectrum-1 multicast routing TCAM operations. It maintains separate IPv4 and IPv6 multicast TCAM regions, uses `parman` to place routes by priority while supporting resize and move operations, and programs route entries through `RMFT2`, region allocation/resizing through `RTAR`, and TCAM moves through `RRCR`.

## Important APIs, Types, and Functions

The exported operation table is `mlxsw_sp1_mr_tcam_ops`. It provides private sizes, `init`, `fini`, `route_create`, `route_destroy`, and `route_update`.

`struct mlxsw_sp1_mr_tcam_region` stores the owning `mlxsw_sp`, RTAR key type, parman instance, and priority array. `struct mlxsw_sp1_mr_tcam` stores one region per L3 protocol. `struct mlxsw_sp1_mr_tcam_route` stores the parman item and selected parman priority.

Route programming helpers are `mlxsw_sp1_mr_tcam_route_replace()` and `mlxsw_sp1_mr_tcam_route_remove()`. Region helpers allocate/deallocate/resize hardware regions and move TCAM ranges. `mlxsw_sp1_mr_tcam_region_parman_ops` configures base count 16, resize step 16, and `PARMAN_ALGO_TYPE_LSORT`.

## Control Flow

Initialization first requires `ACL_MAX_TCAM_RULES`, then allocates an IPv4 multicast region and an IPv6 multicast region using `RTAR`. Each region creates a parman instance and initializes priority objects for all multicast route priorities.

Route creation adds a parman item to the protocol-specific region and priority. Parman assigns an index and may call resize/move callbacks. The route is then written to `RMFT2` with group/source addresses and masks plus the first action set from the AFA block. On write failure the parman item is removed. Destroy removes the hardware route and removes the parman item. Update rewrites the existing index with a new action block.

Finalization destroys IPv6 then IPv4 regions, finalizing priorities, destroying parman, and deallocating hardware regions.

## State and Persistence Behavior

In-memory state consists of per-protocol parman placement state and one private route object per multicast route. Hardware state includes allocated RTAR regions, RMFT2 route records, and RRCR moves performed during parman compaction/resizing. Route indexes are stable only through the parman item and may change when moves occur.

## Dependencies and Integration Points

This backend is selected by Spectrum-1 init and called by shared multicast routing code in `spectrum_mr.c`. It depends on Linux `parman`, register helpers from `reg.h`, AFA action blocks, L3 protocol and multicast route key definitions from `spectrum.h` / `spectrum_mr.h`, and the `ACL_MAX_TCAM_RULES` resource.

## Risks and Edge Cases

- The IPv4/IPv6 switch statements have no default branch; callers must provide only supported protocols.
- Region resize is limited by global `ACL_MAX_TCAM_RULES`, so multicast route scaling competes conceptually with ACL TCAM capacity.
- `mlxsw_sp1_mr_tcam_region_free()` and parman move callbacks ignore write failures, which can hide teardown or compaction hardware errors.
- Route destroy removes hardware before parman state; a failed remove write is ignored by the void destroy path.
- Priority ordering depends on parman and the enum order in `mlxsw_sp_mr_route_prio`.

## Test Signals

Test IPv4 and IPv6 multicast route add/update/delete, all priorities including catchall, route counts crossing 16-entry resize boundaries, forced parman moves, exhaustion beyond `ACL_MAX_TCAM_RULES`, AFA block changes, and failure injection for RTAR, RMFT2, RRCR, parman allocation, and priority allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_mr_tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_acl_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_acl_tcam.c

## Purpose

`spectrum2_acl_tcam.c` implements the Spectrum-2-and-newer ACL TCAM backend using A-TCAM and ERP masks. It reserves KVDL action-set space for default region actions, initializes default continue actions in hardware, hooks C-TCAM mask insertion/removal to ERP mask references, delegates region/chunk/entry operations to shared A-TCAM helpers, supports action replacement, and reports activity via the stored AFA action block.

## Important APIs, Types, and Functions

The exported object is `mlxsw_sp2_acl_tcam_ops` with key type `MLXSW_REG_PTAR_KEY_TYPE_FLEX2`. Private types are `mlxsw_sp2_acl_tcam`, `mlxsw_sp2_acl_tcam_region`, `mlxsw_sp2_acl_tcam_chunk`, and `mlxsw_sp2_acl_tcam_entry`.

Initialization is handled by `mlxsw_sp2_acl_tcam_init()`. It allocates KVDL action-set entries, builds an uncommitted continue AFA block, writes default actions with `PEFA`, writes the base with `PGCR`, and initializes shared A-TCAM state. Entry add/delete/replace wrap `mlxsw_sp_acl_atcam_*()` helpers. Activity uses `mlxsw_afa_block_activity_get()` on the entry's current action block.

## Control Flow

During TCAM init the backend determines how many default action KVDL entries to reserve. It uses the generic TCAM max-region count unless the `ACL_MAX_DEFAULT_ACTIONS` resource is available. It allocates `ACTSET` KVDL entries, creates a continue action block, obtains the current encoded action set, writes one default action per exposed host region using `PEFA`, writes `PGCR` with the KVDL base, and initializes A-TCAM.

Region initialization stores the generic region pointer and calls `mlxsw_sp_acl_atcam_region_init()` with rehash hints and C-TCAM region ops. The C-TCAM entry insert hook obtains an ERP mask for the rule mask and stores it in the A-TCAM entry; the remove hook puts that ERP mask. Chunk and entry lifecycle are thin A-TCAM wrappers. Action replacement updates the stored action block pointer and delegates replacement to A-TCAM.

## State and Persistence Behavior

The backend owns a KVDL range for default TCAM actions over its lifetime. Region private state owns A-TCAM region state; entries own A-TCAM entry state and a pointer to the current AFA block used for activity reporting. ERP mask references are acquired per inserted C-TCAM entry and released on removal.

Hardware state includes KVDL action-set records, PGCR default action base, A-TCAM entries, and ERP mask programming performed by shared helpers. KVDL space is freed on TCAM finalization.

## Dependencies and Integration Points

This backend is used by Spectrum-2, Spectrum-3, and Spectrum-4 init paths. It depends on generic KVDL allocation, AFA action block creation/encoding/activity, A-TCAM/ERP helpers, `PEFA` and `PGCR` registers, and ACL resource discovery. Shared TC flower/matchall offload code reaches it through `mlxsw_sp_acl_tcam_ops`.

## Risks and Edge Cases

- The code may allocate more KVDL entries than host-exposed regions when `ACL_MAX_DEFAULT_ACTIONS` exceeds `_tcam->max_regions`; only exposed regions are initialized with `PEFA`, while hidden device regions are intentionally reserved.
- The continue AFA block is not committed; the code relies on `mlxsw_afa_block_cur_set()` encoding being valid for `PEFA`.
- Error unwinding must free KVDL after failures in AFA creation, PEFA writes, PGCR write, or A-TCAM init.
- Entry activity depends on `entry->act_block` being updated on add and action replacement; stale pointers would break stats/last-use reporting.
- ERP mask get/put balance is critical during rehash and entry removal.

## Test Signals

Test TCAM init/fini with and without `ACL_MAX_DEFAULT_ACTIONS`, PEFA/PGCR write failures, A-TCAM init failure unwind, rule add/delete with shared masks, rehash hint paths, action replacement, activity reporting after replacement, and KVDL leak checks under ACL rule churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_acl_tcam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_kvdl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_kvdl.c

## Purpose

`spectrum2_kvdl.c` implements the Spectrum-2-and-newer KVD linear allocator. Unlike Spectrum-1's fixed size classes, Spectrum-2 partitions KVDL by entry type and sizes those partitions from firmware resources. It tracks usage with bitmaps, allocates contiguous groups of usage bits for variable entry counts, asks firmware to delete freed KVDL records, and exposes generic KVDL operations.

## Important APIs, Types, and Functions

The exported operation table is `mlxsw_sp2_kvdl_ops`. `struct mlxsw_sp2_kvdl_part_info` maps each `enum mlxsw_sp_kvdl_entry_type` to a firmware IEDR resource type plus resource IDs used to determine usage bit count and index range. Supported parts include `ADJ`, `ACTSET`, `PBS`, `MCRIGR`, `IPV6_ADDRESS`, and `TNUMT`.

`struct mlxsw_sp2_kvdl_part` stores part info, usage bit count, indexes per usage bit, last allocated bit, and a flexible usage bitmap. Allocation uses `mlxsw_sp2_kvdl_part_find_zero_bits()` and `mlxsw_sp2_kvdl_part_alloc()`. Freeing uses `mlxsw_sp2_kvdl_rec_del()` to issue an `IEDR` delete record before clearing bitmap bits.

## Control Flow

Initialization iterates over the part-info array. For each entry type it requires both resource IDs, reads `usage_bit_count` and `index_range`, computes `indexes_per_usage_bit = index_range / usage_bit_count`, allocates the usage bitmap, and initializes `last_allocated_bit` to the last bit so the first allocation starts from zero.

Allocation converts entry count to hardware index size with `entry_count * mlxsw_sp_kvdl_entry_size(type)`, finds a contiguous free run of enough usage bits with wrap-around search, sets those bits, and returns `bit * indexes_per_usage_bit` as the KVDL index. Freeing computes the same size, writes an IEDR delete record for the resource type, and only clears bitmap bits if firmware deletion succeeds. `alloc_size_query` returns the requested entry count unchanged.

## State and Persistence Behavior

In-memory state is per-entry-type usage bitmaps and the `last_allocated_bit` cursor. Allocation is type-isolated: each entry type has a separate partition and firmware resource type. Hardware state is explicitly touched on free through `IEDR`, so the allocator coordinates both software reuse and firmware record invalidation.

There are no devlink occupancy callbacks in this file, unlike the Spectrum-1 allocator. Capacity comes from firmware resources queried during core resource discovery.

## Dependencies and Integration Points

The allocator is selected by Spectrum-2, Spectrum-3, and Spectrum-4 init paths. It depends on `resources.h` resource IDs, mlxsw core resource accessors, `IEDR` register helpers, and generic `mlxsw_sp_kvdl_*()` wrappers. It backs ACL action sets, adjacencies, port-buffer structures, multicast records, IPv6 address records, and tunnel/NVE tables depending on entry type.

## Risks and Edge Cases

- `indexes_per_usage_bit` is computed with integer division and is not checked for zero or remainder. Bad firmware resources could cause division-by-zero-adjacent behavior or under-accounted capacity.
- `mlxsw_sp2_kvdl_part_find_zero_bits()` uses `bit + bit_count >= usage_bit_count` as an end test, so exact-fit-at-end behavior should be reviewed carefully for off-by-one capacity loss.
- `last_allocated_bit` is never updated after successful allocation in this implementation, so allocation starts scanning from zero each time despite having a cursor field. That may be intentional simplification or a missed update causing first-fit behavior and fragmentation pressure.
- If the IEDR delete fails, bits are not cleared, preventing software reuse but potentially leaking capacity until reset.
- Bitmap operations are not locally locked and rely on caller serialization.

## Test Signals

Validate resource presence and sane `index_range / usage_bit_count` values for every entry type, exact-fit and near-end allocation cases, exhaustion, free after IEDR success/failure, repeated allocate/free reuse, mixed entry-type isolation, large entry_count requests requiring multiple bits, and KVDL users such as ACL action sets and IPv6 address storage on Spectrum-2/3/4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_kvdl.c -->
