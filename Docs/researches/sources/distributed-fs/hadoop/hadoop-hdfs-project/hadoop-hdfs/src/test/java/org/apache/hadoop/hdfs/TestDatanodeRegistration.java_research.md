# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeRegistration.java

Purpose: tests DataNode registration semantics: avoiding DNS lookups after registration, reporting changed IPC/storage IDs, enforcing software-version/CTime rules, and forced re-registration after block-report or IBR failures.

Important APIs and types: `DatanodeRegistration`, `DatanodeID`, `DatanodeDescriptor`, `DatanodeManager`, `DatanodeStorageInfo`, `NamenodeProtocols`, `NameNodeAdapter`, `DataNodeTestUtils`, `BlockReportOptions`, `IncorrectVersionException`, and mocked `StorageInfo`.

Control flow: DNS test installs a `SecurityManager` counting reverse lookups and verifies refresh/report paths do not add lookups. IPC and storage ID tests restart/register nodes and inspect reports. Version tests mock DN registrations against configured minimum versions and CTimes. `testForcedRegistration` disables heartbeats, toggles `forceRegistration`, triggers heartbeats/block reports/deletion reports/failed IBR, and verifies registration object identity and descriptor state transitions.

State and persistence: starts clusters, registers fake datanodes with NameNode RPC, restarts datanodes, manipulates descriptor registration flags, triggers heartbeats/block reports, and sends deletion reports.

Dependencies and integration: covers NameNode datanode manager, client reports, registration RPCs, heartbeat pipeline, block-report processing, software compatibility checks, and incremental block report failure safety net.

Risks: `SecurityManager` is deprecated and may be unavailable; forced-registration checks rely on internal object identity and timing; mocked registration fields must remain consistent with NameNode validation.

Test signals: unchanged DNS lookup count, report length/IPC port equality, single report entry after storage ID change, expected `IncorrectVersionException` messages, block report processed or skipped as expected, and registration object identity changes only after forced heartbeat.
