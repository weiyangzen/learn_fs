# sources/distributed-fs/ceph-client/drivers/infiniband/core/nldev.c

## Purpose
`nldev.c` implements the RDMA_NL_NLDEV netlink client, which is the main userspace control and introspection interface for RDMA devices. It reports device and port properties, dumps resource-tracker objects, exposes driver-specific details, controls RDMA counter modes and optional hardware counters, manages RDMA links and subdevices, reports character devices, emits monitor notifications, and configures FRMR pools.

## Important APIs, types, and functions
- Exported helpers include `rdma_nl_put_driver_string()`, `rdma_nl_put_driver_u32()`, `rdma_nl_put_driver_u32_hex()`, `rdma_nl_put_driver_u64()`, `rdma_nl_put_driver_u64_hex()`, `rdma_nl_get_privileged_qkey()`, `rdma_nl_stat_hwcounter_entry()`, `rdma_link_register()`, `rdma_link_unregister()`, and `rdma_nl_notify_event()`.
- `nldev_policy[]` defines validation for all NLDEV attributes, including device/port identifiers, resource IDs, statistics attributes, system settings, monitor event fields, and FRMR pool keys.
- `fill_dev_info()` and `fill_port_info()` construct device and port replies, including GUIDs, firmware, protocol, node type, DIM flag, port state, LID/SM LID/LMC, netdevice association, and capability flags.
- Resource fill helpers cover QP, raw QP, CM ID, CQ, raw CQ, MR, raw MR, PD, context, SRQ, raw SRQ, and counter entries.
- `res_get_common_doit()` and `res_get_common_dumpit()` implement the shared one-object and dump paths over RDMA restrack xarrays.
- Link management uses registered `struct rdma_link_ops` implementations through `nldev_newlink()` and `nldev_dellink()`.
- Statistics handlers include `nldev_stat_set_doit()`, `nldev_stat_del_doit()`, `nldev_stat_get_doit()`, `nldev_stat_get_dumpit()`, and `nldev_stat_get_counter_status_doit()`.
- FRMR pool handlers include `nldev_frmr_pools_get_dumpit()` and `nldev_frmr_pools_set_doit()`.
- `nldev_cb_table[]` maps all `RDMA_NLDEV_CMD_*` operations to doit/dump callbacks and admin-permission flags.

## Control flow
`nldev_init()` registers `nldev_cb_table` with the generic RDMA netlink dispatcher. GET commands parse identifiers, look up devices with `ib_device_get_by_index()` in the sender's net namespace, fill an skb, unicast the reply, and drop the device reference. Dump commands use netlink callback cursors in `cb->args[0]` to resume across devices, ports, resources, or FRMR pools.

Resource-specific commands either require a device-level resource ID or, for per-port resources such as QP and counters, a valid port. The common dump path opens a nested resource table, walks the restrack xarray under its lock, skips driver-detail-marked resources unless requested, takes a restrack reference before dropping the xarray lock, fills one nested entry, then resumes. Fill functions add common fields such as PID or kernel resource name and call optional driver hooks for extended or raw details.

Admin commands rename devices, move devices to another net namespace, toggle DIM, create/delete RDMA links, create/delete subdevices, change system netns and privileged QKey modes, bind/unbind QP counters, change counter auto mode, enable/disable optional hardware counters, adjust FRMR aging period, and pin FRMR pool handles. Monitor events build a compact NLDEV_CMD_MONITOR message and multicast it to `RDMA_NL_GROUP_NOTIFY`.

## State and persistence
The file owns a small amount of global state: `privileged_qkey`, the registered link-ops list protected by `link_ops_rwsem`, and the NLDEV callback table while registered. Most reported state comes from live RDMA devices, their restrack roots, counters, hw stats, FRMR pools, net namespace membership, and netdevices. System toggles such as privileged QKey mode and compatible-device netns mode remain kernel runtime state, not durable configuration.

## Dependencies and integration points
`nldev.c` integrates with the generic RDMA netlink dispatcher in `netlink.c`, RDMA device lookup and lifetime rules, restrack, CMA internals for CM ID reporting, uverbs context objects, RDMA counters, hardware stats, dynamic link providers such as RXE, character-device client info, FRMR pool management, netdevice association, and net namespaces. Userspace tools such as `rdma` from iproute2 consume this ABI.

## Risks
- Netlink ABI compatibility is critical. Attribute type, nesting, command, and permission changes can break userspace.
- Resource dumps walk live xarrays while objects are being created and destroyed. Missing restrack references or incorrect `-EAGAIN` handling can race or omit entries.
- Sensitive identifiers such as lkey/rkey and raw driver details are gated by `CAP_NET_ADMIN`; new fields must be audited for disclosure.
- Several handlers allocate reply skbs before performing mutable operations. Error cleanup must free skbs and release device/restrack/cdev references on every path.
- `stat_get_doit_qp()` uses static local mode/mask variables, which is unusual for a request handler and should be treated carefully under concurrency.
- Dynamic link deletion can unregister devices; handlers must not use device pointers after operations that consume references.
- Monitor error logging assumes netdevice lookup succeeds in some event cases; attach/rename failure paths should be tested with disappearing netdevices.

## Test signals
- Netlink ABI tests should cover every command in `nldev_cb_table` for required attributes, malformed attributes, permission checks, namespace lookup, and dump cursor resume.
- Resource tests should create QP, CQ, PD, MR, SRQ, CM ID, context, and counter objects, then verify both summary and detailed dumps, including driver-detail filtering.
- CAP_NET_ADMIN tests should check raw resource commands, lkey/rkey exposure, link/subdevice admin, system settings, stat mutation, and FRMR pool mutation.
- Counter tests should cover auto/manual QP counter binding, unbinding, optional hwcounter dynamic masks, default counter queries, and disabled-counter filtering.
- Monitor tests should subscribe to `RDMA_NL_GROUP_NOTIFY` and verify register, unregister, rename, netdev attach/detach, and netdev rename payloads.
