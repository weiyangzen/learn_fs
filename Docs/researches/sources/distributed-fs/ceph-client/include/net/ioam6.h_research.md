# sources/distributed-fs/ceph-client/include/net/ioam6.h

Purpose: declares IPv6 In-situ OAM namespace/schema state and event/trace helpers. IOAM carries telemetry data inside IPv6 packets.

Important APIs/types: `struct ioam6_namespace` is an rhashtable/RCU object with optional schema pointer, namespace id, narrow data, and wide data. `struct ioam6_schema` is another rhashtable/RCU object with linked namespace, id, length, header, and flexible data. `struct ioam6_pernet_data` stores a mutex and namespace/schema rhashtables. `ioam6_pernet()` returns per-net IOAM data when IPv6 is enabled. APIs find namespaces, fill trace data into an skb, compute trace node length, initialize/exit core and iptunnel support, and emit IOAM generic-netlink events.

Control flow and state: netlink/config code creates namespaces and schemas under the per-net mutex, packet paths look up namespaces and fill trace data, and events notify userspace. State persists per network namespace in rhashtables and is reclaimed via RCU.

Dependencies and integration: depends on IPv6, IOAM UAPI/genl headers, rhashtable, skbuff, network namespaces, and tunnel code. It integrates with IPv6 extension headers, lightweight tunnels, and Generic Netlink control.

Risks: schema/namespace RCU lifetimes and trace length calculations must match packet space. Tests should cover namespace/schema add/delete, trace fill for input/output, node length for all trace bits, IPv6-disabled builds, tunnel init/exit, and netlink event emission.
