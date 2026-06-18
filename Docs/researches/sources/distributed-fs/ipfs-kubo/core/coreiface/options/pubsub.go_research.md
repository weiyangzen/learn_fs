# sources/distributed-fs/ipfs-kubo/core/coreiface/options/pubsub.go

## Purpose
Builds settings for pubsub peer listing and subscriptions.

## Important APIs, Types, and Functions
Defines `PubSubPeersSettings`, `PubSubSubscribeSettings`, option types, `PubSubPeersOptions`, `PubSubSubscribeOptions`, `PubSub` namespace, and methods `Topic` and `Discover`.

## Control Flow and State
Peer listing defaults to no topic filter. Subscribe defaults to discovery disabled. Options mutate simple settings fields consumed by PubSubAPI implementations.

## Dependencies and Integration Points
No external dependencies. Used by PubSubAPI tests for topic-scoped peers.

## Risks and Test Signals
Risks include empty topic semantics and discovery behavior varying by router. Tests cover publish/subscribe delivery, topic peer filtering, and local topic listing.
