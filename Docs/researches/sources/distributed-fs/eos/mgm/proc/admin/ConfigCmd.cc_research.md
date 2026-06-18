# Research: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.cc

## Purpose

`ConfigCmd.cc` implements the protobuf admin command for listing, dumping, resetting, saving, loading, and tailing MGM configuration through `gOFS->mConfigEngine`.

## Important APIs, Types, and Functions

- `ConfigCmd::ProcessRequest()` enforces root-only execution and dispatches by `ConfigProto::subcmd_case()`.
- `LsSubcmd()` calls `IConfigEngine::ListConfigs()`.
- `DumpSubcmd()` calls `DumpConfig()`.
- `ResetSubcmd()` calls `ResetConfig()`.
- `ExportSubcmd()` rejects deprecated export use.
- `SaveSubcmd()` calls `SaveConfig(file, force, comment, std_err)`.
- `LoadSubcmd()` constructs `ConfigResetMonitor` and calls `LoadConfig()`.
- `ChangelogSubcmd()` tails the config-engine changelog.

## Control Flow

On execution, non-root callers get `EPERM`. Root requests are copied from `mReqProto.config()` and dispatched. Listing and dumping return text produced by the config engine. Reset mutates in-memory/current config and returns success. Save/load log their proto debug strings, call the config engine, propagate `errno` on failure, and return success messages on success. Export is intentionally deprecated and always `EINVAL`.

## State and Persistence Behavior

All state is in `gOFS->mConfigEngine`. Save persists current configuration to a named config file, optionally forced. Load replaces current configuration from a named file and uses `ConfigResetMonitor`, likely to coordinate fsview/config reset side effects. Reset cleans current config. Changelog reads engine-maintained history.

## Dependencies and Integration Points

The command depends on `ConfigCmd.hh`, `ProcInterface`, `XrdMgmOfs`, `FsView` for `ConfigResetMonitor`, and `IConfigEngine`. It is constructed by `ProcInterface` for admin-only `RequestProto::kConfig`.

## Risks and Edge Cases

- `ProcessRequest()` requires `uid == 0`, stricter than central admin gating; admins/sudoers who pass `VidIsAdmin()` still cannot run it.
- Failures use global `errno`, which may not be reliably set by every config-engine method.
- `ResetSubcmd()` does not set an explicit `retc`; success relies on protobuf default zero.
- `ExportSubcmd()` remains in the proto surface but is deprecated.

## Test Signals

Tests should cover root/non-root behavior, list with and without backups, dump missing config, save force/no-force, load errors and reset-monitor side effects, changelog line counts, deprecated export failure, and config-engine failure propagation through `std_err` and `retc`.
