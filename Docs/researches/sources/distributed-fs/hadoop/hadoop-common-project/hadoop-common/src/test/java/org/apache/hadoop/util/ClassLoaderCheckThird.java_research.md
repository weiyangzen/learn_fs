<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheckThird.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheckThird.java

## Purpose

`ClassLoaderCheckThird.java` is an empty companion marker class for classloader selection tests.

## Important APIs, Types, and Functions

It declares public class `ClassLoaderCheckThird` with no fields or methods.

## Control Flow

There is no runtime flow beyond class loading.

## State and Persistence Behavior

No state is owned.

## Dependencies and Integration Points

It is referenced by `ClassLoaderCheckMain` and packaged for `ApplicationClassLoader` tests.

## Risks and Edge Cases

Renaming, moving, or adding dependencies could change loading behavior and invalidate tests.

## Test Signals

The signal is whether the class is resolved by the expected loader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheckThird.java -->
