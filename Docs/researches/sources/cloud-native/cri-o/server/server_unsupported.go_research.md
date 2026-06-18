# sources/cloud-native/cri-o/server/server_unsupported.go

## Purpose
Non-Linux fallback for seccomp notifier startup.

## Important APIs, Types, And Functions
`(*Server).startSeccompNotifierWatcher(ctx)` returns nil on builds where the `!linux` tag is selected.

## Control Flow
No operation. The context is accepted only to keep the method signature shared across platforms.

## State And Persistence
No state changes and no persistence.

## Dependencies And Integration Points
Allows the server package to compile on non-Linux targets while Linux behavior lives in `server_linux.go`.

## Risks And Test Signals
Feature absence is silent. Tests on non-Linux should assert that seccomp-notifier-dependent features are gated elsewhere.
