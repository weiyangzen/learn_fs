<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFindClass.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFindClass.java

## Purpose

`TestFindClass.java` tests the `FindClass` command-line diagnostic utility for finding resources, loading classes, and instantiating classes.

## Important APIs, Types, and Functions

It uses `ToolRunner.run(new FindClass(), args)`, helper `run`, nested classes `FailInStaticInit`, `FailInConstructor`, `NoEmptyConstructor`, `BadToStringClass`, `PrivateClass`, and `PrivateConstructor`, plus log4j resource constants.

## Control Flow

Each test invokes `FindClass` with expected exit status and arguments for usage, resource lookup/printing, class load, class creation, static initializer failure, constructor failure, missing no-arg constructor, private class/constructor, and bad `toString`.

## State and Persistence Behavior

State is captured stdout through a `ByteArrayOutputStream` and static initializer/constructor behavior in nested classes. No files are written.

## Dependencies and Integration Points

It integrates with `FindClass`, `ToolRunner`, logging resources, Java reflection/classloading, and JUnit 5.

## Risks and Edge Cases

Classloading failures can differ by JVM diagnostics. Static initializer failure is sticky per classloader once triggered. Private accessibility and constructor behavior must produce stable exit codes.

## Test Signals

Signals are expected exit codes for all command modes and failure classes, plus resource/class discovery for known present and absent inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFindClass.java -->
