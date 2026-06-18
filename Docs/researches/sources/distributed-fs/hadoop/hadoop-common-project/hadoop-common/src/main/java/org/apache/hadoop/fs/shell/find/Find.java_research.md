# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Find.java

Purpose: implements Hadoop shell `-find`, including expression registration, parsing, recursive traversal, optional symlink following, and default `-print` action insertion.

Important APIs and types: static expression set and description builder, `processOptions()`, `parseExpression()`, `recursePath()`, `isPathRecursable()`, `processPath()`, `postProcessPath()`, `applyItem()`, and `processArguments()`. State includes `FindOptions`, root `Expression`, and `stopPaths`.

Control flow: construction enables recursion. Options parse `-L` or `-H`, split leading path args from expression args at the first token beginning with `-`, default path to `.`, parse expression deque using operator/primary stacks and parentheses, and auto-wrap non-action expressions with `Print AND expression`. During traversal, expressions are applied pre-order or post-order depending on options, only at or below min depth, and a `Result.STOP` path is recorded to prevent further recursion.

State and persistence: read-only traversal except expression actions may mutate if future actions are added. `stopPaths` is per-run in memory.

Dependencies and integration: extends `FsCommand`, uses `ExpressionFactory`, built-in `And`, `Print`, and `Name`, `FindOptions`, `PathData`, and inherited recursive traversal.

Risks: expression/path split treats the first dash-leading token as expression, so paths beginning with `-` need command-line escaping conventions. Symlink loop detection compares ancestors in one direction and may not catch all graph cycles. `Result.isDescend()` is only acted on through equality with `Result.STOP` in `applyItem()`, not arbitrary descend=false combinations unless equals STOP. Parenthesis parse errors are minimal. Built-in expression set is small.

Test signals: cover default path/expression, `-name`, `-iname`, `-print`, `-print0`, implicit AND, explicit AND, parentheses, action auto-print insertion, `-L`/`-H` symlink directory traversal, loop avoidance message, STOP behavior, depth-first options via `FindOptions`, and paths starting with dash.
