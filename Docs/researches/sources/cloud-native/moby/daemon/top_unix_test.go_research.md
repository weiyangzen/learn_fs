# sources/cloud-native/moby/daemon/top_unix_test.go

## Purpose
This test file validates Unix `docker top` argument validation and `ps` output parsing.

## Important APIs, Types, And Functions
`TestContainerTopValidatePSArgs` exercises `validatePSArgs`. `TestContainerTopParsePSOutput` exercises `parsePSOutput`.

## Control Flow
Validation cases cover allowed and disallowed `PID` column renames, ASCII spaces, Unicode spaces, and empty/default args. Parse cases cover normal output, missing PID column, and Unicode whitespace that must not be treated as field separators.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects the parser and validation logic used by `ContainerTop`.

## Risks
The tests do not execute real `ps`, so platform-specific `ps` option compatibility is covered elsewhere.

## Test Signals
Provides focused regression coverage for security-sensitive parsing rules.
