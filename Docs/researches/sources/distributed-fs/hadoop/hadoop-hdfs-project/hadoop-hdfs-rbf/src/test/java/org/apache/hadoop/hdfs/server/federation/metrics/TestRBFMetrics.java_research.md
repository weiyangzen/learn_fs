# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRBFMetrics.java

## Purpose
`TestRBFMetrics` validates the router federation metrics exposed both as JMX beans and as `RBFMetrics` data-source JSON. It covers cluster aggregates, mount table rows, NameNode rows, nameservice rows, router rows, and large capacity values.

## Important APIs, Types, and Functions
The class extends `TestMetricsBase`. It uses JMX bean names `Hadoop:service=Router,name=FederationState` and `Hadoop:service=Router,name=Router`, interfaces `FederationMBean` and `RouterMBean`, `RBFMetrics.getMountTable()`, `getNamenodes()`, `getNameservices()`, `getRouters()`, `MembershipStats`, `MountTable`, `RouterState`, and `StateStoreVersion`.

## Control Flow
JMX and direct data-source tests call common validators. Mount-table validation parses a JSON array and matches entries by source path. NameNode validation iterates JSON objects and compares state, datanode counts, block counts, and addresses to active/standby membership fixtures. Nameservice validation expects one active NameNode per nameservice and compares aggregate capacity and maintenance stats. Router validation matches router JSON by address and checks status, compile/version metadata, timestamps, and state-store version formatting. `testCapacity()` sets each active membership's total and available space to `Long.MAX_VALUE`, refreshes registrations, and verifies BigInteger accessors preserve the sum while long accessors overflow.

## State and Persistence
State comes from `TestMetricsBase` fixtures in the state store and from modified membership stats written back through `refreshNamenodeRegistration()`. Metrics read router caches after explicit refreshes.

## Dependencies and Integration Points
The test integrates JMX lookup, JSON serialization, router metrics aggregation, state-store membership/router/mount records, and capacity overflow handling. It depends on `ListUtils.union()` to search active and standby fixture records.

## Risks and Test Signals
JSON object order is not assumed except where counts are checked. There is a notable assertion mapping `numOfEnteringMaintenanceDataNodes` to stale datanodes in nameservice stats, which documents current behavior and would catch changes. Passing tests signal JMX registration, JSON field completeness, active-membership aggregation, router heartbeat visibility, and overflow-safe capacity reporting.
