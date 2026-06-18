# sources/distributed-fs/ipfs-kubo/client/rpc/request.go

## Purpose
This file defines the low-level HTTP RPC request object used by the request builder.

## Important APIs, Types, And Functions
`Request` stores context, API base URL, command, args, options, body, and headers. `NewRequest` normalizes a base URL and initializes default options `encoding=json` and `stream-channels=true`.

## Control Flow
Higher-level builders construct `Request` objects before sending them in `response.go`.

## State And Persistence Behavior
State is per-request only; no persistence.

## Dependencies And Integration Points
It integrates with all RPC API files through `requestBuilder.Send`.

## Risks And Test Signals
Risks include treating non-`http` URL prefixes as plain HTTP and relying on later URL encoding. Signals are all RPC requests reaching `/api/v0/<command>` with expected defaults.
