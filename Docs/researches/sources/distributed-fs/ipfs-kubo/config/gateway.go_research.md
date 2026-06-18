# Research: sources/distributed-fs/ipfs-kubo/config/gateway.go

Purpose: Defines HTTP gateway behavior, including public gateway overrides, response modes, limits, and diagnostic links.

Important APIs/types/functions: Constants expose defaults from Boxo gateway and Kubo. `GatewaySpec` configures per-host paths, subdomain mode, DNSLink behavior, inline DNSLink, and deserialized responses. `Gateway` configures headers, root redirect, fetch behavior, DNSLink, response serialization, codec conversion, HTML errors, public gateways, routing API exposure, timeouts, concurrency, range limits, and diagnostic service URL.

Control flow, state, and persistence: No functions. Values persist in repo config and are interpreted by the gateway server. Several fields use `Flag`, `OptionalDuration`, `OptionalInteger`, or `OptionalBytes` so omitted values can defer to defaults.

Dependencies and integration points: Consumed by core HTTP gateway setup and `commands.Context.GetAPI` via `Gateway.NoFetch`. Public gateway dynamic keys are handled by config key validation.

Risks and test signals: Gateway behavior is security-sensitive: path/subdomain mixing, DNSLink, codec conversion, routing API exposure, and fetch/no-fetch all affect origin isolation and retrieval. Direct tests are not in this subset; `config_test.go` checks validation of dynamic `Gateway.PublicGateways.*.Paths`.
