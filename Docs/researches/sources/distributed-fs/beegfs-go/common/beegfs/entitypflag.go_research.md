# sources/distributed-fs/beegfs-go/common/beegfs/entitypflag.go

## Purpose
This file adapts `EntityIdParser` and `EntityIdSliceParser` to Cobra/pflag `Value` implementations.

## APIs and Control Flow
`NewEntityIdPFlag` stores a parser and pointer to the destination `EntityId`. `Type` returns `entityId`, `String` returns the current entity string or `unspecified`, and `Set` parses input then writes to the destination pointer. `NewEntityIdSlicePFlag` does the same for `[]EntityId`, with a type string indicating comma-separated values; its `String` always returns `<unspecified>`.

## State, Dependencies, and Integration
State is the parser plus a caller-owned destination pointer. The wrappers integrate directly with Cobra command flags via `Flags().Var()`.

## Risks and Test Signals
`Set` assumes destination pointers are non-nil and will panic if misconstructed. Slice flag `String` does not reflect current values, which may affect help/default rendering. There are no listed direct tests for pflag integration.
