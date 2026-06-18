# sources/distributed-fs/eos/unit_tests/mgm/RoutingTests.cc

## Purpose
Tests MGM path routing and route endpoint parsing. It validates route registration/removal, protocol-specific rerouting ports, offline endpoint stall behavior, and path normalization for special `.`/`..` components.

## Important APIs, types, and functions
The tests use `RouteEndpoint::ParseFromString`, endpoint equality, `PathRouting::Add`, `Remove`, `Clear`, `Reroute`, `GetListing`, and status values `NOROUTING`, `REROUTE`, and `STALL`.

## Control flow
Construction tests reject malformed endpoint strings and duplicate route additions. Functionality tests add routes for `/eos/dirN/`, check no-route cases, reroute HTTP/HTTPS to the third endpoint field, reroute XRootD to the endpoint service port, handle multi-endpoint offline stall, then prefer an online master endpoint. Special-path tests assert longest-prefix routing after normalization of trailing `.`, embedded `.`, and `..`.

## State and persistence
State is an in-memory route table and endpoint online/master flags. Production route tables may be configured dynamically and affect client redirection.

## Dependencies and integration points
Depends on Google Test, route endpoint, path routing, and `VirtualIdentity` protocol fields.

## Risks and test signals
The tests protect parsing and normalization. Risks include endpoint health races, async update intervals disabled in tests, path traversal normalization surprises, and route ordering for overlapping prefixes.
