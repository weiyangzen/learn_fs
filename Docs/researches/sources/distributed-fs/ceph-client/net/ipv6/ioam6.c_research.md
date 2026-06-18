# sources/distributed-fs/ceph-client/net/ipv6/ioam6.c

Purpose: implements IPv6 In-situ OAM namespace/schema management, generic-netlink events, and trace-data filling. It owns per-net namespace/schema rhashtables and exposes helpers used by IOAM Hop-by-Hop processing and lightweight tunnels.

Important APIs, types, and functions: `ioam6_namespace()`, `ioam6_trace_compute_nodelen()`, `ioam6_fill_trace_data()`, `ioam6_event()`, `ioam6_init()`, and `ioam6_exit()` are externally relevant. Netlink operations add/delete/dump namespaces, add/delete/dump schemas, and bind/unbind a schema to a namespace. Core objects are `struct ioam6_namespace`, `struct ioam6_schema`, and `struct ioam6_pernet_data`.

Control flow: per-net init allocates the data object, initializes a mutex and two rhashtables, and stores it in `net->ipv6.ioam6_data`. Netlink add/del operations validate required attributes, serialize under the per-net mutex, and mutate rhashtables with RCU freeing. Schema binding updates both sides of the namespace-schema relationship with RCU assignments. Trace filling computes the data insertion pointer from remaining length, node length, and optional schema length, then writes selected IOAM fields such as hop limit/node id, ingress/egress ids, timestamps, namespace data, queue backlog, wide fields, and opaque schema data.

State and persistence: namespace and schema state is per-net and memory-only. Relationships are one-to-one: assigning a schema detaches any previous namespace using that schema and detaches the namespace's previous schema. Trace data is packet-local. Netlink multicast events are transient.

Dependencies and integration points: depends on generic netlink, rhashtable, `net/ioam6.h`, IPv6 addrconf per-device IOAM ids, qdisc queue stats, skb timestamps, pernet subsystem registration, and optional `ioam6_iptunnel_init()`.

Risks: this snapshot contains a duplicated `err = rhashtable_remove_fast(&nsdata->schemas, &sc->head,` line in `ioam6_genl_delsc()`, which is a compile-break signal unless it is intentional source corruption. Trace field writes are pointer arithmetic over packed protocol data and depend on correct `remlen`/`nodelen` validation. Queue-depth sampling locks the qdisc in softirq context. Undefined trace bits are filled with unavailable values, so spec changes need mask updates.

Test signals: netlink add/delete/dump namespace and schema operations, schema reassignment races under lockdep/RCU, trace filling for every supported bit including overflow, namespace data endian checks, qdisc backlog sampling, multicast listener events, and build coverage with `CONFIG_IPV6_IOAM6_LWTUNNEL`.
