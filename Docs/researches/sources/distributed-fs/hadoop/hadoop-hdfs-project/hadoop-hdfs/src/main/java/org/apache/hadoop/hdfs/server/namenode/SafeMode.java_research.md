# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SafeMode.java

## Purpose
`SafeMode` is a private minimal interface for NameNode safe-mode state queries.

## Important APIs, types, and functions
It declares `isInSafeMode()` for any safe-mode state and `isInStartupSafeMode()` for automatic startup safe mode.

## Control flow
There is no implementation. Implementors decide how startup, manual, HA, and block-report-driven states map to the two booleans.

## State and persistence behavior
The interface owns no state. Safe-mode state is runtime NameNode state maintained by the concrete namesystem and related startup/block-report logic.

## Dependencies and integration points
It depends only on classification annotations and is extended by `Namesystem`. Components can depend on safe-mode state without the full `FSNamesystem` type.

## Risks and invariants
Startup safe mode must be distinguished from later safe-mode states. False negatives can allow writes or background work before namespace/block state is ready.

## Test signals
Signals include safe-mode startup tests, HA safe-mode tests, striped-file safe-mode tests, contract safe-mode tests, and administrative safe-mode command tests.
