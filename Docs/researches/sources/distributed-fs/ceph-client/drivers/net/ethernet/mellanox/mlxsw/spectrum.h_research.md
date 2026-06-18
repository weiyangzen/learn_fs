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
