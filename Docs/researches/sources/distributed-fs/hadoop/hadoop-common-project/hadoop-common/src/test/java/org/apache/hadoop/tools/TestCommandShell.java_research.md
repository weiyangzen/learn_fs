<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/tools/TestCommandShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/tools/TestCommandShell.java

## Purpose

`TestCommandShell.java` validates the generic `CommandShell` subcommand dispatch contract with a simple in-test shell.

## Important APIs, Types, and Functions

The nested `Example` extends `CommandShell`, implements `init`, `getCommandUsage`, and contains `Hello` and `Goodbye` subcommands. Tests capture `System.out`, run `hello`, invalid `hello x`, and `goodbye`.

## Control Flow

`Example.init` examines the first argument and installs a subcommand. `Hello.validate` requires exactly one argument; `execute` prints a message. Invalid validation returns usage and exit code 1, while valid subcommands return 0.

## State and Persistence Behavior

State consists of `savedArgs`, selected subcommand state in `CommandShell`, and a captured output stream. The test mutates global `System.out` during setup.

## Dependencies and Integration Points

It integrates with `CommandShell`, `Configuration`, JUnit 5, and stdout behavior for command-line tools.

## Risks and Edge Cases

The test does not restore `System.out`, so it relies on test runner isolation or later tests resetting it. It covers only one invalid argument case, not unknown commands beyond init return code.

## Test Signals

Exit-code assertions and captured output checks verify normal dispatch, validation failure usage text, and alternate subcommand execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/tools/TestCommandShell.java -->
