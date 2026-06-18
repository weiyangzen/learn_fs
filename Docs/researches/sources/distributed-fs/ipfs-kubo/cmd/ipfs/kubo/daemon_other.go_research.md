# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_other.go

## Purpose
This non-Linux file provides no-op daemon notification functions.

## Important APIs, Types, And Functions
`notifyReady` and `notifyStopping` are empty functions behind the `!linux` build tag.

## Control Flow
The same calls in `daemon.go` compile on non-Linux platforms without systemd behavior.

## State And Persistence Behavior
No state is changed.

## Dependencies And Integration Points
It integrates Go build tags with cross-platform daemon startup.

## Risks And Test Signals
Risk is simply that non-Linux supervisors get no readiness notification. Signal is successful non-Linux compilation.
