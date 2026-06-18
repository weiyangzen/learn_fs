# Research: sources/distributed-fs/ipfs-kubo/config/routing_test.go

Purpose: Tests routing custom-router JSON parameter decoding and method validation.

Important APIs/types/functions: `TestRouterParameters` builds a custom routing config with DHT, parallel, and sequential routers and checks decoded parameter concrete types. `TestMethods` validates complete and missing method maps.

Control flow, state, and persistence: Pure JSON marshal/unmarshal and in-memory validation. It uses durations and optional duration fields inside composable routers.

Dependencies and integration points: Uses `testify/require`. Protects `RouterParser.UnmarshalJSON` and `Methods.Check`, both required for advanced custom routing configs.

Risks and test signals: Does not test HTTP router params, unknown methods, unsupported router types, cyclic router graphs, or environment filter parsing. It is strong for preserving typed parameters across JSON round trips.
