# sources/distributed-fs/ceph-client/net/dsa/switch.h

## Purpose
This private header defines DSA notifier event IDs, event payload structures, and switch notifier APIs shared by port, switch, and tree code.

## Important APIs, Types, And Functions
The enum lists all `DSA_NOTIFIER_*` events: ageing time, bridge join/leave, FDB/MDB host and user operations, LAG changes and FDB operations, VLAN host and user operations, MTU, tag-protocol change/connect/disconnect, tag_8021q VLAN add/delete, and conduit-state changes. Payload structs include `dsa_notifier_bridge_info`, `dsa_notifier_fdb_info`, `dsa_notifier_lag_info`, `dsa_notifier_vlan_info`, `dsa_notifier_mtu_info`, `dsa_notifier_tag_proto_info`, and others.

It declares `dsa_vlan_find()`, `dsa_tree_notify()`, `dsa_broadcast()`, `dsa_switch_register_notifier()`, and `dsa_switch_unregister_notifier()`.

## Control Flow
No executable logic is present. The event definitions determine dispatch in `switch.c` and call sites in `port.c`, `dsa.c`, and tag_8021q code.

## State And Persistence
No state is stored here. Payload structs carry transient event data across notifier calls.

## Dependencies And Integration Points
It includes `<net/dsa.h>` for DSA data structures and forward-declares extack. It is the contract for cross-chip and cross-module DSA event propagation.

## Risks And Edge Cases
Adding a notifier ID requires updating `dsa_switch_event()` and all expected producers/consumers. Payload lifetime must outlive synchronous raw notifier delivery.

## Test Signals
Compile coverage plus notifier tests for every event type validate this contract.
