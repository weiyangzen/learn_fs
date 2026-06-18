# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSink.java

## Purpose
Direct unit tests for `RollingFileSystemSink` configuration parsing and roll/flush time calculations.

## Important APIs, Types, And Functions
Uses `RollingFileSystemSink.init()`, `setInitialFlushTime()`, `updateFlushTime()`, `getRollInterval()`, and the package-visible fields `rollIntervalMillis`, `rollOffsetIntervalMillis`, `basePath`, `ignoreError`, `allowAppend`, `source`, and `nextFlush`.

## Control Flow
`testInit()` builds a subset configuration and asserts every parsed field. `testSetInitialFlushTime()` constructs sinks with zero, bounded, and pathological offset windows, seeds a `Calendar`, and checks the calculated initial `nextFlush`. `testUpdateRollTime()` verifies advancement after exact, slightly late, and far-late times. `testGetRollInterval()` iterates supported units and invalid units.

## State And Persistence Behavior
State is limited to sink fields and `Calendar` objects. No filesystem writes occur.

## Dependencies And Integration Points
Depends on Apache Commons `SubsetConfiguration`, `ConfigBuilder`, Hadoop `Path`, and `MetricsException`.

## Risks
Roll interval parsing is user-facing configuration logic; invalid units must fail loudly. Offset calculation permits a random negative offset, so assertions use ranges instead of exact values in those cases.

## Test Signals
Signals include `10m` becoming `600000`, default interval of one hour for bare `1`, supported minute/hour/day suffix variants, and `MetricsException` for unsupported suffixes.
