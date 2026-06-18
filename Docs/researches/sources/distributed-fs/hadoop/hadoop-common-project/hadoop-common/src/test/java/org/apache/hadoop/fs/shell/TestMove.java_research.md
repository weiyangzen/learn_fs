# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestMove.java

## Purpose
Tests selected FsShell move/rename behavior: preventing implicit overwrite when moving into an existing directory that already contains the source basename, and rejecting unsupported threading option on `moveFromLocal`.

## Important APIs, Types, and Functions
The file uses `MoveCommands.Rename`, `MoveCommands.MoveFromLocal`, `CommandFormat.UnknownOptionException`, `PathExistsException`, mocked `FileSystem` and `FileStatus`, and a nested `InstrumentedRenameCommand` that captures `displayError` exceptions instead of printing them. `MockFileSystem` extends `FilterFileSystem` to route `mockfs` operations to the mock.

## Control Flow
Setup registers `mockfs` and resets the mock before each test. `testMoveTargetExistsWithoutExplicitRename` creates source, target directory, and duplicate destination statuses for both unqualified and authority-qualified paths, configures the mock filesystem URI, enables overwrite on the command, runs `Rename`, and asserts the captured error is `PathExistsException`. `testMoveFromLocalDoesNotAllowTOption` directly invokes `MoveFromLocal.run("-t", "2", null, null)` and expects `UnknownOptionException`.

## State and Persistence
All state is in Mockito mocks and command objects. No real filesystem mutations occur.

## Dependencies and Integration Points
This protects move command semantics in `MoveCommands`, especially path qualification behavior when resolving a duplicate destination inside a target directory. It also ensures move commands do not accidentally accept copy-only multithread options.

## Risks and Edge Cases
The first test is narrow but important: overwrite mode should not silently replace an existing child when the user did not explicitly name that child. The run result is not asserted directly; the captured error type is the signal. The second test passes null positional arguments because option parsing fails before path processing.

## Test Signals
Passing tests signal that move preserves no-implicit-overwrite safety and that `moveFromLocal` rejects the `-t` option with the expected parser exception.
