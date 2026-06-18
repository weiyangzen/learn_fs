# Research: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.hh

## Purpose

`AccessCmd.hh` declares the protobuf access-control command handler and the `ProcessRuleKey()` helper. It defines the structured admin interface for managing MGM access bans, allows, redirections, stalls, limits, and stall-host patterns.

## Important APIs, Types, and Functions

- `ProcessRuleKey(const std::string&)` converts eligible `threads:` username keys to internal uid-based keys.
- `AccessCmd` derives from `IProcCommand` and stores a moved `RequestProto` plus caller `VirtualIdentity`.
- `ProcessRequest()` is the public command execution entry.
- Private subcommand methods cover `LsSubcmd`, `RmSubcmd`, `SetSubcmd`, `BanSubcmd`, `UnbanSubcmd`, `AllowSubcmd`, `UnallowSubcmd`, and `StallhostsSubcmd`.
- `aux()` centralizes persistence/result handling for several mutations.

## Control Flow

`ProcInterface` constructs `AccessCmd` for `RequestProto::kAccess`. The command then validates access-admin privileges and dispatches to a private method matching the oneof subcommand in `AccessProto`. Most private methods mutate `Access` global state and call `aux()` or `StoreAccessConfig()`.

## State and Persistence Behavior

The header declares no state of its own beyond inherited `IProcCommand` request/identity data. Runtime and persisted state are external in `mgm/access/Access`. The constructor passes `false` as the third `IProcCommand` argument, so this handler is not flagged as the special long-running behavior used by some commands.

## Dependencies and Integration Points

It includes `proto/Access.pb.h` and `mgm/proc/ProcCommand.hh` for `IProcCommand`/proc definitions. It is tightly paired with `AccessCmd.cc` and constructed by `ProcInterface`.

## Risks and Edge Cases

- Any new `AccessProto` subcommand requires a new private method and switch update in the implementation.
- `ProcessRuleKey()` is declared globally in the MGM namespace, so other code may start depending on its current normalization semantics.
- The header comment says "config commands", which is stale and can confuse maintainers.

## Test Signals

Compile tests should verify generated `Access.pb.h` enum names and all declared subcommands match implementation signatures. Behavioral tests belong in `AccessCmd.cc` coverage, especially privilege checks and persistence behavior.
