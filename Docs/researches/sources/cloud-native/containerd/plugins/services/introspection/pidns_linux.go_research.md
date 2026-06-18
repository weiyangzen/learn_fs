# sources/cloud-native/containerd/plugins/services/introspection/pidns_linux.go

## Purpose
Reports the Linux PID namespace inode for the containerd process.

## Important APIs, Types, And Functions
`statPIDNS` stats `/proc/<pid>/ns/pid`, asserts `*syscall.Stat_t`, and returns inode number.

## Control Flow
Called by `Local.Server` on Linux. It reads procfs metadata and returns the namespace inode or an error.

## State And Persistence
No persistence; reads procfs.

## Dependencies And Integration Points
Linux-only; used by introspection server information.

## Risks
Fails if procfs is unavailable or stat sys type is unexpected. Errors propagate through the server info RPC.

## Test Signals
No direct tests.
