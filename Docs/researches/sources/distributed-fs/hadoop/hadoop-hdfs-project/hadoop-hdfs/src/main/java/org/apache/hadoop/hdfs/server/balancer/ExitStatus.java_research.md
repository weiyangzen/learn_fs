# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/ExitStatus.java

## Purpose

`ExitStatus` is the balancer command-line status enum. Each enum value maps directly to the process exit code returned by HDFS balancer and related tooling.

## Important APIs, Types, and Functions

The enum constants are `SUCCESS`, `IN_PROGRESS`, `ALREADY_RUNNING`, `NO_MOVE_BLOCK`, `NO_MOVE_PROGRESS`, `IO_EXCEPTION`, `ILLEGAL_ARGUMENTS`, `INTERRUPTED`, and `UNFINALIZED_UPGRADE`. The only method, `getExitCode()`, returns the integer code stored by the private constructor.

## Control Flow

There is no internal algorithm. Callers choose an enum based on balancer outcome and pass `getExitCode()` to CLI process-exit paths.

## State and Persistence Behavior

State is immutable enum metadata. There is no persistence, serialization logic, or external resource ownership.

## Dependencies and Integration Points

It depends only on Java enum mechanics and is consumed by balancer command code to standardize shell-visible result codes.

## Risks and Edge Cases

The numeric values are part of CLI behavior; changing them can break scripts or monitoring. Positive `IN_PROGRESS` is distinct from `SUCCESS`, while most error states are negative.

## Test Signals

Tests should assert the exact code for each enum and cover CLI mappings from already-running, no-progress, invalid-argument, interrupted, I/O, and unfinalized-upgrade paths.
