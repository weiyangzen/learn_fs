# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FindClass.java

## Purpose

`FindClass` is a diagnostic `Tool` for classpath and resource lookup. It can load a class, instantiate a class, locate a resource, or print a resource to stdout, returning explicit status codes for scripts.

## Important APIs, Types, And Functions

Actions are `create`, `load`, `locate`, and `print`. Exit codes include `SUCCESS`, `E_USAGE`, `E_NOT_FOUND`, `E_LOAD_FAILED`, and `E_CREATE_FAILED`. Key helpers are `getClass()`, `getResource()`, `loadResource()`, `dumpResource()`, `loadClass()`, `createClassInstance()`, `usage()`, `explainResult()`, and `setOutputStreams()` for tests.

## Control Flow, State, And Persistence

`run()` expects exactly an action and a target. Resource lookup uses the configured classloader. Class loading reports code source when available; creation uses `ReflectionUtils.newInstance()` with the active `Configuration`. Resource printing streams bytes until EOF. Static stdout/stderr streams are mutable test state; no persistent state is written.

## Dependencies And Integration Points

It integrates with `ToolRunner`, `Configured`, `Configuration`, `ReflectionUtils`, and classloader resources. It is useful in Hadoop shell diagnostics and tests that validate client classpaths or generated resources.

## Risks And Test Signals

Static stream overrides can leak between tests. Instantiation can execute arbitrary class initialization and constructors. Resource printing does not close stdout. Tests should validate every action, missing resources/classes, constructor failure, code-source reporting, usage errors, and stream override reset.
