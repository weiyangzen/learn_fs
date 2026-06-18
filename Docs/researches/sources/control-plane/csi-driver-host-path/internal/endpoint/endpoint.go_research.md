# sources/control-plane/csi-driver-host-path/internal/endpoint/endpoint.go

## Purpose
This package normalizes CSI endpoint strings and creates listeners for Unix or TCP endpoints. It is shared by the gRPC server and the bidirectional proxy.

## Important APIs, Types, And Functions
`Parse(ep string)` returns protocol, address, and error. It accepts explicit `unix://` and `tcp://` prefixes case-insensitively, rejects empty post-prefix addresses, and treats all other strings as Unix socket paths. `Listen(endpoint string)` calls `Parse`, removes an existing Unix socket path before listening, returns a `net.Listener`, and returns a cleanup callback that removes Unix socket files on shutdown.

## Control Flow
Callers parse or listen in one step. For Unix endpoints, cleanup starts before `net.Listen` by deleting any stale socket path and ends by deleting the socket file again. TCP endpoints receive a no-op cleanup.

## State, Persistence, And Dependencies
The only persistent state is the Unix socket path on disk. Dependencies are Go `net`, `os`, `strings`, and `fmt`.

## Integration Points
`pkg/hostpath/server.go` uses it to serve CSI gRPC. `internal/proxy/proxy.go` uses it to open both ends of a socket-pair proxy. Endpoint behavior must match command-line `--endpoint` and `--proxy-endpoint` style values.

## Risks
Deleting the Unix socket path before listening is correct for stale sockets but dangerous if the configured path points at an unintended file. Parent directories are not created here. Unsupported schemes without `://` are silently treated as Unix paths, which is permissive but can hide typos.

## Test Signals
Tests should cover explicit Unix and TCP endpoints, bare Unix paths, empty `unix://`, cleanup removing socket files, stale socket replacement, and failure when parent directories are missing.
