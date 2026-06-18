<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netevent.h -->
# sources/distributed-fs/ceph-client/include/net/netevent.h

## Purpose
`netevent.h` declares the generic networking notifier chain for neighbour updates, redirects, probe-timer updates, and route hash/forward priority changes.

## Important APIs, types, and functions
It defines `struct netevent_redirect`, `enum netevent_notif_type`, and functions to register, unregister, and call netevent notifiers.

## Control flow
Subsystems register notifier blocks. Producers call `call_netevent_notifiers` with an event code and typed payload such as `struct neighbour`, `struct netevent_redirect`, `struct neigh_parms`, or `struct net`.

## State and persistence
Notifier-chain state lives in the implementation. Payload state remains owned by the caller and is transient for the callback duration.

## Dependencies and integration points
It depends on notifier blocks and forward declarations for dst, neighbour, and net. It integrates routing, neighbour, and upper-layer consumers that react to topology/cache changes.

## Risks and test signals
Risks include wrong payload type for event IDs, notifier lifetime during module unload, callbacks sleeping in unsuitable context, and ordering assumptions. Tests should cover notifier registration/unregistration, every event type, and module unload while events fire.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netevent.h` completely for this pass (39 lines, 1068 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netevent.h -->
