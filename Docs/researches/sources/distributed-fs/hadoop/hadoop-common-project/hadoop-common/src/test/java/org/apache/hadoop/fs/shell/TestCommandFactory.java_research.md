# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCommandFactory.java

## Purpose
Unit-tests `CommandFactory`, the FsShell registry responsible for mapping command names and aliases to `Command` instances.

## Important APIs, Types, and Functions
The test creates `CommandFactory(conf)`, calls `registerCommands(Class<?>)`, `addClass`, `getNames`, and `getInstance`. Nested commands extend `FsCommand`. `TestRegistrar.registerCommands` registers `TestCommand1` as `tc1` and `TestCommand2` under `tc2` and `tc2.1`. `TestCommand4` declares `NAME`, `USAGE`, and `DESCRIPTION`.

## Control Flow
`testSetup` initializes an empty factory before each test. `testRegistration` confirms no initial names, then verifies registered names preserve insertion order and aliases, then adds additional command classes by explicit string and by `TestCommand4.NAME`. `testGetInstances` verifies unknown names return null, known names instantiate the expected class, command instances record the requested command name, aliases instantiate the same class with alias name, and static usage/description fields are reflected in instance metadata.

## State and Persistence
State is a static factory reference and static `Configuration`; no filesystem or external resources are used. The factory is recreated per test to avoid registry leakage.

## Dependencies and Integration Points
`CommandFactory` is an FsShell integration point used to assemble available shell commands. Reflection over registrar and command classes is central to the behavior tested here.

## Risks and Edge Cases
The test covers basic happy-path registration and lookup but does not test duplicate names, malformed registrar methods, command constructor failures, or configuration propagation beyond instance creation.

## Test Signals
Passing tests signal stable command registry ordering, alias support, unknown-command handling, reflective instantiation, and static command metadata discovery.
