# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DiskBalancerCLI.java`

## Purpose

`DiskBalancerCLI` is the top-level command dispatcher for HDFS disk balancer operations. It defines CLI options for planning, executing, querying, canceling, reporting, and help, then delegates implementation to command classes under `org.apache.hadoop.hdfs.server.diskbalancer.command`.

## Important APIs, Types, and Functions

- Public constants define command and option names, output filename templates, default report count, and plan version.
- Static `Options` instances expose per-command option sets for tests and help generation.
- `run` composes all options, parses args with Commons CLI `BasicParser`, rejects extra positional arguments beyond two, and dispatches.
- `addPlanCommands`, `addExecuteCommands`, `addQueryCommands`, `addCancelCommands`, `addReportCommands`, and `addHelpCommands` populate both global and per-command option collections.
- `dispatch` selects `PlanCommand`, `ExecuteCommand`, `QueryCommand`, `CancelCommand`, `ReportCommand`, or `HelpCommand`, executes it, and always closes it.

## Control Flow

`main` runs the tool with `HdfsConfiguration` and converts thrown exceptions into process exit code `1`. `run` parses all recognized command options at once rather than subcommand-first parsing. `dispatch` checks options in fixed order and assigns `dbCmd` when an option is present; if multiple command options are present, the later matching checks can override earlier ones. If no command option exists, it executes main help and returns `1`.

## State and Persistence Behavior

`DiskBalancerCLI` stores `printStream` and a `currentCommand` field, though the field is not assigned in the shown dispatch path. Persistent/cluster state is handled by delegated command classes: plan/report may write files, execute/cancel/query talk to DataNodes and HDFS. This class itself only parses and dispatches.

## Dependencies and Integration Points

It depends on Apache Commons CLI, Hadoop `Configured`/`Tool`, `HdfsConfiguration`, and disk balancer command implementations. Constants here form part of the contract consumed by those commands and tests.

## Risks and Edge Cases

- Static `Options` instances are mutated every time `add*Commands` is called, so repeated `run` calls in the same JVM can accumulate duplicate options depending on Commons CLI behavior.
- Multiple top-level command options are not rejected directly; last matching command in dispatch order wins.
- `currentCommand` is exposed but not set, which limits observability or may break expectations in tests.
- `BasicParser` is legacy Commons CLI API.
- Extra positional argument validation allows up to two args regardless of which command is selected; deeper validation is delegated.

## Test Signals

Tests should cover each command option selecting the right command, help fallback, multi-command-option behavior, duplicate static option registration across repeated instances, parse errors, command close in failure paths, and positional argument rejection.
