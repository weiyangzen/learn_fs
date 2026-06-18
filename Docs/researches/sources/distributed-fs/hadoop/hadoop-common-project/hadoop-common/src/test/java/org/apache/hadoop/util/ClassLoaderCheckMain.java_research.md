<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheckMain.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheckMain.java

## Purpose

`ClassLoaderCheckMain.java` is an executable test entry point for verifying `ApplicationClassLoader` behavior from a main class.

## Important APIs, Types, and Functions

It defines `main(String[] args)` and invokes `ClassLoaderCheck.checkClassLoader` for `ClassLoaderCheckSecond` and `ClassLoaderCheckThird`.

## Control Flow

The main method checks that one companion class is loaded by the app classloader and another by the parent/system classloader, throwing if expectations fail.

## State and Persistence Behavior

It has no state and no persistence; success is process completion without exception.

## Dependencies and Integration Points

It integrates with `ClassLoaderCheck`, companion classes, and classpath/test-jar construction in application classloader tests.

## Risks and Edge Cases

The expected loader split is sensitive to classpath ordering and system-class exclusion rules.

## Test Signals

Process exit status and thrown exceptions indicate whether classloader isolation behaves as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/ClassLoaderCheckMain.java -->
