# sources/cloud-native/moby/daemon/volume/mounts/parser.go

## Purpose
Defines common mount parser interfaces, shared errors, mode maps, and host-OS parser selection.

## Important APIs, Types, And Functions
Exports `ErrVolumeTargetIsRoot`, shared subpath errors, `rwModes`, `Parser`, and `NewParser`.

## Control Flow
`NewParser` returns `NewWindowsParser` when `runtime.GOOS == "windows"` and `NewLinuxParser` otherwise. The `Parser` interface defines raw/spec parsing, volumes-from parsing, tmpfs conversion, default copy/propagation, volume-name validation, resource ownership checks, and mount config validation.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
All daemon mount parsing and volume service volume-name validation depend on this common interface. The platform-specific parser implementations satisfy it.

## Risks
Adding fields to `Parser` affects all platform parsers. Shared error values are used by tests and possibly API error matching, so changing messages can break compatibility.

## Test Signals
`parser_test.go`, platform parser tests, and validation tests exercise `NewParser` and interface behavior across OS-specific constants.
