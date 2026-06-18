<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/ulimit_test.go

## Purpose
Verifies `UlimitOpt` parsing and exported views.

## Important APIs, Types, And Functions
`TestUlimitOpt` initializes a map with `nofile`, constructs `NewUlimitOpt`, calls `Set`, `String`, and `GetList`.

## Control Flow
The test checks initial stringification, adds a valid `core=1024:1024`, verifies an invalid ulimit type errors, accepts either map iteration order in String output, and expects two list entries.

## State, Dependencies, And Integration Points
No external state. It depends on `container.Ulimit` and `go-units` validation behavior.

## Risks And Test Signals
It does not assert the contents of `GetList` beyond length, but it catches common regressions in parsing, map replacement, and invalid ulimit-name validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit_test.go -->
