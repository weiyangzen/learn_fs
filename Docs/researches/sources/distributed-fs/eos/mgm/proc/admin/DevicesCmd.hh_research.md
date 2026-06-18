# Research: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.hh

## Purpose

`DevicesCmd.hh` declares the protobuf devices command handler for listing device/SMART information.

## Important APIs, Types, and Functions

- `DevicesCmd` derives from `IProcCommand`.
- `ProcessRequest()` is the execution entry point.
- Private `LsSubcmd()` implements `DevicesProto_LsProto`.

## Control Flow

`ProcInterface` constructs this handler for admin-only `RequestProto::kDevices`. The implementation supports only the `ls` subcommand and rejects others.

## State and Persistence Behavior

No command-specific state is declared. Device state comes from `gOFS->mDeviceTracker`.

## Dependencies and Integration Points

The header includes `proto/Devices.pb.h` and `ProcCommand.hh`, and is paired with `DevicesCmd.cc`.

## Risks and Edge Cases

- Adding subcommands requires header and implementation changes.
- The constructor formatting is slightly misaligned but behaviorally irrelevant.

## Test Signals

Compile coverage should verify generated `Devices.pb.h` types. Runtime tests should cover the `ls` implementation.
