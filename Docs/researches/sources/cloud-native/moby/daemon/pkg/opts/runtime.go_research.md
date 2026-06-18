<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/runtime.go -->
# sources/cloud-native/moby/daemon/pkg/opts/runtime.go

## Purpose
Parses named OCI runtime definitions from daemon configuration.

## Important APIs, Types, And Functions
`RuntimeOpt` stores an option name, stock runtime name, and `map[string]system.Runtime`. `NewNamedRuntimeOpt`, `Set`, `String`, `GetMap`, `Type`, and `Name` implement option behavior.

## Control Flow
`Set` requires `name=path`, trims spaces, rejects empty name/path, lowercases the name, rejects the reserved stock runtime name, rejects duplicates, and stores `system.Runtime{Path: path}`.

## State, Dependencies, And Integration Points
State is the referenced runtime map. It depends on Docker API `system.Runtime`. The daemon runtime selection path consumes this map.

## Risks And Test Signals
Lowercasing and trimming are TODO-marked compatibility behaviors that may accept surprising input. No direct test in this subset covers runtime parsing, so regressions rely on broader daemon config tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/runtime.go -->
