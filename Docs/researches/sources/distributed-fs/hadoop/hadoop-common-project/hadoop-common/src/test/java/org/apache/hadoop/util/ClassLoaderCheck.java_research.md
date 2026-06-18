<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheck.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheck.java

## Purpose

`ClassLoaderCheck.java` is a tiny helper used by classloader tests to assert which `ClassLoader` loaded a class.

## Important APIs, Types, and Functions

It exposes `checkClassLoader(Class cls, boolean shouldBeLoadedByAppClassLoader)` and compares `cls.getClassLoader()` against `ClassLoaderCheck.class.getClassLoader()`.

## Control Flow

The helper throws `RuntimeException` when the observed classloader identity does not match the expected application-vs-system loading relationship.

## State and Persistence Behavior

No state is retained or persisted.

## Dependencies and Integration Points

It depends only on Java class loading and is packaged into test jars generated for `ApplicationClassLoader` tests.

## Risks and Edge Cases

Classloader identity depends on the test jar layout and parent-first/child-first rules. The raw `Class` parameter avoids generics but is harmless in test code.

## Test Signals

The signal is whether invoking this helper from separate test classes throws or completes under different loader configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheck.java -->
