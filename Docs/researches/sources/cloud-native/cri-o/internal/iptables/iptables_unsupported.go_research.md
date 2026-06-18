# sources/cloud-native/cri-o/internal/iptables/iptables_unsupported.go

## Purpose
Provides a non-Linux implementation of manual iptables lock acquisition that always reports unsupported platform.

## Important APIs, Types, And Functions
- `grabIptablesLocks(lockfilePath14x, lockfilePath16x string) (iptablesLocker, error)` returns nil plus a `runtime.GOOS` error.

## Control Flow
Build-tagged with `//go:build !linux`. No lock paths are used.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Keeps the shared iptables runner compileable off Linux. If restore wait flags are unavailable on non-Linux, restore will fail through this path.

## Risks And Edge Cases
The broader iptables runner can still be constructed off Linux, but actual restore locking is unsupported. This matches the platform reality for iptables management.

## Test Signals
No direct tests in this subset; build-tag compilation is the signal.
