<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RefreshSuperUserGroupsConfigurationRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RefreshSuperUserGroupsConfigurationRequestPBImpl.java

## Purpose
Empty PB request for refreshing Router superuser proxy group configuration.

## APIs, Types, and Functions
Implements `PBRecord` over `RefreshSuperUserGroupsConfigurationRequestProto`. Like other empty requests, `getProto()` instantiates a builder before building.

## Control Flow, State, and Persistence
The request has no payload. It is created by admin tooling and routed to the Router generic manager/admin server, where the actual refresh updates in-memory security mapping state rather than State Store records.

## Dependencies and Integration
Integrates with `RouterAdmin.refreshSuperUserGroupsConfiguration()`, `RouterGenericManager`, and `RouterProtocol.proto`. It uses `FederationProtocolPBTranslator` and generated federation protos.

## Risks and Test Signals
Correctness depends on endpoint authorization and configuration reload behavior, not on request fields. Test signals include `TestRouterRefreshSuperUserGroupsConfiguration` and PB translator coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/RefreshSuperUserGroupsConfigurationRequestPBImpl.java -->
