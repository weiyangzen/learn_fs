# sources/cloud-native/moby/daemon/volume/safepath/common_test.go

## Purpose
Unit tests for lexical subtree checks used by safepath.

## Important APIs, Types, And Functions
`TestIsLocalTo` exercises `isLocalTo`.

## Control Flow
The table checks paths equal to base, nested paths, absolute escapes, `..` backtracking outside base, backtracking that remains inside base, relative paths, and filenames containing dots.

## State And Persistence
No filesystem state is required; checks are lexical.

## Dependencies And Integration Points
Validates the helper used by both Linux fallback safe open and Windows handle-lock traversal.

## Risks
Does not test symlink resolution; those behaviors are covered by `join_test.go`.

## Test Signals
Good signal that containment is not implemented by naive string prefix checks.
