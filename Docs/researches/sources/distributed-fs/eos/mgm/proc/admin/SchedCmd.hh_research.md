# sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.hh

## Purpose
`SchedCmd.hh` declares the protobuf-backed scheduler command class under `namespace eos::mgm`.

## Important APIs, Types, And Functions
`class SchedCmd : public IProcCommand` stores no extra state, accepts a request and virtual identity, and overrides `ProcessRequest() noexcept`. Private helpers return `ReplyProto` by value: `ConfigureSubcmd()`, `SchedulerTypeSubcmd()`, `WeightSubCmd()`, `LsSubcmd()`, `ShowSubCmd()`, and `RefreshSubCmd()`.

## Control Flow
The declaration sets a two-level dispatch shape: `ProcessRequest()` handles top-level scheduler subcommands, and `ConfigureSubcmd()` handles nested configuration options. Unlike other admin command headers in this subset, helpers return reply objects directly instead of mutating a shared reply reference.

## State, Persistence, And Dependencies
The header depends on `proto/Sched.pb.h` and `mgm/proc/IProcCommand.hh`. It introduces no persistence behavior. The implementation mutates scheduler state through the global MGM scheduler pointer.

## Integration Points
This class plugs scheduler protobuf requests into the common `IProcCommand` execution framework and uses the modern C++ namespace declaration style rather than the `EOSMGMNAMESPACE_BEGIN` macro.

## Risks
Returning replies by value keeps subcommands isolated but can hide inconsistent default replies if a branch forgets to set `retc`. Generated protobuf schema changes are compile-time breaking at the private method signatures.

## Test Signals
Compile-time checks should catch protobuf and base-class compatibility. Runtime tests should build requests for each declared subcommand and assert returned reply fields rather than relying on mutated output parameters.
