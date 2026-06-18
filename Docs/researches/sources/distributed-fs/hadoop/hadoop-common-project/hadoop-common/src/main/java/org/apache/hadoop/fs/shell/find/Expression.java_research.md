# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Expression.java

Purpose: defines the contract for all Hadoop shell `find` expression nodes.

Important APIs and types: lifecycle methods `setOptions()`, `prepare()`, `apply()`, `finish()`; metadata methods `getUsage()`, `getHelp()`; classification methods `isAction()`, `isOperator()`, `getPrecedence()`; parser hooks `addChildren()` and `addArguments()`.

Control flow: `Find` constructs expression trees, sets options, calls `prepare()`, invokes `apply(item, depth)` for each visited path, and then calls `finish()`. Operators consume child expressions; primaries consume string arguments.

State and persistence: interface has no state; implementations may keep parsed args, children, and runtime resources.

Dependencies and integration: works with `PathData` and returns `Result` to control pass/fail and descent.

Risks: implementers must honor deque pop ordering and lifecycle propagation or expression parsing and resource cleanup break. `isAction()` controls whether `Find` auto-adds `-print`, so incorrect classification changes user-visible output.

Test signals: expression implementer tests should verify lifecycle, parser consumption, action/operator classification, precedence, and `Result` semantics for traversal.
