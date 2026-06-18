<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigurationHelper.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigurationHelper.java

## Purpose

`ConfigurationHelper` centralizes duration parsing and minimum-duration enforcement for S3A configuration keys.

## Important APIs, Types, and Functions

It exposes `getDuration()`, `setDurationAsSeconds()`, `setDurationAsMillis()`, and `enforceMinimumDuration()`.

## Control Flow

`getDuration()` reads a duration with units from `Configuration.getTimeDuration()`, converts it to a requested `TimeUnit`, wraps it as `Duration`, and enforces a minimum. Setters write seconds or milliseconds with explicit suffixes. Minimum enforcement logs a warning once when a configured value is too low.

## State and Persistence Behavior

The class is stateless except for a static `LogExactlyOnce` used to avoid repeated warnings. Setters mutate the supplied configuration.

## Dependencies and Integration Points

It depends on Hadoop `Configuration`, Java `Duration`, time units, and S3A logging. It is used by configuration initialization code that needs stable lower bounds.

## Risks and Edge Cases

Duration conversion can truncate depending on unit. Values below minimum are silently raised after a warning. The static warning helper may suppress later warnings for different keys.

## Test Signals

Test default values, explicit unit parsing, second/millisecond setters, minimum clamping, warning-once behavior, and unit conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ConfigurationHelper.java -->
