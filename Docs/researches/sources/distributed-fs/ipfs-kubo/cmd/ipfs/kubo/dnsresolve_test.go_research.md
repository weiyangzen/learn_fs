# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/dnsresolve_test.go

## Purpose
This test file verifies DNS multiaddr resolution used for API endpoint selection.

## Important APIs, Types, And Functions
`makeResolver` builds a mock multiaddr DNS resolver for `example.com`. Tests cover one result, multiple results, and no results by calling `resolveAddr`.

## Control Flow
Each test replaces package variable `dnsResolver`, resolves `/dns4/example.com/tcp/5001`, and asserts either the first `192.0.2.x` result or a `non-resolvable API endpoint` error.

## State And Persistence Behavior
It mutates the package-level resolver for the test process only.

## Dependencies And Integration Points
It integrates `cmd/ipfs/kubo/start.go` API address resolution, multiaddr DNS mock resolver, and multiaddr equality.

## Risks And Test Signals
Risks include global resolver mutation affecting parallel tests if added later. Signals are deterministic first-address selection and correct error on empty DNS results.
