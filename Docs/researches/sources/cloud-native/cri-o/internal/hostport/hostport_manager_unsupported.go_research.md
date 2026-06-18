# sources/cloud-native/cri-o/internal/hostport/hostport_manager_unsupported.go

## Purpose
Provides a non-Linux stub for UDP conntrack cleanup used by hostport management.

## Important APIs, Types, And Functions
- `deleteConntrackEntriesForDstPort(port uint16, protocol uint8, family netlink.InetFamily) error` always returns an unsupported-platform error with `runtime.GOOS`.

## Control Flow
Build-tagged with `//go:build !linux`. It does not inspect arguments beyond formatting the error.

## State And Persistence
No state is changed. No conntrack entries are deleted.

## Dependencies And Integration Points
Keeps hostport meta manager buildable off Linux while preserving the same function signature. Imports `netlink.InetFamily` for signature compatibility.

## Risks And Edge Cases
If hostport Add calls UDP conntrack cleanup on non-Linux, errors are logged by the meta manager but not returned. This is acceptable for best-effort cleanup but means UDP stale state is not cleared off Linux.

## Test Signals
No direct tests in this subset; compile-time build tag coverage is the main signal.
