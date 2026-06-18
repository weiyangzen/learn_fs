# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state_change.h

## Purpose

`drbd_state_change.h` defines the old/new state-change record structures used to broadcast DRBD state changes to userspace and internal notification consumers. It separates resource, connection, device, and peer-device state dimensions so a single transition can describe all affected objects in a multi-volume resource.

## Important APIs and Types

`struct drbd_resource_state_change` stores the resource pointer, role, and resource suspension flags (`susp`, `susp_nod`, `susp_fen`) for `OLD` and `NEW` slots. `struct drbd_device_state_change` stores local disk state for a device. `struct drbd_connection_state_change` stores connection state and peer role. `struct drbd_peer_device_state_change` stores per-peer-device disk state, replication state, and the three resync suspension booleans.

`struct drbd_state_change` is the aggregate container: it has a list node, counts for devices/connections, an inline single resource entry, and pointers into a packed allocation for device, connection, and peer-device arrays. The declared helpers are `remember_old_state()`, `copy_old_to_new_state_change()`, and `forget_state_change()`, plus four `notify_*_state_change()` functions that serialize individual dimensions into notification messages.

## Control Flow

`drbd_state.c` allocates and fills this structure before applying a state transition, fills the `NEW` slots afterward, queues it with after-change work, and eventually passes it to `broadcast_state_change()`. Notification code compares `OLD` and `NEW` slots and emits only changed resource, connection, device, or peer-device messages, preserving continuation markers until the final notification in a batch.

## State and Persistence Behavior

The structures are snapshots, not persistent state. They hold kref-protected pointers to live DRBD objects while queued work may run later. The `OLD` and `NEW` array indices make transitions explicit and avoid reconstructing previous state after the live object has already changed.

## Dependencies and Integration Points

The file depends on DRBD object types, state enums, `struct list_head`, `struct sk_buff`, and the notification type enum from surrounding kernel/DRBD headers. It integrates with `drbd_state.c`, generated netlink notification helpers such as `notify_resource_state()`, `notify_connection_state()`, `notify_device_state()`, and `notify_peer_device_state()`, and any code that wants to report state changes after a deferred transition.

## Risks and Edge Cases

The packed allocation layout in `drbd_state.c` must match the pointer fields declared here. Peer-device entries are ordered as the Cartesian product of devices and connections, so enumeration order must remain stable between old and new capture. Forgetting to drop captured krefs would leak resources; failing to take them would risk use-after-free in queued notifications.

## Test Signals

Tests should confirm that multi-volume transitions produce one coherent notification sequence, unchanged dimensions are skipped, continuation flags are set until the last message, and teardown transitions still notify destroyed peer devices/connections while references are valid.
