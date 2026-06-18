# sources/cloud-native/containerd/plugins/server/ttrpc/server_other.go

## Purpose
Builds a default TTRPC server on platforms that are not Linux, Windows, or Solaris.

## Important APIs, Types, And Functions
`newTTRPCServer` returns `ttrpc.NewServer()` with no extra options.

## Control Flow
Called by shared TTRPC plugin initialization.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Compiled under `!linux && !windows && !solaris`.

## Risks
No OTEL interceptor or same-user handshaker is installed on these platforms.

## Test Signals
No direct tests.
