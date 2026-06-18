# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/TestFind.java

Purpose: Comprehensive unit tests for the FS shell `find` command parser and traversal engine. It validates option parsing, default expressions, expression tree formatting, traversal order, depth constraints, symlink-follow semantics, loop detection, and descent suppression through `Result.STOP`.

Important APIs/types/functions: `Find.processOptions`, `Find.processArguments`, `FindOptions` (`followLink`, `followArgLink`, `depthFirst`, `minDepth`, `maxDepth`, output streams), `Expression`, `BaseExpression.getFileStatus`, `Result`, `PathData`, `RemoteIterator<FileStatus>`, `MockFileSystem.setup`, inner `TestExpression`, `FileStatusChecker`, `createDirectories`, and `createPathData`.

Control flow: Parser tests feed command strings converted by `getArgs`, then assert option flags, remaining path arguments, default current-directory path, rejection of unknown expressions, and expected expression tree strings for `-name`, `-iname`, `-print`, `-print0`, implicit `-and`, `-a`, and `-and`. Traversal tests build a mocked directory graph: directories `item1`, `item2`, `item5`; files; a symlink to a file; symlinks from `item5` to a file, to itself, to a directory, and to a nested file. `listStatus` and `listStatusIterator` are stubbed. A wrapping `TestExpression` records `getFileStatus` resolution before delegating to a mocked expression, so tests can assert both apply order and status lookup order under normal, depth-first, follow-argument, follow-all, min-depth, max-depth, depth/min/max combinations, and STOP/no-descend behavior.

State/persistence: Uses static mock filesystem/configuration reset before each test. All filesystem contents are Mockito objects; no real FS state persists. `FindOptions` carries mutable traversal and output stream settings.

Dependencies/integration: Integrates parser, expression factory/precedence, `PathData`, Hadoop `FileStatus` symlink APIs, traversal recursion, `RemoteIterator` iteration, and output/error streams. The loop test expects a specific stderr message for a followed self-symlink.

Risks: Expected traversal order is highly coupled to implementation order. Symlink behavior is mocked and may miss real filesystem resolution edge cases. The helper `getArgs` splits on a single space and does not model shell quoting. Because many assertions use exact `toString()` expression forms, harmless formatting changes can break tests.

Test signals: Exact expression-tree strings, exact mutation of path argument lists, ordered Mockito verification of `apply` and status checks, absence of unexpected stdout/stderr, and explicit loop warning text for self-referential symlink traversal.
