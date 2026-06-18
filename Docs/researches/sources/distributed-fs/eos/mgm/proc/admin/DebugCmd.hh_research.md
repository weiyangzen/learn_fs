# Research: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.hh

## Purpose

`DebugCmd.hh` declares the protobuf debug command handler for getting and setting MGM/FST debug logging state.

## Important APIs, Types, and Functions

- `DebugCmd` derives from `IProcCommand`.
- `ProcessRequest()` executes the command.
- `GetSubcmd()` is static and handles read-only debug state reporting.
- `SetSubcmd()` handles runtime log-level/filter changes.

## Control Flow

The handler is constructed by `ProcInterface` for admin-only `RequestProto::kDebug`. The implementation dispatches the debug proto oneof to `get` or `set`; set requires root.

## State and Persistence Behavior

No handler-specific state is declared. Runtime logging state is external in `Logging` and remote nodes.

## Dependencies and Integration Points

The header includes `proto/Debug.pb.h` and `ProcCommand.hh`, and is paired with `DebugCmd.cc`.

## Risks and Edge Cases

- `GetSubcmd()` is static because it does not need identity; `SetSubcmd()` is non-static because it checks `mVid`.
- Future debug subcommands require updates to both header and implementation.

## Test Signals

Compile tests should ensure generated debug proto nested types match signatures. Behavior tests should focus on implementation paths for get/set.
