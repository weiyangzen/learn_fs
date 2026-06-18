# sources/distributed-fs/coda/coda-src/util/getsecret.cc

## Purpose
Implements helpers for turning token files or random bytes into RPC2 encryption keys.

## Important APIs, Types, And Functions
`HashSecret()` MD5-hashes arbitrary bytes into an `RPC2_EncryptionKey`. `GetSecret()` reads a token file, caches the derived key in `secret_state`, and refreshes on mtime changes. `GenerateSecret()` fills a key with `rpc2_NextRandom()` bytes.

## Control Flow
`GetSecret()` stats the file, compares `statbuf.st_mtime` with cached `state->mtime`, reads up to 512 bytes when stale, hashes the bytes, and updates the cached mtime unless the file was modified in the current second. It then copies the cached key to the caller.

## State And Persistence
Persistent input is the token file. In-process cache state is `secret_state::mtime` and `secret_state::key`. No lock protects shared state.

## Dependencies And Integration Points
Depends on RPC2 key types/randomness, Coda MD5 wrappers, logging through `LogMsg`/`SrvDebugLevel`, and file I/O. `updatesrv` uses it for update-token authentication.

## Risks
MD5 is legacy cryptography; this code derives fixed-size RPC2 keys rather than modern password hashes. Reads are capped at 512 bytes. Shared `secret_state` use across concurrent workers would need external synchronization. Mtime granularity can delay cache refresh by design.

## Test Signals
Read missing/unreadable token files, token changes across same-second and later mtimes, binary token contents, exact 512-byte files, generated secrets, and authentication success/failure in RPC2 users.
