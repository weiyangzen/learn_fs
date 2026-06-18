<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskValidatorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskValidatorFactory.java

## Purpose

`TestDiskValidatorFactory.java` tests lookup and caching of disk validator implementations.

## Important APIs, Types, and Functions

It calls `DiskValidatorFactory.getInstance("basic")`, checks `BasicDiskValidator.class`, inspects `DiskValidatorFactory.INSTANCES`, and asserts `DiskErrorException` for a nonexistent validator name.

## Control Flow

One test resolves the basic validator and verifies the returned instance and cache entry. Another asks for `non-exist` and expects an exception.

## State and Persistence Behavior

Factory cache state is static in memory. No files are used.

## Dependencies and Integration Points

It integrates with `DiskValidatorFactory`, `BasicDiskValidator`, `DiskValidator`, and `DiskChecker.DiskErrorException`.

## Risks and Edge Cases

Global cache state can couple tests. String-to-class mapping failures must remain clear and not silently return a default implementation.

## Test Signals

Signals are non-null correct-class instance, populated cache, and expected exception on invalid name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDiskValidatorFactory.java -->
