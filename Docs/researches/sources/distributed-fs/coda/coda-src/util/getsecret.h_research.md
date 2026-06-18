# sources/distributed-fs/coda/coda-src/util/getsecret.h

## Purpose
Declares RPC2 secret hashing, token-file loading, and random key generation helpers.

## Important APIs, Types, And Functions
`HashSecret()`, `GetSecret()`, `GenerateSecret()`, and `struct secret_state` are the public contract. `secret_state` stores cached file mtime and key bytes.

## Control Flow
Callers pass a token file and persistent state to `GetSecret()`; the implementation refreshes the key only when the file's mtime changes.

## State And Persistence
The header defines caller-owned cache state. The token file is the durable secret source.

## Dependencies And Integration Points
Includes `rpc2/rpc2.h` and C system types. Used by RPC2-authenticated Coda daemons.

## Risks
Callers must initialize `secret_state` and serialize access if used across threads. The API exposes no key length negotiation beyond `RPC2_KEYSIZE`.

## Test Signals
Compile C and C++ callers, initialize zeroed state, and verify cached and refreshed token behavior.
