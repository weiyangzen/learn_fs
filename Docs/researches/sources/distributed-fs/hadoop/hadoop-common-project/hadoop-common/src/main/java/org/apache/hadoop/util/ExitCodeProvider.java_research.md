# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitCodeProvider.java

## Purpose

`ExitCodeProvider` is a minimal interface for exceptions or error carriers that can expose a process exit code. It lets existing exception hierarchies participate in command-line exit handling without sharing a base class.

## Important APIs, Types, And Functions

The only API is `int getExitCode()`. `ExitUtil.ExitException` and `ExitUtil.HaltException` implement it, and other Hadoop exceptions can implement it where callers need stable shell status propagation.

## Control Flow, State, And Persistence

The interface has no control flow or state. Runtime behavior depends entirely on implementing classes and consumers such as `ExitUtil` or command wrappers.

## Dependencies And Integration Points

It lives in `org.apache.hadoop.util` and has no imports. It integrates with CLI tools, service launchers, and test hooks that distinguish normal failures from generic exceptions.

## Risks And Test Signals

The main risk is inconsistent exit-code semantics across implementers. Tests should assert that wrappers prefer `getExitCode()` over fallback defaults and preserve expected nonzero codes.
