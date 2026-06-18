# sources/cloud-native/buildkit/source/git/source_unix_test.go

## Purpose
For non-Windows test runs, resets the process umask to zero so Git source tests cannot accidentally pass because of the host's normal umask.

## Important APIs, Types, And Functions
- `init` calls `syscall.Umask(0)`.

## Control Flow
The init function executes before tests in the package. Git subprocess wrappers are then responsible for applying `0022`, making file-mode tests meaningful.

## State And Persistence
Changes process-global test umask for the test binary lifetime.

## Dependencies And Integration Points
Depends on `syscall` and complements `runWithStandardUmask` implementations.

## Risks And Edge Cases
Because umask is process-global, any tests in the same package that expect host umask semantics would be affected. In this package that is intentional.

## Test Signals
Supports `TestCompatibility014FileModes` and ordinary checkout mode assertions by forcing a strict baseline.
