# Research: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.hh

## Purpose

`ConvertCmd.hh` declares the protobuf converter command handler used to inspect/configure the converter engine, schedule file conversions, list jobs, and clear jobs.

## Important APIs, Types, and Functions

- `ConvertCmd` derives from `IProcCommand`.
- `ProcessRequest()` executes the command.
- `ConfigList(bool json)` formats current converter state.
- `ConfigSubcmd()`, `FileSubcmd()`, `ListSubcmd()`, and `ClearSubcmd()` implement the proto subcommands.
- `PathFromIdentifierProto()` resolves proto identifiers into namespace paths.
- `CheckConversionProto()` validates conversion parameters.

## Control Flow

`ProcInterface` constructs this handler for `RequestProto::kConvert`. The implementation dispatches the `ConvertProto` oneof to the private helper matching the requested operation, using `RequestProto::JSON` to select JSON formatting.

## State and Persistence Behavior

The class has no declared mutable state beyond inherited request/identity. Converter configuration and job queues live in `gOFS->mConverterEngine`; namespace metadata is accessed externally.

## Dependencies and Integration Points

The header includes `proto/Convert.pb.h`, MGM namespace definitions, and `IProcCommand`. It is paired with `ConvertCmd.cc` and central protobuf dispatch.

## Risks and Edge Cases

- Private validation helpers define the command contract; proto additions need matching declaration/implementation changes.
- The comment typo "jons" and "represetation" is cosmetic but can obscure generated docs.
- Clearing jobs is declared without indicating its stronger privilege check, so readers must inspect implementation.

## Test Signals

Compile tests should ensure `Convert.pb.h` generated nested proto names remain compatible. Behavioral tests are covered by implementation tests for config/file/list/clear flows.
