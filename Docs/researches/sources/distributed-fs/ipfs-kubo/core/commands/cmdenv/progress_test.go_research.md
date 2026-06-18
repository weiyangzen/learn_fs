<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress_test.go

## Purpose

Verifies progress display selection semantics for command post-run handlers.

## Important APIs, Types, and Functions

`TestShouldShowProgress` constructs request option maps with a local `makeReq` helper and compares `ShouldShowProgress` with expected values.

## Control Flow

Subtests assert explicit true and false override TTY state, unset options equal `IsTerminal(os.Stderr)`, and non-bool values are treated as unset.

## State and Persistence Behavior

Pure unit test; no persistence.

## Dependencies and Integration Points

Depends on `cmds.Request`, `os.Stderr`, and `IsTerminal`.

## Risks and Edge Cases

The unset and non-bool expectations are environment-dependent by design because they compare to the same terminal detection call. The test does not mock terminal state.

## Test Signals

Good signal for option precedence. Missing signal includes behavior when stderr is closed or replaced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress_test.go -->
