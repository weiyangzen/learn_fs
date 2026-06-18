# sources/cloud-native/moby/internal/testutil/daemon/daemon_unix.go

## Purpose
Unix-specific daemon helpers for root cleanup, diagnostic/reload signals, and process group setup.

## Important APIs, Types, And Functions
- `cleanupMount` unmounts the daemon root using `moby/sys/mount.Unmount`.
- `SignalDaemonDump` sends `SIGQUIT` to trigger daemon stack dump.
- `signalDaemonReload` sends `SIGHUP` for config reload.
- `setsid` ensures rootless sudo-launched daemon commands run in a new session.

## Control Flow
Functions directly call OS signal or mount APIs and either ignore/log errors depending on caller. `setsid` initializes `SysProcAttr` if needed before setting `Setsid`.

## State And Persistence
`cleanupMount` can alter mount state for daemon root. Signal helpers mutate daemon process state by causing dump/reload behavior.

## Dependencies And Integration Points
Build tag `!windows`; uses Unix signals, `moby/sys/mount`, and `golang.org/x/sys/unix`. Called by `Daemon.Cleanup`, `DumpStackAndQuit`, and `ReloadConfig`.

## Risks And Edge Cases
Unmount failure is logged but not fatal. Signals require a live process and proper permissions. `setsid` matters for rootless signal propagation through sudo.

## Test Signals
Expected signals are successful stack dumps on SIGQUIT, reload events after SIGHUP, and best-effort daemon root unmount during cleanup.
