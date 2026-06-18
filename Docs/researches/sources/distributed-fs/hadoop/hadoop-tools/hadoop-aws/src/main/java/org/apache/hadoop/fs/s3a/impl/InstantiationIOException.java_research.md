<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InstantiationIOException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InstantiationIOException.java

## Purpose

`InstantiationIOException` is a `PathIOException` subtype used when S3A cannot instantiate configured classes such as providers, factories, or optional components.

## Important APIs, Types, and Functions

The `Kind` enum categorizes abstract class, constructor failure, instantiation failure, not-implementing, unavailable, and unsupported-constructor cases. Static factory methods build typed exceptions with consistent messages.

## Control Flow

Callers use static helpers such as `isAbstract()`, `isNotInstanceOf()`, `unavailable()`, `unsupportedConstructor()`, and `instantiationException()` to include URI, class name, configuration key, and cause. Getters expose kind, class name, and key.

## State and Persistence Behavior

The exception stores final kind/class/key fields plus inherited path, message, and cause. There is no persistence beyond exception serialization inherited from `Throwable`.

## Dependencies and Integration Points

It depends on Hadoop `PathIOException` and is used by reflection-heavy S3A configuration and optional component loading, including encryption client availability.

## Risks and Edge Cases

Messages are operationally important because they often surface configuration mistakes. Incorrect kind selection can mislead diagnostics. Class names and keys may be null for unavailable optional modules.

## Test Signals

Test each factory method's kind, message content, path/URI formatting, cause preservation, class/key getters, and behavior for missing optional encryption classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InstantiationIOException.java -->
