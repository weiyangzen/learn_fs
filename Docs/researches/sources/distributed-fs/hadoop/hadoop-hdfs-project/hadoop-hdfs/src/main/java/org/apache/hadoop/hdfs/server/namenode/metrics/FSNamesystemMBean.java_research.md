# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/FSNamesystemMBean.java

## Purpose

`FSNamesystemMBean.java` defines the stable JMX interface for NameNode filesystem state, capacity, block health, DataNode state, snapshots, locking, edit-log sync, tokens, and storage policy satisfier metrics. The source was read as a complete 271-line file.

## Important APIs, Types, and Functions

The interface declares many getters, including `getFSState`, block and capacity totals, file totals, pending reconstruction, low redundancy, scheduled replication, live/dead/stale/decommission/maintenance DataNode counts, snapshot stats, max objects, pending deletion blocks, top user op counts, encryption zone count, lock queue length, sync counts/times, current delegation tokens, pending SPS paths, and reconstruction queue initialization progress. Deprecated names for replication are retained.

## Control Flow

There is no executable flow. Implementers compute values from `FSNamesystem`, block manager, DataNode manager, edit log, snapshot manager, token manager, and other subsystems.

## State and Persistence Behavior

The interface owns no state. Metrics are views over live in-memory NameNode state, much of which is reconstructed from fsimage, edits, and block reports.

## Dependencies and Integration Points

It is part of the NameNode JMX surface and is referenced by EC and replicated block MBeans plus operator tooling. JMX naming conventions are explicitly part of the contract.

## Risks and Edge Cases

Because the interface is stable and externally visible, removing or renaming methods breaks monitoring. Deprecated methods must remain consistent with replacements. JSON-returning methods such as top user counts need stable encoding.

## Test Signals

Tests should validate JMX registration and representative values for capacity, block health, DataNode counts, snapshots, lock queue length, sync totals, tokens, SPS paths, maintenance states, deprecated aliases, and reconstruction queue progress.
