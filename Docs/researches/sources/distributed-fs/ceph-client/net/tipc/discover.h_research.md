# sources/distributed-fs/ceph-client/net/tipc/discover.h

## Purpose

`discover.h` exposes the small discovery subsystem contract to bearer and node management code. It keeps `struct tipc_discoverer` opaque and declares lifecycle, destination-count, reset, and receive entry points for link setup discovery.

## Important APIs, Types, and Functions

The header forward-declares `struct tipc_discoverer`. `tipc_disc_create()` initializes per-bearer discovery and returns an initial discovery skb. `tipc_disc_delete()` tears it down. `tipc_disc_reset()` reinitializes the reusable request after bearer changes. `tipc_disc_add_dest()` and `tipc_disc_remove_dest()` update discovered peer count for timer behavior. `tipc_disc_rcv()` is the inbound discovery message handler.

## Control Flow

Bearer activation calls create, then later passes inbound LINK_CONFIG discovery skbs to `tipc_disc_rcv()`. Link/node up/down paths call add/remove destination to adjust discovery polling. Bearer reset calls `tipc_disc_reset()` to rebuild request metadata, and bearer teardown calls delete.

## State and Persistence Behavior

The header owns no state but enforces opacity of the discoverer internals. Persistent runtime state lives in `discover.c` and `struct tipc_bearer->disc`.

## Dependencies and Integration Points

The declarations integrate with `struct net`, `struct tipc_bearer`, `struct tipc_media_addr`, and `struct sk_buff` users without including their full definitions here. It is included by bearer/node setup code and `discover.c`.

## Risks and Edge Cases

Because the type is opaque, callers must respect lifecycle ordering: no receive/reset/add/remove calls after delete and no delete while uncoordinated timer or bearer users still reference the object. API misuse would become use-after-free in `discover.c`.

## Test Signals

Compile coverage should catch declaration drift. Runtime signals are bearer enable/delete cycles, discovery reset after media changes, and correct timer behavior when destination count moves between zero and nonzero.
