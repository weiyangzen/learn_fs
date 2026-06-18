# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProgramDriver.java

## Purpose
`ProgramDriver` is a small command dispatcher for Hadoop examples and tools. It maps user-visible command names to classes with static `main(String[])` methods and invokes the selected program.

## Important APIs, Types, And Functions
Important members are the `TreeMap<String,ProgramDescription> programs`, `addClass`, `run`, `driver`, `printUsage`, and nested `ProgramDescription`. The nested class stores a reflected `main` method and a help description.

## Control Flow
`addClass` resolves the target class's public `main(String[])` method and stores it by name. `run` validates that the first argument names a registered program, prints usage for missing or unknown names, shifts remaining arguments into a new array, invokes the target main, unwraps `InvocationTargetException`, and returns `0`. `driver` preserves the Hadoop 1.x API by calling `System.exit(-1)` on usage errors.

## State And Persistence
State is an in-memory sorted map of registered programs. There is no synchronization and no persistence.

## Dependencies And Integration Points
It depends on Java reflection and Hadoop annotations. It integrates with command-line entry points that want a single binary to expose many subcommands.

## Risks
Only public `main` methods are accepted. Exceptions from target programs propagate as their original cause. Concurrent mutation of `programs` is unsafe. Usage text goes to stdout, not stderr.

## Test Signals
Tests should cover registration, sorted usage output, unknown command handling, argument shifting, propagation of target exceptions, and `driver` exit behavior through process-level tests.
