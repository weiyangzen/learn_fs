# sources/distributed-fs/ceph-client/net/dsa/switch.c

## Purpose
This file handles switch-wide reactions to DSA notifier events. It translates bridge, LAG, FDB, MDB, VLAN, MTU, ageing-time, tag-protocol, tag_8021q, and conduit-state notifications into driver callbacks, while maintaining refcounted shared-port and LAG programming state.

## Important APIs, Types, And Functions
Public functions are `dsa_vlan_find()`, `dsa_tree_notify()`, `dsa_broadcast()`, `dsa_switch_register_notifier()`, and `dsa_switch_unregister_notifier()`. The central dispatcher is `dsa_switch_event()`. Internal helpers include `dsa_switch_ageing_time()`, `dsa_switch_mtu()`, bridge join/leave, FDB/MDB add/delete for user, host, and LAG databases, VLAN add/delete for user and host paths, tag protocol connect/disconnect/change, and conduit-state forwarding.

Notifier payload types are declared in `switch.h` and carry the source port, database identity, bridge/LAG state, VLAN object, extack, MTU, or tag ops.

## Control Flow
Ports call `dsa_port_notify()` or `dsa_broadcast()`, which invokes raw notifier chains registered per switch tree. Each switch receives `dsa_switch_event()` and handles only events relevant to it. Cross-chip bridge/LAG callbacks are invoked when the event source is on another switch and the driver supports cross-chip operations.

FDB/MDB/VLAN programming is direct for user ports but refcounted for CPU and DSA shared ports because multiple user ports or databases can require the same hardware entry. Add paths search the local list, bump refcount if present, or program hardware and allocate bookkeeping. Delete paths decrement refcount and only remove hardware on the last reference; hardware delete failure restores the refcount. LAG FDBs are similarly refcounted on `struct dsa_lag`.

Ageing time programming selects the fastest active port ageing time for chips with a shared setting. MTU changes apply to the targeted user port plus CPU/DSA ports. Tag-protocol change first calls driver `change_tag_protocol`, updates CPU port receive callbacks, then refreshes user tagger setup and MTU. Connect/disconnect events notify both tagger callbacks and optional switch callbacks.

## State And Persistence
State is stored in per-port `fdbs`, `mdbs`, and `vlans` lists protected by mutexes, LAG FDB lists protected by `lag->fdb_lock`, and switch notifier registrations in each tree's raw notifier head. This state persists for the life of the DSA tree and is cleaned during port/switch release.

## Dependencies And Integration Points
This file integrates DSA port code, switch driver callbacks, switchdev bridge objects, VLAN objects, LAGs, tag_8021q, runtime tagger switching, tracing, and raw notifier chains.

## Risks And Edge Cases
Reference counting shared hardware entries is correctness-critical; missed deletes leave stale FDB/MDB/VLAN entries, while extra deletes remove entries still needed by another database. Some callbacks return `-EOPNOTSUPP`; callers may treat it as acceptable depending on event type. `dsa_broadcast()` warns it is unreliable during asynchronous probe because not all trees may exist. Tagger connect failures must unwind tagger-side state to avoid leaks.

## Test Signals
Tests should exercise notifier dispatch for each event, shared-port FDB/MDB/VLAN refcount add/delete, hardware delete failures, cross-chip bridge/LAG callbacks, ageing-time bounds, MTU propagation, tag protocol change/connect/disconnect, tag_8021q VLAN propagation, and conduit-state notifications.
