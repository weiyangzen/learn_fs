# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatus.java

## Purpose
`ReencryptionStatus` tracks re-encryption progress for encryption zones. It stores one `ZoneReencryptionStatus` per zone and aggregate metrics for completed zones.

## APIs and Control Flow
The class maintains a `TreeMap<Long, ZoneReencryptionStatus>` to preserve zone ID ordering. State transition methods mark zones for retry, started, or completed. `getNextUnprocessedZone()` scans for the first submitted zone. `hasRunningZone()` checks non-completed status. `updateZoneStatus()` adds a zone from `ReencryptionInfoProto` if absent, otherwise updates completion, submission, or in-progress checkpoint state. `removeZone()`, testing counters, `resetMetrics()`, `toString()`, and `getZoneStatuses()` expose management and diagnostics.

## State, Dependencies, and Integration
Comments state FSDirectory lock provides synchronization except for test-only methods. Dependencies include `ZoneReencryptionStatus`, protobuf `ReencryptionInfoProto`, batched-listing empty entries, `Preconditions`, SLF4J logging, and Hadoop list utilities. It integrates with encryption zone re-encryption RPCs and `ReencryptionStatusIterator`.

## Risks and Test Signals
The copy constructor shallow-copies `ZoneReencryptionStatus` objects, so mutations can leak between copies. `zonesReencrypted` increments when adding completed zones and when marking completion, so reconciliation must avoid double counting. Tests should cover submission/retry/processing/completion transitions, update paths with/without last-file checkpoint, removal, metric reset, copy isolation expectations, and lock discipline in NameNode callers.
