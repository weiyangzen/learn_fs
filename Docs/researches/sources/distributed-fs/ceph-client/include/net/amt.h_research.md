# sources/distributed-fs/ceph-client/include/net/amt.h

## Purpose

`amt.h` defines the Automatic Multicast Tunneling netdevice data model, wire headers, state machines, timers, limits, and device-identification helpers used by the AMT gateway/relay implementation.

## Important APIs, Types, and Functions

The header defines AMT message types for discovery, advertisement, request, membership query/update, multicast data, and teardown; set-operation/filter/action/status enums for multicast membership handling; and gateway events. Packed wire structs model each AMT header using endian-sensitive bitfields and nonces/MAC fields. `struct amt_dev` is the main netdevice-private state with the outer device, stream device, namespace, socket pointer, global lock, relay tunnel list, GRO cells, discovery/request/secret/event work, ports, IPs, nonce, MAC, IGMP/MLD query parameters, capacity limits, and gateway event queue.

Relay state is represented by `struct amt_tunnel_list`, `struct amt_group_node`, and `struct amt_source_node`, with spinlocks, delayed GC/source/group timers, RCU heads, hash buckets, nonce/key/MAC fields, and source/group counts. Helpers include `netif_is_amt()` for rtnl link kind detection and `amt_gmi()` to compute the group membership interval from query variables.

## Control Flow

Gateway flow starts with discovery and request work, records received advertisements/queries through status transitions, and queues AMT events in `amt_events` for the event work handler. Relay flow receives discovery/request/update/data messages, allocates or looks up tunnel/group/source nodes, schedules timers for garbage collection and membership expiry, and encapsulates/decapsulates multicast traffic between UDP AMT and the stream device. Header unions allow handlers to parse only the layouts valid for gateway or relay direction.

## State and Persistence Behavior

There is no durable storage. Runtime state is concentrated in `struct amt_dev`, tunnel/group/source RCU lists, socket pointer, GRO cells, work items, nonce/MAC/key material, and timer-backed membership state. Membership and tunnel state expires through delayed work; relay/gateway configuration persists only while the netdevice exists.

## Dependencies and Integration Points

The header depends on siphash/jhash, netdevice, rtnetlink, GRO cells, sockets, IPv4 and optional IPv6 addresses, RCU, delayed work, and UDP/IP header layouts. It integrates as an rtnl link kind named `amt`, with multicast routing/IGMP/MLD behavior and netdevice packet paths.

## Risks and Edge Cases

Packed endian bitfields are fragile across compiler/architecture assumptions and must match AMT wire format exactly. Tunnel/group/source objects mix spinlocks, RCU, and delayed work; missed cancellation or freeing can become use-after-free. Capacity limits (`max_groups`, `max_sources`, `max_tunnels`, event queue length) need enforcement under load. Nonce/MAC/key handling must avoid accepting spoofed updates. IPv6 fields are conditional, so dual-stack code must handle disabled IPv6 builds.

## Test Signals

Test all AMT message parsers, endian layouts, discovery/request retries, nonce mismatch, response MAC validation, gateway and relay status transitions, tunnel/group/source timeout cleanup, maximum group/source/tunnel limits, event queue overflow, GRO delivery, netdevice teardown with pending work, IPv6-enabled and IPv6-disabled builds, and `netif_is_amt()` kind matching.
