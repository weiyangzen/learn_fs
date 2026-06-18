# sources/distributed-fs/ipfs-kubo/core/coreapi/pubsub.go

Purpose: implements experimental CoreAPI pubsub topic listing, peer listing, publish, subscribe, and message wrappers.

Important APIs/types/functions: `PubSubAPI`, `pubSubSubscription`, `pubSubMessage`, methods `Ls`, `Peers`, `Publish`, `Subscribe`, `checkNode`, subscription `Close`/`Next`, and message accessors.

Control flow: every operation calls `checkNode`, which requires pubsub enabled and online mode. `Ls` returns topics, `Peers` parses options and lists peers for optional topic, `Publish` sends data, `Subscribe` validates options and creates a libp2p pubsub subscription. `Next` blocks on subscription next with context.

State and persistence behavior: no repo persistence. Publish sends network pubsub messages; subscribe mutates in-memory pubsub subscription state until canceled.

Dependencies and integration points: wraps libp2p pubsub, CoreAPI online checks, routing presence, and coreiface pubsub abstractions.

Risks: feature-gated by daemon pubsub enablement; otherwise commands return an explicit experimental feature error. Deprecated libp2p pubsub methods are used with nolint markers. Subscription option discovery is parsed but no-op because discovery is handled by pubsub.

Test signals: shared CoreAPI tests can cover pubsub when `NodeProvider` enables `"pubsub": true`.
