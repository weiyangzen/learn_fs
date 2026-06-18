# sources/cloud-native/moby/daemon/volume/mounts/validate_windows_test.go

## Purpose
Windows test constants for shared mount validation tests.

## Important APIs, Types, And Functions
Defines `testDestinationPath = c:\foo` and `testSourcePath = c:\foo`.

## Control Flow
No runtime logic; constants are used by shared parser/validation tests on Windows builds.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected on Windows and keeps shared tests aligned with Windows absolute path grammar.

## Risks
Constants must remain accepted by Windows parser destination/source regexes.

## Test Signals
Successful Windows test compilation validates build-tag wiring.
