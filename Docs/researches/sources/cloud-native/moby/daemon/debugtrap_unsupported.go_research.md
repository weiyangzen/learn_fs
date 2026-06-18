# sources/cloud-native/moby/daemon/debugtrap_unsupported.go

## Purpose
Provides a no-op stack dump trap for build targets that are neither Unix-like nor Windows.

## Important APIs, Types, And Functions
- `setupDumpStackTrap` accepts the root path and does nothing.

## Control Flow
No control flow beyond returning immediately.

## State And Persistence
No signal handlers, events, or dump files are created.

## Dependencies And Integration Points
Selected by build tags for unsupported targets to satisfy generic daemon startup symbols.

## Risks And Edge Cases
Operators on unsupported platforms do not get a stack-dump trigger, but this is consistent with the platform support boundary.

## Test Signals
Compilation is the relevant signal.
