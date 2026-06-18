# sources/distributed-fs/ceph-client/net/tipc/link.h

## Purpose

`link.h` declares the public interface and constants for the TIPC link layer. It lets node, bearer, broadcast, netlink, monitor, and socket paths create links, drive their FSM, enqueue traffic, receive packets, manage broadcast synchronization, and inspect link properties without exposing `struct tipc_link` internals.

## Important APIs, Types, and Functions

The header defines `ELINKCONG`, external FSM event constants, receive/timeout return event bits, and `MAX_PKT_DEFAULT`. Prototypes cover unicast and broadcast link creation, tunnel/failover preparation, reset/state message generation, FSM events, state predicates, active flag, reset/stats reset, transmit/receive, queue accessors, sequence and identity accessors, property getters/setters, netlink property parsing and dump, timeout handling, broadcast peer management, MTU/MSS, gap ACK parsing, broadcast init/sync/ack/nack, silence checking, and namespace lookup.

## Control Flow

Node and bearer code create links, pass outbound skbs to `tipc_link_xmit()`, pass inbound skbs to `tipc_link_rcv()`, call `tipc_link_timeout()` from node timers, and react to returned event bits such as `TIPC_LINK_UP_EVT`, `TIPC_LINK_DOWN_EVT`, and `TIPC_LINK_SND_STATE`. Broadcast code uses the broadcast-specific helpers to synchronize send and receive links.

## State and Persistence Behavior

The header has no storage and keeps `struct tipc_link` opaque. Persistent runtime state is owned by `link.c`, while callers observe it through accessors such as `tipc_link_state()`, `tipc_link_rcv_nxt()`, `tipc_link_acked()`, `tipc_link_mtu()`, `tipc_link_prio()`, and `tipc_link_tolerance()`.

## Dependencies and Integration Points

It includes generic netlink plus TIPC `msg.h` and `node.h`. It is a central integration point for TIPC node management, broadcast, netlink control plane, bearer media setup, monitor, and socket data paths.

## Risks and Edge Cases

The event constants are magic values used for diagnostics and FSM dispatch; accidental changes break callers. Return event bits are combinable and must be handled as flags. Callers must hold the correct node/broadcast locks around mutable link operations because the opaque type does not enforce synchronization.

## Test Signals

Compile coverage catches API drift. Runtime signals include link up/down events from timeout and receive paths, netlink property parsing validation, broadcast helper behavior, and caller handling of `ELINKCONG` from `tipc_link_xmit()`.
