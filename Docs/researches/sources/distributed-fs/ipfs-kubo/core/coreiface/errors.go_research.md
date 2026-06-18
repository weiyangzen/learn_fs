# sources/distributed-fs/ipfs-kubo/core/coreiface/errors.go

## Purpose
Centralizes common CoreAPI sentinel errors.

## Important APIs, Types, and Functions
Defines `ErrIsDir`, `ErrNotFile`, `ErrOffline`, and `ErrNotSupported`.

## Control Flow and State
There is no control flow or persistence. These values are shared error identities for API implementations and wrappers.

## Dependencies and Integration Points
Depends only on Go `errors`. Gateway code maps `ErrOffline` to service-unavailable behavior, and API implementations use these sentinels for mode/type failures.

## Risks and Test Signals
Risks are string/API compatibility and wrapping behavior. Tests should use `errors.Is` where possible and verify offline-mode callers surface `ErrOffline` consistently.
