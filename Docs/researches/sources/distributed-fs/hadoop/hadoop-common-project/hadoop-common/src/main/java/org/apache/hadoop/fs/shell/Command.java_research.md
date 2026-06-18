<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Command.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Command.java

## Purpose
Provides the base execution framework for Hadoop filesystem shell commands: option processing, argument expansion, path recursion, error reporting, usage reflection, and command factory access.

## Important APIs, Types, And Functions
Subclasses implement `getCommandName`, `run(Path)` or path-processing hooks. Main hooks include `processOptions`, `processRawArguments`, `expandArguments`, `expandArgument`, `processArguments`, `processArgument`, `processPathArgument`, `processPaths`, `processPath`, `postProcessPath`, `recursePath`, `isSorted`, and `getListingGroupSize`.

## Control Flow
`run(String...)` warns for deprecated commands, processes options, expands raw arguments into `PathData`, and processes each item. Existing paths flow through `processPathArgument` and `processPaths`; missing paths go to `processNonexistentPath`. Recursive traversal performs post-visit DFS over directory contents, optionally using sorted listings or grouped iterator batches. Errors are caught per argument/path, recorded, printed, and converted into non-zero exit codes.

## State And Persistence
Per-command state includes args/name/exit code/error count/recursive flag/depth/exceptions/output streams and factory reference. No filesystem persistence except subclass operations.

## Dependencies And Integration Points
Used by FsShell command classes. Depends on `PathData`, Hadoop configuration, remote iterators, logging, and reflection for static `NAME`, `USAGE`, and `DESCRIPTION` fields.

## Risks
Subclass contracts are flexible; missing `processPath` implementations fail at runtime. Error handling intentionally continues after many IOExceptions. Reflection-based usage fails if static fields are absent. Recursion depth is mutable shared command state.

## Test Signals
Command lifecycle unit tests for option parsing hooks, glob expansion failures, nonexistent paths, recursive traversal, sorted vs iterator listings, interrupted IO exit code 130, usage/description reflection, and error counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Command.java -->
