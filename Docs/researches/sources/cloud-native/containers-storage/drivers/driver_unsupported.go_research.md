# sources/cloud-native/containers-storage/drivers/driver_unsupported.go

## Purpose
`driver_unsupported.go` provides fallback driver priority and filesystem magic behavior for platforms not covered by Linux, FreeBSD, Solaris, or Darwin.

## Important APIs, Types, And Functions
`Priority` contains `unsupported`. `GetFSMagic` returns `FsMagicUnsupported`.

## Control Flow
Automatic selection will try the unsupported driver name, and platform-specific filesystem checks are unavailable.

## State And Persistence
No mutable state is kept.

## Dependencies And Integration Points
It satisfies symbols needed by `driver.go` on miscellaneous platforms.

## Risks
Only drivers registered for such platforms can work; most storage backends will report unsupported.

## Test Signals
Build-only signal.
