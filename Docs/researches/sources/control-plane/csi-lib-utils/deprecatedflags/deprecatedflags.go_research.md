# sources/control-plane/csi-lib-utils/deprecatedflags/deprecatedflags.go

## Purpose
This package lets binaries register flags that are accepted for backward compatibility but ignored with a warning.

## Important APIs, Types, And Functions
Public APIs are `Add(name string) bool` and `AddBool(name string) bool`. Internal type `deprecated` implements `flag.Value` and `IsBoolFlag`.

## Control Flow
`Add` and `AddBool` register a `deprecated` value with the global `flag` package and return true for compatibility with global variable initialization patterns. When the flag is set, `Set` writes a warning to stderr and returns nil. `IsBoolFlag` marks boolean flags so `-flag` syntax is accepted.

## State, Persistence, And Dependencies
State is registered in the process-global flag set. It writes warnings to stderr. Dependencies are only standard library packages.

## Integration Points
Sidecars can use this when removing old flags without breaking command lines immediately.

## Risks And Test Signals
There are no tests in this subset. The warning omits a trailing newline, which can merge with other stderr output. The package uses global `flag` instead of an injected FlagSet.
