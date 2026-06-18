<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFactory.java

## Purpose
Registers shell command names and creates command instances for FsShell.

## Important APIs, Types, And Functions
`registerCommands` reflectively invokes a class's static `registerCommands(CommandFactory)`. `addClass`, `addObject`, `getInstance`, and `getNames` manage command mappings.

## Control Flow
Class registrations map names to command classes. Object registrations map names to reusable instances and put null in the class map so names appear in listings. `getInstance` returns a registered object or reflectively instantiates a class with the provided configuration, then sets command name and factory.

## State And Persistence
In-memory maps from command name to class or object. No persistence.

## Dependencies And Integration Points
Used by FsShell startup and help/usage commands. Depends on Hadoop `ReflectionUtils`, `Configured`, and command registration conventions.

## Risks
`getInstance` requires non-null configuration. Reusable object registrations can retain state across invocations if the command object is mutable. Reflection failures are wrapped as runtime exceptions with stringified stack traces.

## Test Signals
Register class/object commands, instantiate with config, list sorted names, unknown command returns null, null configuration failure, and registrar reflection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFactory.java -->
