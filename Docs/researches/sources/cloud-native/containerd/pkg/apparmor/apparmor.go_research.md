# sources/cloud-native/containerd/pkg/apparmor/apparmor.go

## Purpose
Exposes a portable public `HostSupports` helper for AppArmor availability.

## Important APIs, Types, And Functions
`HostSupports` delegates to platform-specific `hostSupports`.

## Control Flow
On Linux it checks kernel/AppArmor/parser/container state; on non-Linux it returns false.

## State And Persistence
State is handled by platform implementations, including Linux `sync.Once` caching.

## Dependencies And Integration Points
The package is used by runtime/security profile code deciding whether AppArmor profiles can be used.

## Risks
This wrapper hides platform-specific caching and environment assumptions. Callers should treat false as "do not use AppArmor".

## Test Signals
No direct tests in this subset.
