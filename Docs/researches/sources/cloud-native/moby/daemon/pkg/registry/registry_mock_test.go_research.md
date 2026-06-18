<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry_mock_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/registry_mock_test.go

## Purpose
Defines reusable HTTP/HTTPS mock registry servers and helpers for registry package tests.

## Important APIs, Types, And Functions
Global `testHTTPServer` and `testHTTPSServer` are initialized in `init`. Helpers include `handlerAccessLog`, `makeURL`, `makeHTTPSURL`, `makeIndex`, `makeHTTPSIndex`, `makePublicIndex`, `writeHeaders`, `writeResponse`, `handlerGetPing`, `handlerSearch`, and `TestPing`.

## Control Flow
`init` registers v1 ping/search and v2 version handlers on an HTTP mux, then starts test servers. Handlers validate GET methods and return JSON. `TestPing` sends a GET to `/v1/_ping` and checks status/header.

## State, Dependencies, And Integration Points
The servers are process-global test state. They support registry tests needing endpoints without external network access and integrate with `registry.IndexInfo` construction helpers.

## Risks And Test Signals
Global servers live for the test process and may affect parallel tests if handlers mutate state in the future. The mock covers basic success responses, not auth challenges or registry error bodies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry_mock_test.go -->
