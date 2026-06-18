# sources/cloud-native/containers-storage/drivers/graphtest/graphtest_windows.go

## Purpose
`graphtest_windows.go` is an empty Windows package stub for `graphtest`.

## Important APIs, Types, And Functions
It declares package `graphtest` and no APIs.

## Control Flow
No runtime behavior exists.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
It keeps the package buildable on Windows when Unix test helpers are excluded.

## Risks
Windows builds receive none of the shared graphtest helpers from Unix files.

## Test Signals
Build-only signal.
