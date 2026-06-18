# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Auth.inc

## Purpose

`Auth.inc` implements the MGM authentication-plugin RPC bridge. It runs a ZeroMQ ROUTER/DEALER frontend/backend proxy, worker threads that receive protobuf requests from EOS auth plugins, validates HMACs, dispatches requests into normal `gOFS` XRootD/OFS methods, tracks open directory and file objects by UUID, serializes responses, and collects per-operation latency statistics.

## Important APIs, Types, and Functions

- `StartAuthWorkerThread()` is a pthread-style trampoline into `AuthWorkerThread()`.
- `AuthMasterThread()` binds the frontend TCP socket and inproc backend, then runs `zmq::proxy`.
- `ConnectToBackend()` creates/recreates a `ZMQ_REP` worker socket and retries connection to `inproc://authbackend`.
- `AuthWorkerThread()` is the main request loop and dispatcher for stat, fsctl, chmod, checksum, exists, mkdir, remdir, rem, rename, prepare, truncate, directory operations, and file open/stat/name/read/write/close.
- `ValidAuthRequest()` verifies request integrity by clearing the hmac field, serializing the protobuf, computing `SymKey::HmacSha256`, base64 encoding, and comparing with `CRYPTO_memcmp`.
- `AuthCollectInfo()`, `AuthComputeStats()`, `AuthUpdateAggregate()`, and `AuthPrintStatistics()` maintain and log latency aggregates.

## Control Flow

The master binds a client-facing ROUTER socket and a DEALER backend and proxies messages until ZeroMQ termination. Each worker connects to the backend and loops receiving a protobuf request. After parsing, it rejects invalid HMACs or switches on `RequestProto_OperationType`.

Stateless operations reconstruct `XrdOucErrInfo` and `XrdSecEntity` from protobuf helpers, call the matching `gOFS` method, and copy any binary result into the response. Stateful directory and file operations use UUID maps guarded by `mMutexDirs` or `mMutexFiles`. Open creates `XrdMgmOfsDirectory` or `XrdMgmOfsFile`, stores it on success, and deletes it on failure. Subsequent read/stat/name/write/close operations find the object, call the corresponding method, and close erases and deletes it.

After each request, the worker deletes reconstructed security entities, converts the error object if present, serializes `ResponseProto`, sends it nonblocking with retries, reconnects the socket on send failure, and records latency.

## State and Persistence Behavior

The bridge persists no namespace state directly but invokes operations that do. It owns runtime socket state, file/directory object maps, auth sample/aggregate maps, mutexes, and per-request reconstructed objects. File and directory handles can hold MGM-side state across multiple auth-plugin RPCs, so map cleanup on close and failure is critical. HMAC verification depends on the shared symmetric key store.

## Dependencies and Integration Points

Dependencies include ZeroMQ, protobuf auth messages, `auth_plugin/ProtoUtils.hh`, OpenSSL `CRYPTO_memcmp`, `XrdMgmOfsFile`, `XrdMgmOfsDirectory`, XRootD error/security types, and most `gOFS` command methods. It integrates external auth-plugin clients with the normal in-process MGM OFS implementation.

## Risks and Edge Cases

- HMAC validation must remain constant-time and must restore no trusted state from unauthenticated input.
- The large switch manually manages memory for reconstructed XRootD objects; missed deletes or double deletes are possible around FSctl/prepare/client handling.
- UUID map entries can leak if clients open and never close or if close requests are lost.
- `FILEWRITE` delegates to `XrdMgmOfsFile::write()`, which is unsupported for normal MGM files; clients must expect errors.
- Socket reconnect after failed send can drop an already executed request response, making idempotency of callers important.
- Directory `nextEntry()` uses `SFS_ERROR` for end-of-stream, which may be indistinguishable from some failures unless callers inspect context.

## Test Signals

Tests should cover HMAC mismatch rejection, each operation type serialization/deserialization, file and directory UUID lifecycle, duplicate open idempotence, missing UUID errors, send retry/reconnect behavior, ETERM shutdown, binary stat/read response sizes, memory cleanup for FSctl/prepare/client objects, and latency aggregation output after minute boundaries.
