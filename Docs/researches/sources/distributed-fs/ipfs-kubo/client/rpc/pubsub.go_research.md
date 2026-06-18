# sources/distributed-fs/ipfs-kubo/client/rpc/pubsub.go

## Purpose
This file implements pubsub topic listing, peer listing, publishing, and subscriptions over HTTP RPC.

## Important APIs, Types, And Functions
`PubsubAPI` exposes `Ls`, `Peers`, `Publish`, and `Subscribe`. `pubsubSub` implements subscription lifecycle. `pubsubMessage` implements `iface.PubSubMessage`. `toMultibase` encodes bytes as URL-safe base64 multibase.

## Control Flow
Topics and messages are encoded/decoded using multibase because RPC transports topic/data fields as text. `Subscribe` opens `pubsub/sub`, starts a decoder goroutine feeding a message channel, and `Next` decodes peer ID, data, sequence, and topics for callers.

## State And Persistence Behavior
Publish sends data into the node's pubsub system; subscribe holds an open HTTP response until closed or canceled.

## Dependencies And Integration Points
It integrates Kubo pubsub commands, libp2p peer IDs, coreiface pubsub APIs, multibase encoding, and streaming JSON.

## Risks And Test Signals
Risks include subscription goroutine leaks if `Close` is not called, multibase decode failures, and close-once handling via nil `done`. Signals are CoreAPI pubsub tests for topic/peer discovery and message delivery.
