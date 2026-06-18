# sources/distributed-fs/ceph-client/include/uapi/linux/batman_adv.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/batman_adv.h` exports the generic-netlink and rtnetlink userspace ABI for configuring and inspecting B.A.T.M.A.N. advanced mesh interfaces. The complete 704-line header was read. It names the netlink family and multicast groups, defines translation-table and multicast flags, gateway modes, netlink attributes, commands, throughput-meter reasons, and nested link attributes.

## Important APIs, Types, and Functions

There are no functions. Important symbols are `BATADV_NL_NAME`, multicast groups `BATADV_NL_MCAST_GROUP_CONFIG` and `BATADV_NL_MCAST_GROUP_TPMETER`, `enum batadv_tt_client_flags`, `enum batadv_mcast_flags_priv`, `enum batadv_gw_modes`, `enum batadv_nl_attrs`, `enum batadv_nl_commands`, `enum batadv_tp_meter_reason`, `enum batadv_ifla_attrs`, and `IFLA_BATADV_MAX`. The large `batadv_nl_attrs` enum covers mesh, hard-interface, originator, neighbor, TT, gateway, bridge-loop-avoidance, DAT, multicast, VLAN, and tunable configuration fields.

## Control Flow

The header has no runtime flow. Netlink flow is command/attribute driven: userspace sends a `BATADV_CMD_GET_*` request to dump mesh state, sends `BATADV_CMD_SET_MESH`, `BATADV_CMD_SET_HARDIF`, or `BATADV_CMD_SET_VLAN` to update tunables, or starts/cancels a throughput-meter session with the TP-meter commands. Kernel replies use the enumerated attributes and may emit multicast notifications on the config or throughput-meter groups.

## State and Persistence Behavior

This file defines runtime configuration and reporting state rather than owning storage. State described by attributes includes active hard interfaces, mesh addresses, routing algorithm, originator and neighbor metrics, translation-table state, multicast flags, VLAN IDs, bridge loop avoidance data, DAT cache entries, gateway mode/bandwidth/selection, hop penalty, log level, fragmentation, network coding, orig/ELP intervals, throughput override, and multicast fanout. Persistence is tied to kernel netdevice/module lifetime unless userspace reapplies configuration.

## Dependencies and Integration Points

This header is paired with the wire packet ABI in `batadv_packet.h` and with kernel policy tables in batman-adv netlink/rtnetlink implementation files. It integrates with libnl-style generic-netlink clients, rtnetlink creation of batadv netdevices through `IFLA_BATADV_ALGO_NAME`, and tooling such as `batctl` that uses stable enum values for dumps and configuration.

## Risks and Edge Cases

The comments explicitly require updating netlink policies when attributes or ifla values are added. Attribute and command numbering is ABI: reordering would break userspace. Some flags are local-only while others are remote or CRC-synchronized, so userspace must not treat all TT or multicast bits identically. TP-meter statuses deliberately reserve values below 128 for non-error completion/cancel and values at or above 128 for errors, matching `batadv_tp_is_error()` in the packet header. Alias commands such as `BATADV_CMD_GET_MESH_INFO` and `BATADV_CMD_GET_HARDIFS` must remain numerically identical to their base commands.

## Test Signals

Useful coverage includes generic-netlink policy tests, `batctl` dump/set smoke tests, netdevice creation through rtnetlink with `IFLA_BATADV_ALGO_NAME`, enum stability checks against userspace headers, multicast notification tests for config and TP-meter events, and integration tests that set every boolean/numeric mesh tunable and read it back through `BATADV_CMD_GET_MESH`.
