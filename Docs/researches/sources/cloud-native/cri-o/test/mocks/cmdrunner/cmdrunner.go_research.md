# sources/cloud-native/cri-o/test/mocks/cmdrunner/cmdrunner.go

## Purpose
Generated GoMock implementation of `utils/cmdrunner.CommandRunner`.

## Important APIs, Types, And Functions
`MockCommandRunner`, recorder type, `NewMockCommandRunner`, `EXPECT`, and mocked methods `CombinedOutput`, `Command`, and `CommandContext`.

## Control Flow
Each mock method calls `m.ctrl.Call`; each recorder method calls `RecordCallWithMethodType`, preserving variadic arguments.

## State And Persistence
No persistence. Holds GoMock controller and expected call state in memory.

## Dependencies And Integration Points
Used by tests that need deterministic command execution behavior without invoking host commands.

## Risks And Test Signals
Generated file should not be hand-edited. Interface drift requires regeneration or compile failures.
