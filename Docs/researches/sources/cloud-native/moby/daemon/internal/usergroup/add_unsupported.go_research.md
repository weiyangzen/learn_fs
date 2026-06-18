# sources/cloud-native/moby/daemon/internal/usergroup/add_unsupported.go

## Purpose
Provides the non-Linux fallback for user namespace remap account creation.

## Important APIs, Types, And Functions
`AddNamespaceRangesUser(name)` returns `-1, -1` and an error stating that adding users or groups is unsupported on this OS.

## Control Flow
No work is attempted on unsupported platforms.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Selected by the `!linux` build tag to satisfy call sites that compile across platforms.

## Risks And Test Signals
The error string starts with a capitalized "No", which may matter if callers or tests compare exact text. There are no tests in this subset for unsupported platforms.
