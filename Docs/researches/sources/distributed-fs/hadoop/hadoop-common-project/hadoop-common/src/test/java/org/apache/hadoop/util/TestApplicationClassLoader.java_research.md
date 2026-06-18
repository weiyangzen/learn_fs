<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestApplicationClassLoader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestApplicationClassLoader.java

## Purpose

`TestApplicationClassLoader.java` tests application classloader classpath URL construction, system-class matching, nested-class matching, and resource lookup.

## Important APIs, Types, and Functions

It uses static `constructUrlsFromClasspath` and `isSystemClass`, `ApplicationClassLoader`, `GenericTestUtils`, `FileUtil`, Guava `Splitter`, and helper `makeTestJar`.

## Control Flow

Setup deletes and recreates a test directory. Classpath tests create files, directories, a jar directory, and nonexistent entries, then assert only existing file/dir/jar URLs are returned. System-class tests run positive and negative include/exclude patterns, including nested class suffixes. Resource tests create a jar with `resource.txt` and load it through `ApplicationClassLoader`.

## State and Persistence Behavior

Temporary files and jars are written under `target/test-dir/appclassloader` and cleaned during setup. Loader state is in-memory.

## Dependencies and Integration Points

It integrates with `ApplicationClassLoader`, filesystem helpers, jar streams, Apache Commons IO, JUnit 5, and classpath pattern semantics used by Hadoop launchers.

## Risks and Edge Cases

Risks include wildcard classpath expansion order, nonexistent path handling, negative pattern precedence, nested-class naming, and resource leaks from unclosed streams.

## Test Signals

Signals include exact URL counts/order, include/exclude system-class booleans, and successful resource loading from a child loader while absent from the parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestApplicationClassLoader.java -->
