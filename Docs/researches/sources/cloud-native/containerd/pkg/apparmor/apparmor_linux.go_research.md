# sources/cloud-native/containerd/pkg/apparmor/apparmor_linux.go

## Purpose
Detects AppArmor host support on Linux.

## Important APIs, Types, And Functions
`hostSupports` uses package globals `appArmorSupported` and `checkAppArmor sync.Once`.

## Control Flow
The first call checks `/sys/kernel/security/apparmor`, ensures environment variable `container` is empty to avoid docker-in-docker, checks `/sbin/apparmor_parser`, then reads `/sys/module/apparmor/parameters/enabled` and requires leading `Y`.

## State And Persistence
Detection result is cached in memory for the process.

## Dependencies And Integration Points
Uses `os` filesystem and environment checks. Derived from runc/libcontainer AppArmor detection with extra parser and container checks.

## Risks
Hard-coded parser path may miss distributions with a different path. The one-time cache can be stale in tests or after environment changes.

## Test Signals
No direct tests in this subset.
