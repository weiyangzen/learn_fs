# sources/cloud-native/containerd/plugins/server/ttrpc/plugin.go

## Purpose
Registers the local TTRPC server endpoint and wires TTRPC-capable services.

## Important APIs, Types, And Functions
`config` stores endpoint address/UID/GID and implements getter/setter. `server.Start` opens a local listener and serves TTRPC. Init creates `newTTRPCServer`, registers services implementing `RegisterTTRPC`, and returns a server.

## Control Flow
Startup skips on empty address, creates platform-specific TTRPC server options, iterates all initialized TTRPC and gRPC plugin instances, calls `RegisterTTRPC` on supported services, requires at least one service, and returns the server wrapper. Start opens a local listener and serves with `context.WithoutCancel(ctx)`.

## State And Persistence
No persistence. Owns the TTRPC server and listener.

## Dependencies And Integration Points
Requires TTRPC and gRPC plugin types. Uses `pkg/sys.GetLocalListener`, `internal.Serve`, and platform-specific server constructors. Events service registers TTRPC forwarding here.

## Risks
Only services that implement `RegisterTTRPC` are exposed. Failed service plugins are skipped. The server uses a context without cancellation for serving, relying on server close/listener close for shutdown.

## Test Signals
No direct tests.
