# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestCompositeGroupMapping.java

Purpose: Tests `CompositeGroupsMapping` with multiple configured providers, provider-specific configuration, and combined/non-combined lookup modes.

Important APIs/types/functions: `CompositeGroupsMapping`, `Groups`, `GroupMappingServiceProvider`, `Configurable`, `CommonConfigurationKeys.HADOOP_SECURITY_GROUP_MAPPING`, custom `UserProvider`, `ClusterProvider`, and provider config prefixes.

Control flow: static configuration registers two providers. Provider base classes validate that provider-specific config was rewritten into each provider's `Configuration`. Tests lookup John and hdfs from different providers, then lookup Jack with combined mode true expecting two groups and combined mode false expecting only the first provider's group.

State and persistence: static shared `Configuration` mutated by tests; provider implementations are stateless aside from injected conf.

Dependencies/integration points: Hadoop `Groups` service and composite mapping provider configuration.

Risks: shared static `conf` can leak combined flag between tests if execution order changes; provider lookup order matters; assertions use `assertTrue` rather than exact list equality.

Test signals: verifies provider discovery, provider-specific config propagation, ordered lookup, and combined aggregation behavior.
