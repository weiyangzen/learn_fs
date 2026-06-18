# sources/cloud-native/moby/daemon/libnetwork/networkdb/broadcast.go

## Purpose
Defines NetworkDB memberlist broadcast message wrappers and send helpers for network, node, and table events.

## Important APIs, Types, And Functions
`networkEventMessage`, `nodeEventMessage`, and `tableEventMessage` implement `memberlist.Broadcast`. `sendNetworkEvent`, `sendNodeEvent`, and `sendTableEvent` encode protobuf messages and enqueue them. `getBroadcasts` drains multiple transmit queues within packet limits.

## Control Flow
Network/table broadcast invalidation coalesces messages by network/node or network/table/key. Node events do not invalidate. `sendNodeEvent` waits up to five seconds for `Finished` notification when peers exist. `sendTableEvent` looks up the local joined network before queuing on its table broadcast queue. `getBroadcasts` decreases remaining packet budget after each queue.

## State And Persistence
No persistence. It mutates memberlist transmit queues and reads NetworkDB network/node state under locks.

## Dependencies And Integration Points
Called by `networkdb.go` entry/network lifecycle and by cluster join/leave logic. Uses `memberlist` and `serf` Lamport times.

## Risks
Incorrect invalidation can drop necessary events or flood queues. Node broadcast timeout can surface as join/leave failure when peers are slow. Table events for removed networks are silently skipped.

## Test Signals
No direct tests in this subset; behavior is indirectly covered by NetworkDB integration tests elsewhere.
