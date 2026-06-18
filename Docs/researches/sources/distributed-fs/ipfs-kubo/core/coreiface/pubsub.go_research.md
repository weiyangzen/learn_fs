# sources/distributed-fs/ipfs-kubo/core/coreiface/pubsub.go

## Purpose
Defines CoreAPI pubsub subscription, message, and control interfaces.

## Important APIs, Types, and Functions
Declares `PubSubSubscription`, `PubSubMessage`, and `PubSubAPI` with `Ls`, `Peers`, `Publish`, and `Subscribe`.

## Control Flow and State
There is no implementation here. The contract exposes streaming subscription state via `Next`, message metadata such as sender/sequence/topic/signature/key, and topic-peer queries.

## Dependencies and Integration Points
Depends on context, pubsub options, and libp2p peer IDs. Implementations integrate with the node pubsub router.

## Risks and Test Signals
Risks include subscription cancellation, message authenticity fields, peer discovery semantics, and topic-local vs remote state. Tests cover basic two-node publish/subscribe, sender identity, topic peer listing, and topic listing.
