# sources/distributed-fs/ceph-client/net/tipc/monitor.h

## Purpose

`monitor.h` declares the TIPC monitor API and the per-link monitor cache structure used by `link.c`. It is the interface between bearer/node peer events, link protocol STATE-message preparation/receive, and netlink monitor reporting.

## Important APIs, Types, and Functions

`struct tipc_mon_state` stores a link endpoint's cached monitor list generation, peer domain generation, acked self-domain generation, and flags for monitoring, probing, reset, and synchronization. Prototypes cover monitor create/delete, peer up/down/remove, STATE-message prepare/receive, cached state lookup, threshold set/get, netlink monitor and peer dump, self-address reinitialization, and exported `tipc_max_domain_size`.

## Control Flow

Bearer setup creates a monitor per bearer. Node/link up/down events update peers. Link protocol send calls `tipc_mon_prep()` with its `tipc_mon_state`; receive calls `tipc_mon_rcv()`; timeout calls `tipc_mon_get_state()` to decide whether to probe or reset. Control-plane netlink uses threshold and dump functions.

## State and Persistence Behavior

The header has no global mutable state except the external size constant. `struct tipc_mon_state` persists inside each link and caches monitor decisions across STATE messages. The `synched` flag gates initial generation synchronization after link reset.

## Dependencies and Integration Points

It includes `netlink.h` and references `struct net`, `struct tipc_nl_msg`, and link protocol buffers. It integrates with link state messages, bearer lifecycle, node peer events, and generic netlink monitor commands.

## Risks and Edge Cases

`tipc_mon_state` fields are part of link behavior but not wire format. Resetting the structure at the wrong time can cause missed generation acks or unnecessary probes; failing to reset after link reset can ignore a peer's first domain record. `tipc_max_domain_size` must match the actual maximum record size in `monitor.c`.

## Test Signals

Compile coverage catches API drift. Runtime validation should observe monitor flags changing during peer churn, threshold netlink set/get behavior, link reset clearing monitor state, and STATE-message payload sizing using `tipc_max_domain_size`.
