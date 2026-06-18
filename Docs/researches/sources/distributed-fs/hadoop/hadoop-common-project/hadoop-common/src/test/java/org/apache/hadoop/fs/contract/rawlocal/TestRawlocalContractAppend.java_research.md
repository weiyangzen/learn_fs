# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractAppend.java

## Purpose
`TestRawlocalContractAppend` runs append contract tests against raw local FS and skips an unsupported Windows open-file rename case.

## Important APIs, Types, And Functions
It extends `AbstractContractAppendTest`, creates `RawlocalFSContract`, and overrides `testRenameFileBeingAppended()`. The override uses AssertJ assumptions to skip when `Path.WINDOWS` is true before calling `super`.

## Control Flow
Inherited append tests run normally. For rename-while-appending, the test aborts on Windows, where open file handles prevent the behavior, and otherwise executes the inherited scenario.

## State And Persistence
No subclass fields. Raw local files are created, appended, and possibly renamed during tests.

## Dependencies And Integration Points
It depends on raw local filesystem semantics and `Path.WINDOWS` platform detection.

## Risks
Skipping only Windows avoids false negatives, but other filesystems mounted locally could also have restrictive open-file rename behavior.

## Test Signals
Signals include byte-for-byte append validation and platform-appropriate handling of open-file rename.
