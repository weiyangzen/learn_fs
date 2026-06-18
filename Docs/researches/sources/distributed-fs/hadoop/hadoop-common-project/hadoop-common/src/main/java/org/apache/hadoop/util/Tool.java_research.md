# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Tool.java

Purpose: `Tool` is Hadoop's stable CLI application contract for programs that accept generic Hadoop command-line options and carry a `Configuration`.

Important APIs/types/functions: it extends `Configurable` and declares `int run(String[] args) throws Exception`.

Control flow: implementers receive application-specific arguments after `ToolRunner` removes generic Hadoop options.

State and persistence behavior: state is supplied by the `Configurable` configuration implementation in concrete tools; `Tool` itself has no fields.

Dependencies and integration points: pairs with `GenericOptionsParser`, `ToolRunner`, `Configured`, MapReduce jobs, shells such as `KeyShell`, and test utilities invoking command-like classes.

Risks: implementers must treat `args` as post-generic-option arguments, not raw process arguments. Exceptions are allowed to propagate, so entrypoints need exit-code handling.

Test signals: tests should instantiate tools through `ToolRunner` to verify generic options update configuration and only remaining args reach `run`.
