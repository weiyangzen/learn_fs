# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/util/CLICommand.java

Purpose: interface abstracting one parsed CLI test command and its executor factory.

Important APIs: `getExecutor(String tag, Configuration conf)`, `getType()`, `getCmd()`, and `toString()`.

Control flow: implemented by `CLITestCmd`; the harness calls `getExecutor` during test execution, then passes `getCmd` to the executor.

State and persistence: no state in the interface; implementers carry command text and type.

Dependencies/integration: depends on Hadoop `Configuration` and `CommandExecutor`. Enables upstream projects to add new command types without changing the harness.

Risks and test signals: type dispatch is runtime-only, so unknown implementations fail during execution. Tests should verify each supported `CLICommandTypes` has an executor.
