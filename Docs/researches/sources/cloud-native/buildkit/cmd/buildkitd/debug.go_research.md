# Research: sources/cloud-native/buildkit/cmd/buildkitd/debug.go

Purpose: registers and implements buildkitd HTTP debug endpoints for expvar, pprof, net/trace, Prometheus metrics, GC triggering, in-flight trace recording, and cache-debug inspection. It is enabled only when `debugAddress` is configured.

Important APIs and flow: `setupDebugHandlers` mounts `/debug/vars`, pprof, `/debug/requests`, `/debug/events`, cache endpoints, `/debug/gc`, `/metrics`, and flight recorder routes, then listens through the same listener abstraction used by the daemon. Cache endpoints load plaintext digest debug records, lookup individual digests, parse cache import JSON into temporary cache key storage, and render cache-store records as text or JSON. `debugCacheStore` walks solver cache records, resolves related digests/selectors through the cachedigest DB, and attaches readable debug frames.

State and persistence: reads and sometimes triggers runtime state. `/debug/gc` forces Go GC. Cache debug reads `cachedigest` and solver cache stores; `/debug/cache/load` parses request bodies but does not persist them to daemon state. `cacheStoreForDebug` is set during controller creation.

Dependencies and risks: depends on HTTP, pprof, expvar, Prometheus, cachedigest, cache import parser, cache store internals, and listener security. Debug address is opt-in, but endpoints expose sensitive cache/build internals and should be bound carefully. There are no direct tests in this subset.
