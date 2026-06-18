<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl.go

## Purpose
Abstracts BeeGFS 7 and BeeGFS 8 command-line tooling for directory creation, stat, and stripe pattern operations.

## Important APIs, Types, And Functions
`beegfsCtlExecutorInterface` defines the driver-facing CTL operations. `beegfsCtlDispatcher` detects v7/v8 per volume. `beegfsCtlExecutorV8` wraps `beegfs`; `beegfsCtlExecutorV7` wraps `beegfs-ctl`. Shared helpers include `newBeeGFSCtlExecutor`, `detectCTLVersion`, `execBeeGFSCmd`, `constructSetPatternForVolumeArgs`, `constructCreateDirForVolumeArgs`, and typed ctl errors.

## Control Flow
Startup checks whether either v7 or v8 CTL can run. Each operation re-detects the target file system version by trying v8 `node list` then v7 `--listnodes`. Directory creation stats first, builds parent directories from root to target, tolerates already-exists errors, and wraps failures with volume context.

## State And Persistence
No internal persistent state. External side effects are BeeGFS directory creation and stripe pattern changes. V8 commands pass mgmtd/auth/TLS flags from volume config; v7 commands use generated client config files.

## Dependencies And Integration Points
Depends on `os/exec`, BeeGFS CLI binaries, command output strings, connAuth/TLS files written near mount dirs, and controller/node server code that calls these operations.

## Risks And Edge Cases
Error classification is string-matched against stdout/stderr and can drift with CLI versions. Version detection on every command adds overhead but supports upgrades without restart. Special permission bits are intentionally dropped from CTL create args and must be handled elsewhere if needed.

## Test Signals
Unit tests cover v7/v8 set-pattern args, create-directory args including uid/gid/mode, and typed error wrapping. Actual CLI execution is not unit-tested.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl.go -->
