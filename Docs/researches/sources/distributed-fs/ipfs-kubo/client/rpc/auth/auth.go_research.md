# sources/distributed-fs/ipfs-kubo/client/rpc/auth/auth.go

## Purpose
This package provides an HTTP transport wrapper that injects an Authorization header into RPC requests.

## Important APIs, Types, And Functions
`AuthorizedRoundTripper` stores an authorization string and base `http.RoundTripper`. `NewAuthorizedRoundTripper` defaults a nil base to `http.DefaultTransport`. `RoundTrip` sets `Authorization` then delegates.

## Control Flow
The wrapper is constructed by CLI startup when `--api-auth` is provided and used by the HTTP client for remote command execution.

## State And Persistence Behavior
State is the in-memory authorization string. No persistence occurs.

## Dependencies And Integration Points
It integrates with `cmd/ipfs/kubo/start.go`, Kubo `API.Authorizations`, and standard `net/http`.

## Risks And Test Signals
Risks include mutating the caller's request header in place and overwriting existing Authorization values. Signals are authenticated API calls succeeding when the header is required.
