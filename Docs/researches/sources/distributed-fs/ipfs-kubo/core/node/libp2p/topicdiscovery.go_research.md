# sources/distributed-fs/ipfs-kubo/core/node/libp2p/topicdiscovery.go

Purpose: creates routing-backed topic discovery with exponential backoff. Important API is `TopicDiscovery`.

Control flow: it builds a `routingdiscovery.RoutingDiscovery` from content routing, then wraps it in `backoff.NewBackoffDiscovery` with 60-second minimum, one-hour maximum, full jitter, factor 5, and a random source.

State and persistence: runtime-only backoff state.

Dependencies/integration: libp2p discovery/backoff/routing and content routing. Provided when pubsub or IPNS-over-pubsub is enabled.

Risks: random seed uses `rand.Int63` from the package-level source; discovery delays affect pubsub mesh formation. No direct tests.
