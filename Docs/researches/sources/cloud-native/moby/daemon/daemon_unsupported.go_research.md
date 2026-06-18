# sources/cloud-native/moby/daemon/daemon_unsupported.go

## Purpose
Provides stub daemon platform hooks for unsupported build targets outside Linux, FreeBSD, and Windows so the package can compile with minimal behavior.

## Important APIs, Types, And Functions
- `checkSystem` returns nil.
- `setupResolvConf` is a no-op.
- `getSysInfo` returns a generic `sysinfo.New()`.
- `runInNetNS` executes the callback directly.

## Control Flow
There is no platform setup logic; each function either returns a neutral value or calls the provided callback.

## State And Persistence
No persistent state is created or mutated.

## Dependencies And Integration Points
Build tags select this file only for unsupported platforms. It satisfies symbols required by generic daemon code.

## Risks And Edge Cases
Returning nil from `checkSystem` can hide missing real platform support if an unsupported target is accidentally built. Generic sysinfo may not describe platform-specific capabilities.

## Test Signals
The main signal is package compilation on unsupported targets; there are no direct unit tests.
