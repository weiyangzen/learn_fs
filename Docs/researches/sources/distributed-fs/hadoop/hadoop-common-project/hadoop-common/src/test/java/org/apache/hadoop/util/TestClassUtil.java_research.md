<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestClassUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestClassUtil.java

## Purpose

`TestClassUtil.java` tests utilities that locate the jar or class file containing a given class.

## Important APIs, Types, and Functions

Tests call `ClassUtil.findContainingJar(Assertions.class)` and `ClassUtil.findClassLocation(ViewFileSystem.class)`, with AssertJ assertions and JUnit timeouts.

## Control Flow

Each test invokes a location helper, wraps the returned path in `File`, asserts it exists, and checks the filename pattern.

## State and Persistence Behavior

No state is mutated; the tests inspect the runtime classpath.

## Dependencies and Integration Points

It integrates with `ClassUtil`, AssertJ, JUnit 5, `ViewFileSystem`, and dependency jars on the test classpath.

## Risks and Edge Cases

Classpath layout differs across IDEs, build tools, shaded jars, and exploded classes. Filename regexes can fail if dependency packaging changes.

## Test Signals

Signals are non-null existing locations, expected `assertj-core*.jar` jar path, and `ViewFileSystem.class` class-file path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestClassUtil.java -->
