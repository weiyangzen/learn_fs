# sources/distributed-fs/ipfs-kubo/routing/wrapper.go

Purpose: adapts delegated HTTP routing client components into libp2p routing interfaces.

Important APIs and control flow: `ProvideManyRouter` combines routing helper batch providing with `routing.Routing`. `httpRoutingWrapper` embeds content routing, peer routing, value store, and provide-many interfaces. `Bootstrap` is a no-op because HTTP delegated routers do not need peer bootstrap.

State and persistence: no state beyond embedded router implementations.

Dependencies and integration: returned by `httpRoutingFromConfig`; lets HTTP delegated routing satisfy `routing.Routing` and optional batch provide interfaces.

Risks and test signals: compile-time assertions check interface conformance. Because methods are supplied through embedding, missing embedded components would result in nil-interface panics if constructed incorrectly. Parser tests indirectly create wrappers.
