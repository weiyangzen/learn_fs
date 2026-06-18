# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/pubsub.go

## Purpose
Conformance tests for basic PubSubAPI messaging and topic peer discovery.

## Important APIs, Types, and Functions
Defines `TestPubSub` and `TestBasicPubSub`.

## Control Flow and State
Creates a two-node online swarm, subscribes node 0 to `testch`, repeatedly publishes from node 1 until a message is received, checks data and sender identity, verifies topic-scoped peers, and checks topic listings on subscribed versus publishing-only nodes.

## Dependencies and Integration Points
Depends on PubSubAPI, KeyAPI self identity, pubsub topic options, and multi-node provider setup.

## Risks and Test Signals
Signals cover end-to-end publish/subscribe, sender metadata, and peer/topic queries. The publish retry loop is timing-sensitive and does not cover discovery-enabled subscribe, signatures, or sequence fields.
