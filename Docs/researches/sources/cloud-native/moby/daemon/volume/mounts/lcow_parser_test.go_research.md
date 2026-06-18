# sources/cloud-native/moby/daemon/volume/mounts/lcow_parser_test.go

## Purpose
Unit coverage for LCOW raw mount parsing and split-to-`MountPoint` conversion.

## Important APIs, Types, And Functions
`TestLCOWParseMountRaw` validates accepted/rejected strings. `TestLCOWParseMountRawSplit` compares parsed mountpoints against expected structs.

## Control Flow
The tests inject `mockFiProvider`, then exercise Windows host paths, named volumes, mixed-case modes, Linux slash destinations, reserved Windows volume names, missing sources, file sources, root destinations, and named pipe rejection. Split tests assert source, destination, mode, driver, type, read-write, and propagation fields.

## State And Persistence
No persistent state; all source existence checks come from the mock provider.

## Dependencies And Integration Points
Depends on LCOW parser, shared Windows mock file info, Docker API mount structs, and cmp options ignoring unexported `MountPoint` fields.

## Risks
The tests are table-driven but cover only known regex cases. They do not cover `ParseMountSpec` directly beyond shared validator behavior.

## Test Signals
Strong signal for LCOW's hybrid path semantics: Windows source grammar with Linux container destination grammar and no named-pipe mounts.
