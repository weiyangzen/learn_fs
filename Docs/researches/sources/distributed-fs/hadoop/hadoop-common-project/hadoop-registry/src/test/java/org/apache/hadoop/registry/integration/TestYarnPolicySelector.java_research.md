# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/integration/TestYarnPolicySelector.java

Purpose: tests `SelectByYarnPersistence`, a `RegistryAdminService.NodeSelector` used by purge logic to select service records by YARN ID and persistence policy.

Important APIs and functions: fixture creates a `ServiceRecord` with ID `1` and `APPLICATION` persistence plus a `RegistryPathStatus`. `assertSelected()` invokes `selector.shouldSelect()`. Tests cover nonmatching persistence, matching app persistence, and nonmatching app ID.

Control flow: direct selector invocation avoids ZooKeeper traversal and isolates matching rules.

State and persistence: pure in-memory record and status.

Dependencies and integration: connects YARN persistence constants to registry admin purge selection. This is the unit-level counterpart to purge traversal in `RegistryAdminService`.

Risks and test signals: good signal for exact ID/persistence matching. It does not test wildcard behavior, null record fields, or integration with actual purge recursion.
