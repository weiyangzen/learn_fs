# Research: sources/distributed-fs/ipfs-kubo/config/routing.go

Purpose: Defines routing mode, delegated router configuration, advanced custom router composition, method validation, environment-derived filters, and HTTP-provider detection.

Important APIs/types/functions: Routing defaults and env keys; `Routing`, `Router`, `Routers`, `Methods`, `RouterParser`, router types, DHT modes, method names/list, `HTTPRouterParams.FillDefaults`, `DHTRouterParams`, `ComposableRouterParams`, `ConfigRouter`, `Method`, `getEnvOrDefault`, `(*Config).HasHTTPProviderConfigured`, and `routerSupportsHTTPProviding`.

Control flow, state, and persistence: `Methods.Check` requires all supported methods and rejects unknown ones. `RouterParser.UnmarshalJSON` first decodes the router type then decodes `Parameters` into type-specific structs for HTTP, DHT, sequential, or parallel routers. HTTP params fill default batch/concurrency values when zero. `getEnvOrDefault` accepts comma/space-separated env overrides. HTTP-provider detection walks custom router composition recursively from the provide method.

Dependencies and integration points: Integrates config with routing subsystem, delegated routing HTTP clients, DHT mode setup, autoconf delegated endpoint expansion, and provide capability decisions.

Risks and test signals: Recursive router detection can loop indefinitely on cyclic custom router configs. Unknown router types leave parameters as generic nil/empty without explicit validation here. Env-based defaults are process-global and can change tests. `routing_test.go` covers typed JSON parameter round-trip and method completeness.
