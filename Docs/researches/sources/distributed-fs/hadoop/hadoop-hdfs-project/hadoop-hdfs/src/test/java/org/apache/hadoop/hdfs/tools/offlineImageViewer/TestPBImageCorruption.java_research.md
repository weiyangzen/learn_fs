# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/TestPBImageCorruption.java

## Purpose
`TestPBImageCorruption` unit-tests `PBImageCorruption` classification and mutation behavior.

## Important APIs, Types, And Functions
The only production type under test is `PBImageCorruption`, with methods `getType`, `getId`, `getNumOfCorruptChildren`, `addMissingChildCorruption`, `addCorruptNodeCorruption`, and `setNumberOfCorruption`.

## Control Flow
One test constructs a corrupt-node instance, adds missing-child corruption, and checks the combined type. Another verifies that constructing an instance with neither corruption kind throws `IllegalArgumentException`. The last test starts from a missing-child instance, validates ID/type/count, adds corrupt-node corruption, updates count, and checks combined type/count.

## State, Persistence, And Dependencies
State is entirely in-memory object fields. There is no filesystem or cluster dependency.

## Integration Points
This supports the larger PB image corruption detector tests by pinning the value-object semantics used in detector output.

## Risks
Coverage is intentionally narrow and does not test CSV rendering or detector traversal. Type strings are exact and user-visible to corruption reports.

## Test Signals
Signals are exact type strings, ID and count getters, count mutation, and constructor validation failure.
