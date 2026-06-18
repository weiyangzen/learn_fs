# Research: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.hh

## Purpose

`ConfigCmd.hh` declares the protobuf MGM configuration command handler. It exposes a root-only administrative surface for config list, dump, reset, export, save, load, and changelog operations.

## Important APIs, Types, and Functions

- `ConfigCmd` derives from `IProcCommand`.
- The constructor moves `RequestProto` and stores the caller identity.
- `ProcessRequest()` is the execution entry point.
- Private methods correspond to `ConfigProto` subcommands: `LsSubcmd`, `DumpSubcmd`, `ResetSubcmd`, `ExportSubcmd`, `SaveSubcmd`, `LoadSubcmd`, and `ChangelogSubcmd`.

## Control Flow

`ProcInterface` constructs this class for `RequestProto::kConfig`. The implementation then checks root privileges and dispatches to private methods based on the config proto oneof.

## State and Persistence Behavior

The class declares no member state beyond inherited request/identity data. Configuration state and persistence are delegated to `gOFS->mConfigEngine`.

## Dependencies and Integration Points

The header includes `proto/Config.pb.h` and `ProcCommand.hh`. It is paired with `ConfigCmd.cc` and participates in central protobuf admin dispatch.

## Risks and Edge Cases

- Proto evolution requires adding private methods and implementation switch cases.
- The header exposes export even though the implementation rejects it as deprecated.
- The comment spacing and extra blank lines are harmless but reflect an older generated/manual style.

## Test Signals

Compile tests should verify generated config proto symbols match declarations. Runtime behavior is covered in `ConfigCmd.cc` tests.
