# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommandTypes.java

Purpose: marker interface for categorizing CLI test command families.

Important APIs/types: empty interface implemented by `CLICommandFS`; intended for additional upstream command type markers.

Control flow: used by `CLICommand.getType` and runtime executor selection in `CLITestCmd`.

State and persistence: no state.

Dependencies/integration: part of the CLI test utility extension point.

Risks and test signals: no compile-time mapping enforces that each type has an executor. Tests should include failure behavior for unknown command types if new types are introduced.
