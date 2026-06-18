# Research: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.hh

## Purpose

`EvictCmd.hh` declares the protobuf tape-eviction command handler used to remove disk replicas for tape-backed files.

## Important APIs, Types, and Functions

- `EvictCmd` derives from `IProcCommand`.
- The constructor passes `true` as the third `IProcCommand` argument, marking it differently from most admin handlers, likely as a long-running/asynchronous command.
- `ProcessRequest()` executes the eviction logic.

## Control Flow

`ProcInterface` constructs this handler for `RequestProto::kEvict`, which is classified as user-callable rather than admin-only. The implementation performs per-file permission checks before destructive replica removal.

## State and Persistence Behavior

No state is declared in the header. State mutations are implemented in `EvictCmd.cc` through namespace metadata and replica drop operations.

## Dependencies and Integration Points

The header includes `IProcCommand`, MGM namespace definitions, and `ConsoleRequest.pb.h`. It is paired with `EvictCmd.cc`.

## Risks and Edge Cases

- The command is user-callable but destructive; permission checks in the implementation are the primary protection.
- The special `IProcCommand(..., true)` constructor flag should be understood before changing async behavior.

## Test Signals

Compile tests should verify proto types and constructor signatures. Behavioral tests should focus on permission and replica-removal paths in the implementation.
