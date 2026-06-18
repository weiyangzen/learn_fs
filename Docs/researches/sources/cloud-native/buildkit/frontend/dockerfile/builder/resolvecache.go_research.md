# sources/cloud-native/buildkit/frontend/dockerfile/builder/resolvecache.go

Purpose: caches and deduplicates image config resolution calls made through the gateway client during Dockerfile build conversion.

Important APIs: `withResolveCache` embeds `client.Client`; `ResolveImageConfig` hashes `sourceresolver.Opt`, keys by `ref,optHash`, and uses `flightcontrol.CachedGroup`; `resolveResult` stores mutable ref, digest, and config bytes.

Control flow: every call enables `CacheError`, hashes the resolver option structurally, runs or joins the cached flight, delegates to the embedded client on cache miss, and returns stored values.

State and persistence: in-memory cached group state lives for the wrapper lifetime. Errors are cached intentionally, which can avoid duplicate failing resolver requests but may preserve transient failures inside one build.

Dependencies and integration: wraps the gateway client in `Build`; uses `hashstructure/v2`, BuildKit sourceresolver, flightcontrol, and OCI digest.

Risks and test signals: risks include hash instability for new option fields, cached transient errors, and memory growth in long-lived clients. Integration signal is reduced duplicate metadata loads and consistent behavior across repeated base image references.
