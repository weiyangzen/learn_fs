# sources/distributed-fs/ipfs-kubo/core/corehttp/gateway_test.go

## Purpose
Tests selected gateway behavior with a mock namesystem and httptest server, focusing on version endpoint output and public gateway deserialized-response configuration inheritance.

## Important APIs, Types, and Functions
Defines `mockNamesys`, `newNodeWithMockNamesys`, `delegatedHandler`, `doWithoutRedirect`, `newTestServerAndNode`, `TestVersion`, and `TestDeserializedResponsesInheritance`.

## Control Flow and State
`mockNamesys.Resolve` follows chained `/ipns/` names with a depth counter and appends unresolved suffix segments. Test servers build real core nodes over an in-memory mock repo and mount `HostnameOption`, `GatewayOption`, and `VersionOption`. The inheritance test constructs configs directly and inspects `getGatewayConfig`.

## Dependencies and Integration Points
Depends on Kubo core node construction, coreapi, repo mocks, datastore, Boxo namesys/path, HTTP test utilities, and testify assertions. It validates gateway code through the same serve-option API used by daemon setup.

## Risks and Test Signals
The mock resolver is intentionally partial and does not test publishing. The tests signal regressions in `/version` formatting and `Gateway.PublicGateways[*].DeserializedResponses` defaulting, but leave path gateway fetching, hostname routing, CORS headers, NoFetch behavior, and metrics labeling to other coverage.
