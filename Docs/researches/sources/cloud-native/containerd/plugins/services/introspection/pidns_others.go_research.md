# sources/cloud-native/containerd/plugins/services/introspection/pidns_others.go

## Purpose
Provides a non-Linux stub for PID namespace reporting.

## Important APIs, Types, And Functions
`statPIDNS` returns zero and nil.

## Control Flow
No inspection occurs; non-Linux `Local.Server` receives a zero PID namespace value.

## State And Persistence
No state.

## Dependencies And Integration Points
Compiled under `!linux` to preserve shared introspection code.

## Risks
Clients must treat zero PID namespace as unsupported rather than a real namespace inode.

## Test Signals
No direct tests.
