<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/DataTransferThrottler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/DataTransferThrottler.java

## Purpose
`DataTransferThrottler` enforces a shared byte-per-second budget across one or more threads by sleeping callers when recent transfer volume exceeds the configured period allowance.

## APIs and Types
Constructors accept bandwidth alone with a 500 ms period or explicit period plus bandwidth. Public synchronized methods are `getBandwidth`, `setBandwidth`, `throttle(long)`, and `throttle(long, Canceler)`.

## Control Flow
Each throttle call subtracts transferred bytes from the current period reserve and adds to in-flight used bytes. While reserve is non-positive, it checks cancellation, waits until the current period ends, advances by one period if within a three-period extension, or resets accounting after long idle time. It restores interrupted status and exits the loop if wait is interrupted, then subtracts the call's bytes from `bytesAlreadyUsed`.

## State and Persistence
All mutable state is guarded by the object monitor: period, period extension, bytes per period, current period start, reserve, and bytes already used. No persistence.

## Dependencies and Integration
It depends on `Time.monotonicNow` and optional `Canceler`. It is used by HDFS data transfer paths to shape aggregate throughput.

## Risks
`setBandwidth` affects future periods but can produce zero `bytesPerPeriod` for very low bandwidth with short periods due to integer division, causing pathological throttling. Synchronization serializes all callers. Cancellation only exits sleeping logic and does not undo already-accounted bytes until method exit. Interrupted waits do not throw, so callers must inspect thread interrupt state.

## Test Signals
Tests should cover no-op for nonpositive bytes, bandwidth getter/setter, sleep behavior with fake/controlled time if available, cancellation return, interrupt restoration, long-idle reset, and low-bandwidth rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/DataTransferThrottler.java -->
