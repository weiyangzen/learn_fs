# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/resources/testserver-default.xml

## Purpose
Default testserver configuration fixture.

## Important APIs, Types, And Functions
Defines `testserver.a=default` in standard Hadoop XML property form.

## Control Flow
Loaded as a resource by tests; no executable code.

## State, Persistence, And Dependencies
Configuration-only state. It relies on standard Hadoop XML config parsing and classpath resource availability.

## Integration Points
Used by test-server configuration loading paths to verify default property resolution and override behavior.

## Risks
The file is intentionally small; it only validates one property and cannot detect broader parser issues.

## Test Signals
Tests should observe `testserver.a` resolving to `default` unless another resource overrides it.
