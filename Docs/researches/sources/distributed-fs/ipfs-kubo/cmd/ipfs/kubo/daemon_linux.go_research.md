# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_linux.go

## Purpose
This Linux-only file sends systemd readiness and stopping notifications for the daemon.

## Important APIs, Types, And Functions
`notifyReady` calls `daemon.SdNotifyReady`; `notifyStopping` calls `daemon.SdNotifyStopping`.

## Control Flow
`daemon.go` calls these helpers after daemon readiness and when shutdown begins.

## State And Persistence Behavior
It mutates systemd service state through the notification socket when available.

## Dependencies And Integration Points
It integrates `github.com/coreos/go-systemd/v22/daemon` and the Linux build tag.

## Risks And Test Signals
Risks are silent ignored notification errors and environment/socket absence. Signals are systemd units observing READY=1 and STOPPING=1.
