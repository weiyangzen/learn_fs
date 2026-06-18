# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/BaseExpression.java

Purpose: base implementation for `find` expressions, providing usage/help storage, option propagation, lifecycle propagation, argument/child storage, default expression classification, and helper accessors for path/status/filesystem.

Important APIs and types: `setUsage()`, `setHelp()`, `setOptions()`, `prepare()`, `finish()`, `isAction()`, `isOperator()`, `getPrecedence()`, `addChildren()`, protected `addChildren(exprs,count)`, `addArguments(args,count)`, `getArgument()`, `getFileStatus()`, `getPath()`, and `getFileSystem()`.

Control flow: lifecycle calls cascade to all children. `isAction()` is true if any child is an action. Default child/argument methods do nothing; subclasses opt in. `getFileStatus()` follows symlinks when global options say follow all links or follow command-argument links at depth zero.

State and persistence: stores `FindOptions`, `Configuration`, linked-list arguments, and child expressions. No filesystem mutation.

Dependencies and integration: implements `Expression` and `Configurable`, uses `PathData`, `FileStatus`, `FileSystem`, and `Path`.

Risks: `getOptions()` returns a new default `FindOptions` when unset, which can mask missing option propagation. `getFileStatus()` references `options` field directly, so calling before `setOptions()` can NPE if symlink status is evaluated. Child insertion uses `push()`, reversing order relative to pop sequence by design.

Test signals: cover lifecycle propagation, action detection through children, missing/null argument errors, child ordering, symlink status following under `-L`/`-H`, unset options behavior, and `toString()` format.
