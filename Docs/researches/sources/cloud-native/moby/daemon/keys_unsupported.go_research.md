# sources/cloud-native/moby/daemon/keys_unsupported.go

## Purpose
Provides the non-Linux no-op implementation of daemon key limit adjustment.

## Important APIs, Types, And Functions
`modifyRootKeyLimit()` returns nil without doing work.

## Control Flow
There is no conditional behavior.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Selected by `!linux` so daemon startup can call the same function on all platforms.

## Risks And Test Signals
Unsupported platforms silently skip key-limit configuration, which is appropriate because the Linux procfs key sysctls do not exist. No tests are included.
