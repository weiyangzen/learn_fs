# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/TestActiveAuditManagerThreadLeakage.java

## Purpose

`TestActiveAuditManagerThreadLeakage.java` stress-tests `ActiveAuditManagerS3A` weak-reference span tracking to prevent thread-local memory leaks described by HADOOP-18091.

## Important APIs, Types, and Functions

The class creates `ActiveAuditManagerS3A` with `MemoryHungryAuditor`, inspects `WeakReferenceThreadMap`, uses `PRUNE_THRESHOLD`, and creates spans from fixed thread pools. Key tests are `testSpanMapClearedInServiceStop()`, `testMemoryLeak()`, `testRegularPruning()`, and `testSpanDeactivationRemovesEntryFromMap()`.

## Control Flow

The leak test repeatedly creates managers on a short-lived executor, has long-lived worker threads create spans, forces GC, probes weak map entries, verifies dereferenced entries are pruned, and keeps weak references to managers to confirm some are garbage collected. Other tests check stop clears the map, periodic pruning occurs, and deactivation removes entries.

## State and Persistence Behavior

State is intentionally heap-heavy and weak-reference-based: manager list, worker thread pool, active span map entries keyed by thread ID, pruning count, and weak manager references.

## Dependencies and Integration Points

It validates the active audit manager's lifecycle, weak map cleanup, memory-heavy auditor behavior, and span activation/deactivation interactions.

## Risks and Edge Cases

The test is timing/GC-sensitive and uses large constants. It avoids creating spans in the JUnit thread because those references would live for the JVM duration.

## Test Signals

Signals are span map size zero after stop, nonzero prune count, nonzero garbage-collected managers, exact periodic pruning count, and map-key presence transitions after deactivation.
