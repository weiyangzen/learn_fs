<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/pool.go -->
# sources/cloud-native/buildkit/util/resolver/pool.go

Purpose: provides a shared resolver/auth-handler pool with local image-store fallback modes and session-aware resolver cloning.

Important APIs and types: `DefaultPool`, `Pool`, `NewPool`, `Clear`, `GetResolver`, `Resolver`, `ScopeType`, `ResolveMode`, `ParseImageResolveMode`, `WithSession`, `WithImageStore`, `ResolveLocal`, `Resolve`, and `Fetcher`.

Control flow: `GetResolver` normalizes the reference name, builds a cache key from image name and scope, includes session IDs for push scopes, creates or reuses an auth handler namespace, and returns a new resolver wrapper. `Pool.gc` runs every five minutes, removing stale auth fetchers that have not been used for ten minutes or whose sessions are gone. `Resolver.HostsFunc` flightcontrols registry host lookup and attaches a fresh authorizer to copied host entries. Resolve modes prefer remote, force remote, or prefer local image store.

State and persistence: process-local pool map keyed by scope/name, auth fetcher caches, host config caches, image-store pointer, and resolve mode. No disk persistence.

Dependencies and integration: uses containerd docker resolver, images store, BuildKit sessions, protobuf resolve mode constants, BuildKit logging, and `authorizer.go`.

Risks: pull-only auth handlers are intentionally shared across sessions; push handlers include session IDs to avoid leaking write-capable credentials. `Fetcher` calls `Resolve` first when the auth counter is zero to populate auth challenge state. GC runs forever via `time.AfterFunc`.

Test signals: no direct pool tests in this subset; resolver tests focus on mirror host parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/pool.go -->
