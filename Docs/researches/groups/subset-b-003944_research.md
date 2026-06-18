# Research: subset-b-003944

Grouped research for Mellanox mlx5 RDMA driver files under `sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5`. Each section preserves the original source path and is bounded for reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/gsi.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/gsi.c

## Purpose
`gsi.c` implements the mlx5 software wrapper for InfiniBand GSI/QP1 behavior. The driver creates one hardware receive-side GSI QP and, when the hardware supports programmable DETH source QPN, optional UD transmit QPs per P_Key index or per RoCE LAG transmit port. The wrapper preserves normal RDMA-core QP1 APIs while hiding the hardware split between receive QP and send QPs.

## Important APIs, Types, And Functions
`struct mlx5_ib_gsi_wr` is the private outstanding-send bookkeeping object. It embeds an `ib_cqe`, a saved `ib_wc`, and a completion flag. The public entry points are `mlx5_ib_create_gsi`, `mlx5_ib_destroy_gsi`, `mlx5_ib_gsi_modify_qp`, `mlx5_ib_gsi_query_qp`, `mlx5_ib_gsi_post_send`, `mlx5_ib_gsi_post_recv`, and `mlx5_ib_gsi_pkey_change`.

`generate_completions()` walks `gsi->outstanding_wrs` in producer/consumer order and emits saved completions through `mlx5_ib_generate_wc()`. `handle_single_completion()` is installed as the hardware CQE callback and copies the real WC into the wrapper slot while preserving the original caller `wr_id`. `setup_qp()` creates and transitions a UD transmit QP for a valid P_Key or LAG port slot. `get_tx_qp()` selects the appropriate transmit QP, falling back to the hardware GSI QP when no fanout is used.

## Control Flow
Creation allocates the transmit-QP pointer array and outstanding WR ring, allocates a private send CQ, creates the hardware GSI receive QP with type `MLX5_IB_QPT_HW_GSI`, and registers the wrapper in `dev->devr.ports[port - 1].gsi`. If DETH source-QPN setting is unavailable, `num_qps` is zero and sends go directly through `rx_qp`; otherwise IB ports size the table by `max_pkeys`, while LAG Ethernet ports size it by `dev->lag_ports`.

Modify calls are forwarded to `rx_qp`. Once the hardware QP reaches RTS, every configured transmit slot is lazily initialized by `setup_qp()`. Send posting clones each UD WR, selects a transmit QP under `gsi->lock`, records an outstanding completion slot, posts to the selected hardware QP, and rolls back the producer index on post failure. Missing transmit QPs produce a successful synthetic send completion through `mlx5_ib_gsi_silent_drop()`.

## State And Persistence Behavior
State is in memory only and lives inside `struct mlx5_ib_qp.gsi`: `rx_qp`, private CQ, transmit QP array, ring indices, saved capabilities, port number, and lock. `dev->devr.ports[].gsi` is a lifecycle integration pointer used by port P_Key event work. No persistent storage is written. Ordering is preserved by completing only consecutive ring entries from `outstanding_ci` to the first incomplete entry.

## Dependencies And Integration Points
The file depends on RDMA core QP/CQ APIs, `mlx5_ib_generate_wc()` from the CQ path, P_Key queries through `ib_query_pkey()`, and mlx5 capabilities such as `set_deth_sqpn`, port type, and LAG state. It is invoked by the QP implementation when creating/querying/modifying/posting/destroying `IB_QPT_GSI`, and by `main.c` P_Key-change work via `mlx5_ib_gsi_pkey_change()`.

## Risks
The lock protects both transmit-QP creation and outstanding WR ring state; regressions here can corrupt send completion order. `setup_qp()` must destroy failed QPs; this source has `WARN_ON_ONCE(qp)` in the error path rather than an actual destroy call, so cleanup behavior should be checked against the wider tree. Silent drops intentionally report success when a needed transmit QP is unavailable, which is protocol-sensitive and should remain limited to the wrapper's expected QP1 semantics. The ring is bounded by `cap.max_send_wr`; zero or mismatched capabilities would break modulo arithmetic.

## Test Signals
Useful tests include QP1 create/destroy on IB and Ethernet RoCE ports, P_Key table changes creating new transmit QPs, posting with invalid P_Key indexes and verifying synthetic completions, LAG xmit-port selection through AH attributes, and stress posting enough WRs to hit the ring-full path and completion ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/gsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.c

## Purpose
`ib_rep.c` implements RDMA representor support for mlx5 eswitch offloads. It registers an auxiliary `rdma-rep` driver, loads/unloads IB representors for eswitch vports, creates a raw Ethernet RDMA device for uplink representors, binds non-uplink vports as ports on that device, and integrates with LAG/shared-FDB topologies.

## Important APIs, Types, And Functions
The key exported functions are `mlx5r_rep_init()`, `mlx5r_rep_cleanup()`, `mlx5_ib_get_rep_netdev()`, and `create_flow_rule_vport_sq()`. `mlx5_ib_vport_rep_load()` and `mlx5_ib_vport_rep_unload()` are registered as `struct mlx5_eswitch_rep_ops`. `mlx5_ib_set_vport_rep()` attaches a loaded eswitch rep to an existing `mlx5_ib_dev` port and sets the RDMA port netdev. `mlx5_ib_take_transport()` and `mlx5_ib_release_transport()` transfer RDMA transport flow-table root ownership across peer devices when shared-FDB LAG requires a common owner.

## Control Flow
Probe registers `rep_ops` with the eswitch for `REP_IB`. Loading an uplink representor usually allocates a new `mlx5_ib_dev` with `raw_eth_profile`, sets `is_rep`, sizes `ibdev->port` from local and peer vport counts, maps the RDMA port to the representor netdev, and calls `__mlx5_ib_add()`. Non-uplink vports are then represented by setting `dev->port[vport_index].rep`, setting `rep->rep_data[REP_IB].priv`, mapping the netdev with `ib_device_set_netdev()`, and adding a LAG demux rule when the vport is not native to the owner eswitch.

In shared-FDB LAG, non-master devices calculate an adjusted `vport_index` based on peer device sequence and MPESW/non-MPESW rules. The master can register peer vport reps after the uplink RDMA device exists. Unload reverses the netdev mapping and private pointers, deletes demux rules, unregisters peer reps for shared-FDB uplink teardown, releases transport ownership, and removes the RDMA device through `__mlx5_ib_remove()`.

## State And Persistence Behavior
Representor state is in memory: `rep->rep_data[REP_IB].priv` points at the owning `mlx5_ib_dev`, and `dev->port[i].rep` points back to the eswitch rep. LAG demux and RDMA transport flow-table root ownership are hardware/firmware-managed state changed during load/unload. There is no persistent disk state.

## Dependencies And Integration Points
This file integrates mlx5 eswitch representors, LAG APIs, flow steering root-device ownership, RDMA device registration through `main.c` profiles, and raw packet SQ steering. `create_flow_rule_vport_sq()` is used by raw packet QP setup to send a representor SQ to its vport via `mlx5_eswitch_add_send_to_vport_rule()`.

## Risks
Index accounting across shared-FDB, MPESW, and peer device sequence ordering is error-prone; a wrong `vport_index` maps netdevs and demux rules to the wrong RDMA port. Load/unload must be symmetric, especially transport root ownership rollback and peer representor unregister. `create_flow_rule_vport_sq()` returns `NULL` for non-reps or port zero and `ERR_PTR(-EINVAL)` when a rep is missing, so callers must distinguish no-op from hard failure.

## Test Signals
Exercise switchdev representor creation/removal, shared-FDB LAG master and non-master load order, MPESW uplinks, non-uplink vport demux rules, raw packet QP traffic through representor SQ steering, and cleanup while peer vports are still registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.h

## Purpose
`ib_rep.h` is the small public interface between mlx5 RDMA core code and representor support. It exposes representor initialization, cleanup, raw Ethernet profile access, netdev lookup, and send-to-vport rule creation while compiling to no-op stubs when `CONFIG_MLX5_ESWITCH` is disabled.

## Important APIs, Types, And Functions
The header declares `extern const struct mlx5_ib_profile raw_eth_profile`, `mlx5r_rep_init()`, `mlx5r_rep_cleanup()`, `create_flow_rule_vport_sq()`, and `mlx5_ib_get_rep_netdev()`. The function signatures use `struct mlx5_ib_dev`, `struct mlx5_ib_sq`, `struct mlx5_eswitch`, `struct mlx5_flow_handle`, and `struct net_device`.

## Control Flow
There is no runtime control flow beyond conditional compilation. With eswitch support enabled, callers link to `ib_rep.c`. Without eswitch support, initialization returns success, cleanup is empty, flow-rule creation returns `NULL`, and representor netdev lookup returns `NULL`.

## State And Persistence Behavior
The header owns no state. It determines whether representor state is reachable at compile time. The stub behavior makes non-eswitch builds treat representor features as absent rather than failing module initialization.

## Dependencies And Integration Points
It includes `<linux/mlx5/eswitch.h>` and `mlx5_ib.h`, making it part of the mlx5 RDMA driver's internal ABI. `main.c` uses `raw_eth_profile` and module-level `mlx5r_rep_init()/cleanup()`. QP/raw-packet flow paths use `create_flow_rule_vport_sq()`.

## Risks
Stubs returning `NULL` rely on callers interpreting `NULL` as "feature absent/no flow rule needed". Any caller that treats `NULL` as success with a required representor rule can silently skip steering. The include relationship also means changes in `mlx5_ib.h` can affect this header's users broadly.

## Test Signals
Build coverage with `CONFIG_MLX5_ESWITCH=y` and disabled, plus raw packet representor traffic tests in enabled builds and module load tests in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_virt.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_virt.c

## Purpose
`ib_virt.c` implements RDMA-core SR-IOV VF management operations for mlx5 IB devices. It lets the PF query or set VF link-state policy, query VF traffic counters, and set/get VF node and port GUIDs.

## Important APIs, Types, And Functions
Public entry points are `mlx5_ib_get_vf_config()`, `mlx5_ib_set_vf_link_state()`, `mlx5_ib_get_vf_stats()`, `mlx5_ib_set_vf_guid()`, and `mlx5_ib_get_vf_guid()`. Helper converters `mlx_to_net_policy()` and `net_to_mlx_policy()` map between mlx5 `enum port_state_policy` and netlink `IFLA_VF_LINK_STATE_*` constants. Private helpers `set_vf_node_guid()` and `set_vf_port_guid()` write the selected GUID field.

## Control Flow
Get-config allocates an HCA vport context, queries `vf + 1` as an "other vport", translates the policy, and fills `struct ifla_vf_info`. Set-link-state validates the requested netlink policy, sets `MLX5_HCA_VPORT_SEL_STATE_POLICY`, modifies the HCA vport context, and mirrors the policy into `mdev->priv.sriov.vfs_ctx[vf]` on success. Stats allocate a firmware output buffer, query vport counters, and map selected unicast and multicast packet/octet counters into `ifla_vf_stats`. GUID setters update firmware and mark cached `node_guid_valid` or `port_guid_valid` in `vfs_ctx`. GUID getter returns cached GUIDs or zero when not valid.

## State And Persistence Behavior
Firmware vport context is the authoritative state for policy and GUID programming. The driver mirrors successful policy/GUID writes into the in-memory SR-IOV VF context under `mdev->priv.sriov.vfs_ctx`. Statistics are queried on demand and not stored.

## Dependencies And Integration Points
These functions are installed in `main.c` as `mlx5_ib_dev_sriov_ops` when the device is a PF. They depend on mlx5 vport commands, `struct mlx5_vf_context`, RDMA `ib_device` container conversion, and Linux netlink VF structures.

## Risks
The file assumes RDMA-core validation of VF index and port arguments; direct misuse could index `vfs_ctx` out of range. Firmware and cache must remain consistent: cache updates occur only after successful modify commands. `mlx5_ib_get_vf_config()` returns `-EINVAL` if firmware returns an unknown policy translation.

## Test Signals
Use PF SR-IOV tests for setting VF link states disable/enable/auto, reading them back, setting node and port GUIDs and verifying cached get behavior, querying stats under traffic, and negative testing invalid policy values and firmware command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_virt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.c

## Purpose
`macsec.c` bridges RoCE GID programming with mlx5 MACsec offload steering. When RoCE UDP-encap GIDs are added on offloaded MACsec netdevs, it installs MACsec-aware RoCE steering rules, handles security association add/delete events, and manages ambiguous physical-vs-MACsec GID slots.

## Important APIs, Types, And Functions
The exported functions are `mlx5r_macsec_init_gids_and_devlist()`, `mlx5r_macsec_dealloc_gids()`, `mlx5r_macsec_event_register()`, `mlx5r_macsec_event_unregister()`, `mlx5r_add_gid_macsec_operations()`, and `mlx5r_del_gid_macsec_operations()`. `struct mlx5_reserved_gids` records a MACsec GID index and referenced physical GID attribute for ambiguous IP handling. `struct mlx5_macsec_device` tracks one MACsec netdev, its RoCE GID list, and TX/RX SA rule lists. `struct mlx5_roce_gids` stores a saved GID index and IPv4/IPv6 socket address.

## Control Flow
Initialization checks `mlx5_is_macsec_roce_supported()`, allocates `reserved_gids` arrays per RDMA port sized by the RoCE address table, initializes entries to `-1`, and initializes the MACsec device list and mutex. Event registration attaches a blocking notifier to `mdev->macsec_nh`. On SA-added events, `handle_macsec_gids()` finds or creates the MACsec-device record and installs SA rules for every saved RoCE GID. On SA-deleted events, `del_sa_roce_rule()` removes matching TX/RX SA rules.

GID add operations ignore non-RoCE-v2 GIDs and unsupported devices. They RCU-read `attr->ndev`, require an offloaded MACsec netdev, hold a netdev reference, then serialize on `dev->macsec.lock`. The code finds/creates the MACsec device, tries to find a physical GID with the same GID value, clears that physical hardware GID if found, records the physical GID in `reserved_gids`, adds MACsec RoCE steering, saves the RoCE GID address, and returns. GID delete reverses the ambiguity handling and removes steering/list entries.

## State And Persistence Behavior
All state is in memory: per-port `reserved_gids`, `dev->macsec.macsec_devices_list`, per-device GID and SA-rule lists, notifier registration, and referenced `ib_gid_attr` objects. Firmware or flow-steering state is changed through mlx5 MACsec rule helpers and `set_roce_addr()`. There is no disk persistence.

## Dependencies And Integration Points
`main.c` calls the add/delete hooks from `mlx5_ib_add_gid()` and `mlx5_ib_del_gid()`, initializes/deallocates MACsec state in the init stage, and registers/unregisters the notifier in the device-notifier stage. The file depends on Linux MACsec netdev helpers, RDMA GID cache APIs, mlx5 MACsec flow-steering helpers, and `set_roce_addr()` from `main.c`.

## Risks
Reference lifetimes are sensitive: physical GIDs found through `rdma_find_gid()` must be released exactly once, and MACsec netdev references are paired with `dev_hold()/dev_put()`. Ambiguous GID handling temporarily clears a physical GID slot; failure paths must restore it. `get_macsec_device()` creates records even in delete paths, so unexpected delete events can allocate empty records before `cleanup_macsec_device()` removes them. Concurrency relies on the MACsec mutex after RCU netdev lookup.

## Test Signals
Test adding/removing RoCE v2 GIDs on offloaded MACsec netdevs, SA add/delete notifier replay, duplicate/ambiguous GID addresses, IPv4-mapped and IPv6 GIDs, unsupported MACsec capability paths, and teardown with outstanding saved GIDs or SA rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.h

## Purpose
`macsec.h` exposes the internal mlx5 RoCE MACsec hooks to the RDMA driver while providing compile-time no-op stubs when `CONFIG_MLX5_MACSEC` is disabled.

## Important APIs, Types, And Functions
The header forward-declares `struct mlx5_reserved_gids` and declares GID add/delete hooks, GID/device-list initialization and deallocation, and MACsec event notifier register/unregister helpers. In non-MACsec builds, the add/init functions return success and delete/dealloc/register/unregister functions are empty.

## Control Flow
There is no runtime control flow in the header. Conditional compilation selects real implementations from `macsec.c` or stubs. The real hooks are called from `main.c` in GID cache operations and device lifecycle stages.

## State And Persistence Behavior
The header owns no state directly. Its conditional declaration controls whether `struct mlx5_ib_port` includes per-port `reserved_gids` in `mlx5_ib.h`, and whether MACsec operations manipulate `dev->macsec` state.

## Dependencies And Integration Points
It includes `<net/macsec.h>`, RDMA cache/address headers, and `mlx5_ib.h`. Because `mlx5_ib.h` also includes `macsec.h`, changes here can influence most mlx5 RDMA compilation units.

## Risks
The no-op stubs mean callers must not rely on MACsec side effects when the feature is disabled. Header include cycles are managed by include guards, but adding definitions that require complete mlx5 types could create ordering problems.

## Test Signals
Build tests with `CONFIG_MLX5_MACSEC=y` and disabled, plus runtime tests confirming GID add/delete works without MACsec support and invokes steering only when support is compiled and advertised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mad.c

## Purpose
`mad.c` implements mlx5 RDMA MAD handling and MAD_IFC query helpers. It filters incoming management datagrams, forwards supported classes/methods to firmware, provides special PMA counter handling, and exposes helper queries for node, port, P_Key, and GID data used by `main.c`.

## Important APIs, Types, And Functions
The central entry point is `mlx5_ib_process_mad()`. Query helpers include `mlx5_query_ext_port_caps()`, `mlx5_query_mad_ifc_system_image_guid()`, `mlx5_query_mad_ifc_max_pkeys()`, `mlx5_query_mad_ifc_vendor_id()`, `mlx5_query_mad_ifc_node_desc()`, `mlx5_query_mad_ifc_node_guid()`, `mlx5_query_mad_ifc_pkey()`, `mlx5_query_mad_ifc_gids()`, and `mlx5_query_mad_ifc_port()`. Internal helpers include `mlx5_MAD_IFC()`, `process_pma_cmd()`, `query_ib_ppcnt()`, and PMA assignment routines for standard and extended counters.

## Control Flow
`mlx5_ib_process_mad()` ignores unsupported management classes and methods, consumes invalid trap requests, handles PMA GETs locally when vport counters are supported, and otherwise calls `mlx5_MAD_IFC()`. `mlx5_MAD_IFC()` checks SMI permission for subnet management classes using `dev->port_caps[].has_smi`, builds an operation modifier for ignored M_Key/B_Key checks, and calls `mlx5_cmd_mad_ifc()`.

PMA handling determines the native mlx5 port for the RDMA port, falls back to the PF first port when a multiport peer is unaffiliated, and uses PPCNT registers for SMI devices or vport counters for normal devices. `IB_PMA_CLASS_PORT_INFO` replies advertise extended-width counters. Port query helpers construct SMPs, issue MAD_IFC queries, and decode fixed byte offsets into RDMA core structures, including extended speed handling for FDR/EDR/HDR/NDR/XDR and FDR-10 extended-port info.

## State And Persistence Behavior
The file does not own long-lived mutable state. It reads `dev->port_caps` and may set `ext_port_cap` in `mlx5_query_ext_port_caps()`. All MAD buffers and register outputs are per-call allocations. Firmware and hardware counters are queried on demand.

## Dependencies And Integration Points
`main.c` installs `mlx5_ib_process_mad()` in `ib_device_ops` and uses the query helpers for MAD-backed access on IB ports without virtualized HCA access. The file depends on RDMA MAD/SMP/PMA definitions, mlx5 command MAD_IFC support from `cmd.h`, mlx5 PPCNT register access, and multiport native-port resolution functions from `main.c`.

## Risks
MAD data decoding uses fixed offsets into SMP data; spec or firmware layout mismatches would produce wrong attributes. PMA paths allocate buffers sized for the max of vport-counter and PPCNT structures; size mistakes can corrupt decoding. SMI permission depends on earlier `set_has_smi_cap()` initialization. Native-port fallback for unaffiliated multiport devices intentionally returns data for port 1, which can be surprising during hotplug or partial initialization.

## Test Signals
Exercise MAD GET/SET/TRAP_REPRESS filtering, SMI permission denial, PMA standard and extended counter queries on SMI and non-SMI devices, port attribute decoding across IB link speeds, P_Key and GID table queries, and multiport unaffiliated fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/main.c

## Purpose
`main.c` is the mlx5 RDMA driver's primary registration and lifecycle implementation. It maps mlx5 core devices into RDMA `ib_device` instances, publishes device and port operations, handles RoCE and InfiniBand port queries, manages user contexts and mmap objects, coordinates events, multiport/LAG, representors, data-direct resources, and staged probe/remove profiles.

## Important APIs, Types, And Functions
Major externally visible functions are `__mlx5_ib_add()`, `__mlx5_ib_remove()`, `mlx5_ib_query_port()`, `mlx5_ib_query_port_speed()`, `set_roce_addr()`, `mlx5_ib_dev_res_cq_init()`, `mlx5_ib_dev_res_srq_init()`, `mlx5_ib_data_direct_bind()`, and `mlx5_ib_data_direct_unbind()`. Module entry/exit are `mlx5_ib_init()` and `mlx5_ib_cleanup()`. Auxiliary probes are `mlx5r_probe()` for RDMA devices and `mlx5r_mp_probe()` for multiport devices.

Key device operation tables are `mlx5_ib_dev_ops`, optional `mlx5_ib_dev_sriov_ops`, `mlx5_ib_dev_mw_ops`, `mlx5_ib_dev_xrc_ops`, `mlx5_ib_dev_common_roce_ops`, representor port ops, and UAPI definitions in `mlx5_ib_defs`. Profiles `pf_profile`, `raw_eth_profile`, and `plane_profile` define ordered init/cleanup stages.

## Control Flow
Module init allocates an emergency translation page, creates the ordered event workqueue, initializes QP event support and ODP, registers representor and data-direct drivers, then registers multiport and RDMA auxiliary drivers. RDMA auxiliary probe allocates `mlx5_ib_dev`, sizes its port array, detects multiplane SMI support for IB, chooses `pf_profile` or `raw_eth_profile`, and calls `__mlx5_ib_add()`.

`__mlx5_ib_add()` runs profile stages in enum order and unwinds already-initialized stages on failure. The normal PF profile initializes base state and special mkeys, flow steering, capabilities and operation tables, non-default port callbacks, RoCE, QP/SRQ tables, device resources, ODP, counters, debugfs, BFREGs, devx whitelist, system-error notifier, RDMA registration, device notifier/MACsec events, UMR pools, delay drop, and restrack. Remove sets `ib_active=false`, runs cleanup in reverse stage order, frees the port array, and deallocates the RDMA device.

Port query flow selects one of three access methods: MAD_IFC for native IB without `ib_virt`, HCA vport access for IB/HCA mode, or NIC vport access for Ethernet/RoCE. RoCE query translates Ethernet PTYS link modes into RDMA width/speed, reflects netdev carrier and MTU, and handles LAG upper netdevs and representors. GID add/delete hooks call MACsec operations and program hardware RoCE address-table entries through `mlx5_core_roce_gid_set()`.

User-context flow validates ABI request versions, optional DevX creation and privileged UID capability, BFREG/UAR allocation strategy, transport-domain allocation, doorbell-page list setup, CQE version negotiation, and response copying. Mmap flow decodes legacy command offsets or RDMA user mmap entries, maps UAR WC/NC pages, core clock pages, MEMIC/VAR/TLP VAR entries, and frees entries through type-specific cleanup.

Event flow converts mlx5 core notifier events into RDMA events on an ordered workqueue. Port changes generate speed, active/error, LID, P_Key, GID, and client-reregister events; P_Key changes schedule GSI QP refresh. System errors walk outstanding QPs and armed CQs to trigger completions, dispatch fatal events, and mark the device inactive. Netdev and LAG notifiers synchronize RoCE port state and RDMA netdev mappings.

Multiport flow maintains global master and unaffiliated-port lists under `mlx5_ib_multiport_mutex`. Masters create a native-port stub, bind matching peer ports by system image GUID, affiliate/unaffiliate NIC vports, track peer netdevs, replay core events, and enable local loopback across master/slave devices. Multiport auxiliary devices either bind to an existing master or wait on the unaffiliated list.

## State And Persistence Behavior
All state is kernel memory and firmware/hardware state. Important in-memory state includes `dev->ib_active`, port arrays, `mlx5_ib_port.roce` netdev tracking, multiport `mpi` pointers and refcounts, `devr` internal PD/CQ/SRQ/XRCD resources, xarrays for ODP and signature MRs, flow DB, data-direct resources, VAR bitmaps, delay-drop debugfs state, and notifier blocks. Firmware state includes PDs, UARs, transport domains, vport RoCE enablement, LAG demux/vport LAG, mkeys, MACsec/RoCE address table entries, and node descriptions. No durable disk state is written.

## Dependencies And Integration Points
`main.c` is the integration point for RDMA core, mlx5 core, eswitch representors, LAG, netdev notifiers, DevX, flow steering, ODP, UMR, memory registration, device memory, counters, congestion debugfs, data-direct, DMAH, MACsec, and auxiliary bus probing. Most other mlx5 RDMA files provide functions installed here into `ib_device_ops` or profile stages.

## Risks
The staged lifecycle must remain strictly symmetric; wrong stage ordering can expose operations before resources exist or free resources while callbacks are live. Several failure paths in `__mlx5_ib_add()` return `-ENOMEM` instead of the original error, which can hide root causes. Mmap offset decoding and RDMA mmap-entry ownership are security-sensitive because they expose PCI BAR pages and device memory to userspace. Multiport refcount/unaffiliate logic depends on correct completion counts under spinlocks. Netdev notifier paths must balance `dev_put()` calls and avoid dispatching events after `ib_active` becomes false. RoCE GID deletion calls `set_roce_addr(..., NULL, attr)`, while `set_roce_addr()` still uses `gid->raw`; this relies on surrounding code/contracts and is a high-value review point.

## Test Signals
Core signals include module load/unload; RDMA auxiliary probe/remove; `ibv_devinfo`, ucontext allocation, DevX contexts, UAR mmap, VAR/UAR uverbs objects; IB and RoCE port query/speed query; RoCE GID add/delete and netdev rescan; LAG active-backup changes; multiport peer hotplug/unplug; representor load/unload; system-error event injection; delay-drop debugfs; ODP/UMR/counter stage init; and failure injection at each profile stage to verify reverse cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mem.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mem.c

## Purpose
`mem.c` contains focused memory helper routines for mlx5 RDMA memory registration paths. It converts pinned user memory into hardware physical address segments and computes page-size/page-offset encodings for mlx5 command mailboxes with quantized offset fields.

## Important APIs, Types, And Functions
`mlx5_ib_populate_pas()` fills a PAS array from an `ib_umem` using `rdma_umem_for_each_dma_block()`. `__mlx5_umem_find_best_quantized_pgoff()` selects an allowed page size and calculates a quantized page offset. The public macro wrappers for the quantized helper are declared in `mlx5_ib.h`.

## Control Flow
PAS population iterates DMA blocks at the requested page size, ORs each DMA address with access flags, converts to big endian, and advances the output pointer. Quantized page-offset selection first asks RDMA core for the largest compatible page size using `ib_umem_find_best_pgoff()`. It then repeatedly halves the page size until the DMA offset fits in the mailbox page-offset field after scaling. If the reduced page size is not permitted by the original bitmap or the final quantized offset exceeds the field mask, it returns zero.

## State And Persistence Behavior
The file owns no state. It writes only caller-provided PAS arrays and page-offset output variables. Results are derived from the DMA mapping state held by `ib_umem`.

## Dependencies And Integration Points
The helpers are used by MR, CQ, QP, WQ, and device-memory registration code that needs mlx5 mailbox-compatible memory layout. Dependencies are RDMA umem iteration APIs, DMA block iterators, endian helpers, and page-size bitmaps prepared by `mlx5_ib.h` macros.

## Risks
The quantized loop assumes halving will eventually make the offset representable; invalid scale or bitmap inputs can still lead to a zero result. PAS population trusts the caller-provided array is large enough for `ib_umem_num_dma_blocks()`. Access flags are ORed into physical addresses, so flag bit placement must match hardware PAS format.

## Test Signals
Test user MR registration with aligned and unaligned addresses, multiple supported page sizes, small mailbox page-offset fields, dma-buf/ODP-backed umems where applicable, and PAS contents for read/write access flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mlx5_ib.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mlx5_ib.h

## Purpose
`mlx5_ib.h` is the central private header for the mlx5 RDMA driver. It defines core object containers, device state, capability helpers, stage/profile infrastructure, mmap formats, memory-key and ODP state, GSI state, RoCE/representor/MACsec integration fields, and prototypes for operations implemented across the driver.

## Important APIs, Types, And Functions
Important container types include `mlx5_ib_dev`, `mlx5_ib_ucontext`, `mlx5_ib_pd`, `mlx5_ib_qp`, `mlx5_ib_cq`, `mlx5_ib_srq`, `mlx5_ib_mr`, `mlx5_ib_mw`, `mlx5_ib_flow_db`, `mlx5_ib_port`, `mlx5_roce`, `mlx5_ib_resources`, `mlx5_ib_gsi_qp`, `mlx5_ib_delay_drop`, `mlx5_var_table`, and `mlx5_macsec`. The header declares conversion helpers such as `to_mdev()`, `to_mqp()`, `to_mcq()`, `to_mmr()`, and many RDMA operation prototypes.

Key enums and macros define QP pseudo-types (`MLX5_IB_QPT_HW_GSI`, `MLX5_IB_QPT_DCI`, `MLX5_IB_QPT_DCT`), UMR update flags, mmap types and offset layout, MTT access flags, mkey types, optional counter types, debug congestion parameters, and `enum mlx5_ib_stages`. `struct mlx5_ib_profile` maps stage IDs to init/cleanup callbacks.

## Control Flow
The header has limited executable control flow through inline helpers. Page-size helpers build supported page-size and page-offset bitmaps for mlx5 command fields. User-index helpers validate CQE-version-dependent user indexes. ODP helpers store and dereference mkeys in an xarray with waitqueue release. LAG affinity helper centralizes when a user context should get default transmit-port affinity. Page-size helpers for MKC choose supported page sizes based on hardware min/max entity-size caps and IOVA alignment.

## State And Persistence Behavior
The header defines the shape of all major in-memory driver state. `mlx5_ib_dev` owns the RDMA device, core-device pointer, notifiers, port array, device resources, UMR/ODP/flow/counter/debug/data-direct/mkey state, profile pointer, special mkeys, and optional MACsec state. Per-object structures mirror RDMA-core objects and add mlx5 hardware IDs, buffers, locks, and firmware resources. No state is persisted by the header itself.

## Dependencies And Integration Points
It includes Linux kernel, RDMA core, mlx5 core, uverbs, mlx5 ABI, SRQ/QP, and MACsec headers. Every file in this work item depends on it directly or indirectly. Prototypes tie together implementations in AH, CQ, QP, MR, SRQ, MAD, memory, ODP, DevX, flow steering, counters, data-direct, and `main.c`.

## Risks
Because this is the central private ABI, layout or semantic changes can affect many compilation units. Locking responsibilities are embedded in comments and fields: QP mutexes, WQ spinlocks, CQ resize mutexes, flow DB mutex, delay-drop mutex, multiport spinlocks, data-direct lock, and MACsec lock must be honored by implementation files. Conditional fields under `CONFIG_MLX5_MACSEC` and ODP stubs require build-matrix coverage. Mmap enum values and object sizes are user ABI-adjacent and must remain compatible with uverbs expectations.

## Test Signals
Build coverage across feature combinations (`CONFIG_MLX5_ESWITCH`, `CONFIG_MLX5_MACSEC`, ODP, user access, IPoIB), sparse/lockdep where available, uverbs ABI tests for object sizes and mmap offsets, QP/CQ/MR/SRQ lifecycle tests, ODP mkey reference tests, GSI QP tests, and multiport/LAG/representor tests that exercise the fields defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mlx5_ib.h -->
